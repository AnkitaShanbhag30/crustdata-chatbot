import re
import requests
import json
import logging  # For error logs
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv

# Load .env file to get the OpenAI API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app, resources={r"/chat": {"origins": ["https://crustdata-chatbot-frontend-oxzkpajbw-ankita-shanbhags-projects.vercel.app", "https://crustdata-chatbot-frontend.vercel.app"]}})

# In-memory conversation history (single user demo).
# In production, store per-user data in a DB or session.
conversation_history = []

SYSTEM_PROMPT = """
You are a helpful assistant for Crustdata's API support. 
Use the following references for answers:

1. API Docs: https://www.notion.so/crustdata/Crustdata-Discovery-And-Enrichment-API-c66d5236e8ea40df8af114f6d447ab48
2. Dataset API Detailed Examples: https://www.notion.so/crustdata/Crustdata-Dataset-API-Detailed-Examples-b83bd0f1ec09452bb0c2cac811bba88c

Answer user questions clearly and concisely, and provide example API requests when necessary. Reference specific URLs as appropriate.
"""

def validate_api_examples(answer_text: str) -> str:
    """
    Look for API request examples in the answer_text.
    If found, try to validate them. If validation fails, remove or modify them.
    For simplicity, this example just searches for lines containing 'GET', 'POST', or 'curl'.
    """
    lines = answer_text.splitlines()
    validated_lines = []

    for line in lines:
        if "GET" in line or "POST" in line or "curl" in line:
            url_match = re.search(r"(https?://[^\s]+)", line)
            if url_match:
                test_url = url_match.group(1)
                try:
                    resp = requests.head(test_url, timeout=5)
                    if resp.ok:
                        validated_lines.append(line)
                    else:
                        validated_lines.append(f"# Removed invalid API request: {line}")
                except Exception as e:
                    validated_lines.append(f"# Removed invalid API request due to error: {line}")
            else:
                validated_lines.append(line)
        else:
            validated_lines.append(line)

    return "\n".join(validated_lines)

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    # 1) Append the user's message to the in-memory conversation
    conversation_history.append({"role": "user", "content": user_input})

    # 2) Construct the full message list: system prompt + entire conversation history
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history

    try:
        # 3) Call the OpenAI ChatCompletion API with the entire conversation
        response = openai.chat.completions.create(
            model="gpt-4",  # or "gpt-3.5-turbo"
            messages=messages,
            max_tokens=500
        )
    except openai.error.OpenAIError as e:
        logging.error(f"OpenAI error occurred: {e}")
        return jsonify({"error": "OpenAI API Error occurred. Check server logs for details."}), 500

    # 4) Extract the assistant's answer
    raw_answer = response.choices[0].message.content.strip()

    # 5) (Optional) Validate any API-call examples
    validated_answer = validate_api_examples(raw_answer)

    # 6) Append the assistant's reply to the conversation history
    conversation_history.append({"role": "assistant", "content": validated_answer})

    # Return the final answer to the user
    return jsonify({"answer": validated_answer})

if __name__ == "__main__":
    app.run(debug=True)
