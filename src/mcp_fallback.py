"""
Fallback for when RAG doesn't have a confident answer: connects to the
Context7 MCP server (live, version-specific library documentation) and
lets GPT decide whether/how to use its tools to answer the question.

This is async because the MCP protocol is async-first — kept in its
own file so query.py's main flow can stay simple and synchronous, and
just call into this one function when it needs the fallback.
"""

import os
import json
from openai import OpenAI
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from dotenv import load_dotenv

load_dotenv()

CONTEXT7_URL = "https://mcp.context7.com/mcp"
CHAT_MODEL = "gpt-4o"

openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def _mcp_tools_to_openai_format(mcp_tools):
    """Convert MCP tool definitions into OpenAI function-calling format."""
    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.input_schema
                or {"type": "object", "properties": {}},
            },
        }
        for tool in mcp_tools
    ]


MAX_TOOL_ROUNDS = 4  # resolve-library-id, then get-library-docs, plus headroom


async def resolve_via_mcp(question: str, on_usage=None) -> str | None:
    """
    Ask GPT whether Context7's tools can help answer this question, and
    if so, let it call them — looping so it can chain calls (e.g.
    resolve-library-id, then get-library-docs with the resolved ID)
    instead of stopping after a single tool call. Returns the combined
    tool result text, or None if GPT decides no tool is relevant, or
    no round ever returns real content.

    `on_usage`, if given, is called with each OpenAI response's
    `.usage` object as calls happen, so callers can track token cost
    across the (possibly multi-round) tool-calling loop.
    """
    try:
        async with streamable_http_client(CONTEXT7_URL) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                tools_result = await session.list_tools()
                openai_tools = _mcp_tools_to_openai_format(tools_result.tools)

                messages = [{
                    "role": "user",
                    "content": (
                        "A student asked a technical question that our internal "
                        "docs couldn't confidently answer. If tools here can help "
                        "find the current, correct answer, use them — some tools "
                        "need to be chained (e.g. resolve a library's ID first, "
                        "then fetch its docs using that ID). Keep calling tools "
                        "until you actually have real documentation content, not "
                        "just a list of matching libraries. If nothing here is "
                        "relevant, don't call anything.\n\n"
                        f"Question: {question}"
                    ),
                }]

                collected_results = []

                for round_num in range(MAX_TOOL_ROUNDS):
                    response = openai_client.chat.completions.create(
                        model=CHAT_MODEL,
                        messages=messages,
                        tools=openai_tools,
                    )
                    if on_usage:
                        on_usage(response.usage)
                    message = response.choices[0].message

                    if not message.tool_calls:
                        break  # GPT has what it needs, or nothing applies

                    # Echo the assistant's tool-call request back into the
                    # conversation so GPT can see its own prior calls.
                    messages.append({
                        "role": "assistant",
                        "content": message.content,
                        "tool_calls": [
                            {
                                "id": call.id,
                                "type": "function",
                                "function": {
                                    "name": call.function.name,
                                    "arguments": call.function.arguments,
                                },
                            }
                            for call in message.tool_calls
                        ],
                    })

                    for call in message.tool_calls:
                        args = json.loads(call.function.arguments or "{}")
                        print(f"[MCP round {round_num + 1}] calling {call.function.name}({args})")

                        tool_result = await session.call_tool(call.function.name, args)
                        text_parts = [
                            block.text for block in tool_result.content
                            if hasattr(block, "text")
                        ]
                        tool_text = "\n".join(text_parts)
                        collected_results.append(tool_text)

                        # Feed this tool's result back so GPT can decide
                        # whether to call another tool (e.g. get-library-docs
                        # after resolve-library-id) or stop here.
                        messages.append({
                            "role": "tool",
                            "tool_call_id": call.id,
                            "content": tool_text,
                        })

                return "\n\n---\n\n".join(collected_results) if collected_results else None

    except Exception as e:
        import traceback
        print("\n========== MCP FALLBACK ERROR ==========")
        print(f"Error type: {type(e).__name__}")
        print(f"Error: {e}")
        traceback.print_exc()
        return None


if __name__ == "__main__":
    import asyncio

    question = "How do I create a FastAPI endpoint?"
    result = asyncio.run(resolve_via_mcp(question))

    print("\n========== MCP RESULT ==========")
    print(result)