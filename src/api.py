"""
Tiny HTTP wrapper around query.diagnose(), so n8n's HTTP Request node can
call our Python logic without n8n needing to know anything about
OpenAI/Pinecone.

Run:
    python api.py
Then POST to http://localhost:5000/diagnose with JSON:
    {"question": "my error text", "image_base64": "optional, base64 png",
     "thread_id": "optional, Slack thread_ts for memory"}

If API_SHARED_SECRET is set in the environment, requests must also
include a matching `X-API-Key` header (checked in n8n's HTTP Request
node under Headers). Left unset, the endpoint is open — fine for local
dev, but set it once this is deployed somewhere public so random
requests can't run up your OpenAI/Pinecone bill.
"""

import base64
import hmac
import tempfile
import os
from flask import Flask, request, jsonify
from query import diagnose

app = Flask(__name__)

API_SHARED_SECRET = os.environ.get("API_SHARED_SECRET")


@app.route("/diagnose", methods=["POST"])
def diagnose_endpoint():
    if API_SHARED_SECRET and not hmac.compare_digest(
        request.headers.get("X-API-Key", ""), API_SHARED_SECRET
    ):
        return jsonify({"error": "unauthorized"}), 401

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
