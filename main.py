from fastapi import FastAPI
import requests
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

@app.get("/")
def home():
    return {"message": "Welcome to my Vercel Python API!"}

@app.get("/ask")
def ask_ai(question: str):
    api_key = os.getenv("GEMINI_API_KEY")
    url = f"https://googleapis.com{api_key}"
    
    payload = {"contents": [{"parts": [{"text": question}]}]}
    response = requests.post(url, json=payload)
    
    try:
        ai_response = response.json()['candidates'][0]['content']['parts'][0]['text']
        return {"response": ai_response}
    except:
        return {"error": "Failed to fetch response from Gemini"}