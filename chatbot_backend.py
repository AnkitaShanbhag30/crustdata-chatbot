from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv  # Import dotenv to load .env variables

# Load .env file to get the OpenAI API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")  # Use the environment variable for the API key

app = Flask(__name__)
CORS(app, resources={r"/chat": {"origins": "http://localhost:3000"}})

SYSTEM_PROMPT =  """
You are a helpful assistant for Crustdata's API support. 
Use the following references for answers:

1. API Docs: https://www.notion.so/crustdata/Crustdata-Discovery-And-Enrichment-API-c66d5236e8ea40df8af114f6d447ab48
2. Dataset API Detailed Examples: https://www.notion.so/crustdata/Crustdata-Dataset-API-Detailed-Examples-b83bd0f1ec09452bb0c2cac811bba88c

Answer user questions clearly and concisely, and provide example API requests when necessary. Reference specific URLs as appropriate.
"""

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    # Create the OpenAI API response
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input},
        ],
        max_tokens=500
    )

    # Access the correct part of the response object
    answer = response.choices[0].message.content.strip()  # Correct way to access the message content
    return jsonify({"answer": answer})


if __name__ == "__main__":
    app.run(debug=True)
