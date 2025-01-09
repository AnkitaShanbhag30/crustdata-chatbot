# Crustdata Chatbot

Crustdata Assignment

## Overview

This project is a chatbot designed to assist users with Crustdata's API support. It provides answers to common questions and offers example API requests.

## Table of Contents

- [Crustdata Chatbot](#crustdata-chatbot)
  - [Overview](#overview)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Running the Application](#running-the-application)
  - [Usage](#usage)

## Features

- Interactive chatbot for Crustdata API support
- Provides answers to frequently asked questions
- Offers example API requests
- User-friendly interface

## Getting Started

### Prerequisites

- Node.js (v14 or later)
- Python (v3.11 or later)
- `pip` (Python package installer)

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/crustdata-chatbot.git
    cd crustdata-chatbot
    ```

2. Set up the backend:
    ```sh
    python3 -m venv chatbot_venv
    source chatbot_venv/bin/activate  # On Windows use `chatbot_venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3. Set up the frontend:
    ```sh
    cd chatbot_frontend
    npm install
    ```

4. Rename `.env.example` to `.env` file in the root directory and add your OpenAI API key:
    ```env
    OPENAI_API_KEY="your-openai-api-key"
    ```

### Running the Application

1. Start the backend server:
    ```sh
    python chatbot_backend.py
    ```

2. Start the frontend development server:
    ```sh
    cd chatbot_frontend
    npm start
    ```

3. Open your browser and navigate to `http://localhost:3000`.

## Usage

- Enter your question in the input box and click "Send".
- The chatbot will respond with an answer based on the Crustdata API documentation.