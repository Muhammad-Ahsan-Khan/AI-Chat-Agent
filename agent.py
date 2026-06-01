import math
import json
from datetime import datetime
import random
import re
import os
import time
from dotenv import load_dotenv

load_dotenv()

LOGS_DIR = "logs"
if os.path.exists(LOGS_DIR):
    if not os.path.isdir(LOGS_DIR):
        alt = LOGS_DIR + "_dir"
        i = 1
        while os.path.exists(alt):
            alt = f"{LOGS_DIR}_dir{i}"
            i += 1
        LOGS_DIR = alt
        os.makedirs(LOGS_DIR, exist_ok=True)
else:
    os.makedirs(LOGS_DIR, exist_ok=True)

# Initialize Google Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
client = None
GOOGLE_AVAILABLE = False

if not GOOGLE_API_KEY:
    print("⚠ GOOGLE_API_KEY not found in environment variables")
else:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GOOGLE_API_KEY)
        client = genai.GenerativeModel('gemini-2.5-flash')
        GOOGLE_AVAILABLE = True
        print("✓ Gemini API initialized successfully")
    except ImportError:
        print("⚠ google-generativeai not installed. Install with: pip install google-generativeai")
    except Exception as e:
        print(f"⚠ Failed to initialize Gemini: {str(e)}")


def preprocess_text(text):
    text = re.sub(r'[^\w\s]', '', text)
    text = text.lower()
    text = ' '.join(text.split())
    return text


def text_to_vector(text):
    clean_text = preprocess_text(text)
    words = clean_text.split()
    word_count = {}
    for word in words:
        word_count[word] = word_count.get(word, 0) + 1
    return word_count


def cosine_similarity(vec1, vec2):
    all_words = set(vec1.keys()).union(set(vec2.keys()))
    dot_product = sum(vec1.get(word, 0) * vec2.get(word, 0)
                     for word in all_words)

    magnitude1 = math.sqrt(sum(val ** 2 for val in vec1.values()))
    magnitude2 = math.sqrt(sum(val ** 2 for val in vec2.values()))

    if magnitude1 == 0 or magnitude2 == 0:
        return 0

    return dot_product / (magnitude1 * magnitude2)


def find_best_match(user_input, patterns):
    user_vector = text_to_vector(user_input)

    best_match = None
    highest_similarity = 0
    threshold = 0.5

    for pattern, response in patterns.items():
        pattern_vector = text_to_vector(pattern)
        similarity = cosine_similarity(user_vector, pattern_vector)

        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match = response
    
    if highest_similarity >= threshold:
        return best_match, highest_similarity
    else:
        return None, highest_similarity


def create_knowledge_base():
    patterns = {
        "hello hi hey": "Hi there!",
        "how are you": "I'm doing fine!",
        "weather": "I can't check weather.",
        "who are you": "I'm a chatbot.",
        "help": "Sure, what do you need?",
        "thank you thanks": "You're welcome!",
        "bye goodbye": "Goodbye!",
    }
    return patterns


def get_google_response(user_input, conversation_history=None, max_retries=3):
    """Get response from Google Gemini API with retry logic"""
    if not GOOGLE_API_KEY:
        return "Error: GOOGLE_API_KEY environment variable is not set. Please add it to your .env file.", 0.0
    
    if not GOOGLE_AVAILABLE:
        return "Error: Gemini API not available. Please ensure google-generativeai is installed and GOOGLE_API_KEY is set.", 0.0
    
    if not client:
        return "Error: Gemini client failed to initialize. Please check your API key.", 0.0

    for attempt in range(max_retries):
        try:
            # Build the prompt with conversation context
            context = ""
            if conversation_history:
                for turn in conversation_history[-10:]:  # Last 10 turns for context
                    if turn.get("user"):
                        context += f"User: {turn.get('user')}\n"
                    if turn.get("agent"):
                        context += f"Assistant: {turn.get('agent')}\n"
            
            # Create the full prompt
            if context:
                prompt = f"{context}User: {user_input}\nAssistant:"
            else:
                prompt = user_input
            
            # Call Gemini API
            response = client.generate_content(prompt)
            
            # Extract text from response
            if response and hasattr(response, 'text') and response.text:
                return response.text.strip(), 0.95
            elif response:
                return str(response).strip(), 0.85
            
            return "No response from Gemini API", 0.0
                
        except Exception as e:
            error_str = str(e)
            
            # Check if it's a rate limit error
            if "429" in error_str or "RESOURCEEXHAUSTED" in error_str:
                if attempt < max_retries - 1:
                    # Exponential backoff: 2s, 4s, 8s
                    wait_time = 2 ** (attempt + 1)
                    print(f"Rate limited. Retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    return "API rate limit exceeded. Please try again in a moment.", 0.0
            
            # Check if it's a model not found error
            elif "404" in error_str or "NOTFOUND" in error_str:
                print(f"Model error: {error_str}")
                return "Gemini model not found. Please check configuration.", 0.0
            
            # Other errors
            else:
                error_msg = f"Gemini API error: {error_str[:100]}"
                print(f"DEBUG: {error_msg}")
                return error_msg, 0.0
    
    return "Failed to get response after retries", 0.0


def log_interaction(user_input, response, confidence):
    """Log conversation interactions."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "user_input": user_input,
        "response": response,
        "confidence": confidence
    }

    log_file = os.path.join(LOGS_DIR, "interactions.json")
    try:
        with open(log_file, "a") as f:
            json.dump(log_entry, f)
            f.write("\n")
    except Exception as e:
        print(f"Failed to log interaction: {str(e)}")


def spell_check(word, vocabulary):
    if word in vocabulary:
        return word
    for vocab_word in vocabulary:
        if len(word) == len(vocab_word):
            diff = sum(c1 != c2 for c1, c2 in zip(word, vocab_word))
            if diff == 1:
                return vocab_word
    return word


def main():
    patterns = create_knowledge_base()
    vocabulary = set()
    for pattern in patterns.keys():
        vocabulary.update(pattern.split())

    print("Chat started. Type 'exit' to quit.\n")
    conversation_history = []
    
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        
        user_lower = user_input.lower()
        if user_lower in ["exit", "quit"]:
            print("Bot: Goodbye")
            break
        
        # Try pattern matching first
        words = user_lower.split()
        corrected = [spell_check(w, vocabulary) for w in words]
        corrected_input = " ".join(corrected)
        response, confidence = find_best_match(corrected_input, patterns)       
        
        if response and confidence >= 0.3:
            print(f"Bot: {response}\n")
            log_interaction(user_input, response, confidence)
            conversation_history.append({"user": user_input, "agent": response})
        else:
            # Fall back to Gemini API
            reply, conf = get_google_response(user_input, conversation_history)
            print(f"Bot: {reply}\n")
            log_interaction(user_input, reply, conf)
            conversation_history.append({"user": user_input, "agent": reply})


def chat_reply(user_input, conversation_history=None):
    """Main function called by Flask app"""
    # Try pattern matching first
    response, confidence = find_best_match(user_input, create_knowledge_base())
    if response and confidence >= 0.5:
        return response, confidence
    
    # Fall back to Gemini API
    return get_google_response(user_input, conversation_history)


if __name__ == "__main__":
    main()
