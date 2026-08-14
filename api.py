"""
Tiny HTTP wrapper around query.diagnose(), so n8n's HTTP Request node can
call our Python logic without n8n needing to know anything about
OpenAI/Pinecone.

Run:
    python api.py
Then POST to http://localhost:5000/diagnose with JSON:
    {"question": "my error text", "image_base64": "optional, base64 png",
     "thread_id": "optional, Slack thread_ts for memory"}
"""

import base64
import tempfile
import os
from flask import Flask, request, jsonify
from query import diagnose

app = Flask(__name__)


@app.route("/diagnose", methods=["POST"])
def diagnose_endpoint():
    data = request.get_json(force=True)
    question = data.get("question", "")
    thread_id = data.get("thread_id")
    if not question:
        return jsonify({"error": "missing 'question'"}), 400

    image_path = None
    image_b64 = data.get("image_base64")
    if image_b64:
        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        tmp.write(base64.b64decode(image_b64))
        tmp.close()
        image_path = tmp.name

    try:
        result = diagnose(question, image_path=image_path, thread_id=thread_id)
    finally:
        if image_path and os.path.exists(image_path):
            os.remove(image_path)

    return jsonify(result)


if __name__ == "__main__":
    app.run(port=5000)
