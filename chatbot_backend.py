import re
import requests
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Flask app setup
app = Flask(__name__)
CORS(app, resources={r"/chat": {"origins": ["https://crustdata-chatbot-frontend.vercel.app"]}})
# CORS(app, resources={r"/chat": {"origins": ["http://localhost:3000", "http://192.168.1.72:8000", "https://crustdata-chatbot-frontend.vercel.app"]}})
# LangChain setup
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
llm = ChatOpenAI(openai_api_key=openai_api_key, temperature=0, model="gpt-4")
# conversation_chain = ConversationChain(llm=llm, memory=memory)

SYSTEM_PROMPT = """
You are a helpful assistant for Crustdata's API support.
Use the following references for answers:

1. API Docs: https://www.notion.so/crustdata/Crustdata-Discovery-And-Enrichment-API-c66d5236e8ea40df8af114f6d447ab48
2. Dataset API Detailed Examples: https://www.notion.so/crustdata/Crustdata-Dataset-API-Detailed-Examples-b83bd0f1ec09452bb0c2cac811bba88c

Answer user questions clearly and concisely, and provide example API requests when necessary. Reference specific URLs as appropriate.
"""
template = SYSTEM_PROMPT + "\n\n{chat_history}\nUser: {input}\nAssistant:"
prompt = PromptTemplate(input_variables=["input", "chat_history"], template=template)
conversation_chain = LLMChain(llm=llm, prompt=prompt, memory=memory)

def validate_api_examples(answer_text: str) -> str:
    """
    Look for API request examples in the answer_text.
    If found, try to validate them. If validation fails, remove or modify them.
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

@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == 'OPTIONS':
        return build_cors_preflight_response()
    elif request.method == 'POST':
        user_input = request.json.get("message")
        if not user_input:
            return jsonify({"error": "No message provided"}), 400

        try:
            # LangChain: Generate response and maintain conversation history
            assistant_response = conversation_chain.run(input=user_input)

            # Validate API examples in the response
            validated_answer = validate_api_examples(assistant_response)

            return jsonify({"answer": validated_answer})
        except Exception as e:
            logging.error(f"Error during chat: {e}")
            return jsonify({"error": "An internal server error occurred."}), 500

def build_cors_preflight_response():
    response = jsonify({'status': 'success'})
    response.headers.add("Access-Control-Allow-Origin", "https://crustdata-chatbot-frontend.vercel.app")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
    return response

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True)
