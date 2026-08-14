"""
Standalone test for mcp_fallback.py — verifies the Context7 MCP
connection and tool-calling work before testing it as part of the
full diagnose() flow in query.py.

Run:
    python test_mcp_fallback.py
"""

import asyncio
from dotenv import load_dotenv
from mcp_fallback import resolve_via_mcp

load_dotenv()


async def main():
    # A question that should clearly need current library docs to
    # answer well — good for confirming the tool actually gets used.
    test_question = "What's the current recommended way to import ChatOpenAI in LangChain?"

    print(f"Question: {test_question}\n")
    print("Calling Context7 MCP server...\n")

    result = await resolve_via_mcp(test_question)

    if result:
        print("MCP fallback returned a result:\n")
        print(result)
    else:
        print("MCP fallback returned None — either GPT decided no tool "
              "applied, or the server call failed (check the printed "
              "error above, if any).")


if __name__ == "__main__":
    asyncio.run(main())
