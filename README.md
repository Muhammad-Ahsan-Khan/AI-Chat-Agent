# AI Chat Bot

A simple chatbot that uses text similarity matching and Google Gemini for responses.

## Installation

1. Install dependencies
   ```
   pip install -r requirements.txt
   ```

2. Set up `.env` file
   ```
   copy .env.example .env
   ```
   Add your Gemini API key to `.env`

3. Run the app
   ```
   python app.py
   ```

4. Open http://127.0.0.1:5000 in your browser

## How it Works

The bot checks user input against a knowledge base of patterns. If there's a good match, it returns a preset response. Otherwise, it uses Gemini API for a response.

## Setup

You need a Gemini API key. Get one free at https://aistudio.google.com/app/apikey

## Files

- `agent.py` - Bot logic
- `app.py` - Flask server
- `templates/index.html` - Web interface
- `logs/` - Chat history

## Issues

- Missing API key? I Added it to `.env`
- Missing packages? I ran command`pip install -r requirements.txt`
- API errors? I Checked key is valid