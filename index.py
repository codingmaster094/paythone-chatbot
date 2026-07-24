import os
import json
import urllib.request
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# ફ્રન્ટએન્ડ HTML ફાઈલ સાથે કનેક્ટ કરવા માટે CORS પોલિસી ઓપન રાખવી
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# વર્ષ ૨૦૨૬ નું ઓફિશિયલ સ્ટેબલ ગૂગલ જેમીની API URL
API_KEY = os.environ.get("GEMINI_API_KEY")
API_URL = f"https://googleapis.com{API_KEY}"

class ChatRequest(BaseModel):
    prompt: str

@app.get("/")
def read_root():
    return {"status": "Active", "message": "Super AI API is fully running on Vercel!"}

@app.post("/api/chat")
def chat_with_ai(req: ChatRequest):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not set in Vercel Environment Variables.")
        
    # ગૂગલ સર્વર માટેનું એકદમ સાદું અને સ્ટેબલ પેલોડ માળખું
    json_payload = json.dumps({
        "contents": [{
            "parts": [{"text": req.prompt}]
        }]
    }).encode("utf-8")
        
    try:
        request_obj = urllib.request.Request(
            API_URL, 
            data=json_payload, 
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        with urllib.request.urlopen(request_obj) as response:
            response_data = json.loads(response.read().decode("utf-8"))
            
            # રિસ્પોન્સમાંથી ડેટા કાઢવાનો ૧૦૦% સચોટ નિયમ
            ai_response = response_data['candidates'][0]['content']['parts'][0]['text']
            return {"response": ai_response}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
