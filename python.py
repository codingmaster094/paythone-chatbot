import os
import json
import base64
import urllib.request
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# HTML ફ્રન્ટએન્ડ સાથે કનેક્ટ કરવા માટે CORS સેટિંગ્સ
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ગુગલ જેમીની URL સેટઅપ
API_KEY = os.environ.get("GEMINI_API_KEY")
API_URL = f"https://googleapis.com{API_KEY}"

# યુઝરના પ્રશ્નનું માળખું નક્કી કરવું
class ChatRequest(BaseModel):
    prompt: str
    file_bytes: str = None  # જો યુઝર ઈમેજ કે PDF મોકલે તો (ઓપ્શનલ)
    file_name: str = None

@app.get("/")
def read_root():
    return {"status": "Active", "message": "Welcome to Super AI API on Vercel!"}

@app.post("/api/chat")
def chat_with_ai(req: ChatRequest):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API Key missing on Vercel settings.")
        
    parts_payload = [{"text": req.prompt}]
    
    # જો ફ્રન્ટએન્ડમાંથી ફાઈલનો ડેટા આવે
    if req.file_bytes and req.file_name:
        name_lower = req.file_name.lower()
        if name_lower.endswith(('.png', '.jpg', '.jpeg')):
            mime_type = "image/png" if name_lower.endswith('.png') else "image/jpeg"
        else:
            mime_type = "application/pdf"
            
        parts_payload.insert(0, {
            "inline_data": {
                "mime_type": mime_type,
                "data": req.file_bytes
            }
        })
        
    try:
        json_payload = json.dumps({"contents": [{"parts": parts_payload}]}).encode("utf-8")
        request_obj = urllib.request.Request(
            API_URL, 
            data=json_payload, 
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        with urllib.request.urlopen(request_obj) as response:
            response_data = json.loads(response.read().decode("utf-8"))
            ai_response = response_data['candidates'][0]['content']['parts'][0]['text']
            return {"response": ai_response}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))