# AI Chat Agent
 
A real-time AI chatbot built with Python Flask, NLP text matching, cosine similarity, and Google Gemini API to deliver intelligent, context-aware chatbot responses.
 
## Features
 
- Real-time chatbot web interface
- Flask-based backend
- NLP text matching using cosine similarity
- Google Gemini API integration for AI-generated responses
- Environment variable support for secure API key management
- Clean and simple project structure
 
## Tech Stack
 
- Python
- Flask
- HTML/CSS
- Google Gemini API
- NLP
- Cosine Similarity
 
## Project Structure
 
```text
AI-Chat-Agent/
├── app.py
├── agent.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
├── LICENSE
├── GEMINI_INTEGRATION.md
└── templates/
    └── index.html
```
 
## Installation
 
Clone the repository:
 
```bash
git clone https://github.com/Muhammad-Ahsan-Khan/AI-Chat-Agent.git
cd AI-Chat-Agent
```
 
Install dependencies:
 
```bash
pip install -r requirements.txt
```
 
Create a `.env` file by copying `.env.example`:
 
```bash
copy .env.example .env
```
 
Add your Gemini API key inside `.env`:
 
```env
GOOGLE_API_KEY=your_api_key_here
```
 
Run the app:
 
```bash
python app.py
```
 
Open the app in your browser:
 
```text
http://127.0.0.1:5000
```
 
## How It Works
 
The chatbot first checks the user’s input using NLP-based similarity matching. If a close match is found, it returns a predefined response. If no strong match is found, it uses the Google Gemini API to generate a context-aware AI response.
 
## Security Note
 
The real `.env` file is not uploaded to GitHub because it may contain private API keys. Use `.env.example` as a template and add your own API key locally.
 
## License
 
This project is licensed under the MIT License.
