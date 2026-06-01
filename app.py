from flask import Flask, request, jsonify, render_template
from agent import chat_reply
from datetime import datetime, timedelta
import time
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Rate limiting: max 5 requests per minute per IP
request_times = {}
MAX_REQUESTS_PER_MINUTE = 5

def check_rate_limit():
    """Check if user has exceeded rate limit"""
    client_ip = request.remote_addr
    current_time = datetime.now()
    
    if client_ip not in request_times:
        request_times[client_ip] = []
    
    # Remove old requests outside 1 minute window
    request_times[client_ip] = [
        req_time for req_time in request_times[client_ip]
        if current_time - req_time < timedelta(minutes=1)
    ]
    
    if len(request_times[client_ip]) >= MAX_REQUESTS_PER_MINUTE:
        return False, f"Rate limit: Max {MAX_REQUESTS_PER_MINUTE} requests per minute"
    
    request_times[client_ip].append(current_time)
    return True, "OK"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    # Check rate limit
    allowed, message = check_rate_limit()
    if not allowed:
        return jsonify({
            'response': message,
            'confidence': 0.0
        }), 429
    
    data = request.json
    user_input = data.get('message', '')
    final_response, confidence = chat_reply(user_input, conversation_history=None)

    return jsonify({
        'response': final_response,
        'confidence': confidence
    })


if __name__ == '__main__':
    print("Starting Web Server...")
    print("Rate limit: 5 requests per minute")
    app.run(debug=True)