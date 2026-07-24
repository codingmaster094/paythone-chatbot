import io
import os
import json
import base64
import urllib.request  # પાયથોનની પોતાની ઇન-બિલ્ટ લાઈબ્રેરી (ઇન્સ્ટોલ નથી કરવી પડતી)
import streamlit as st

st.set_page_config(page_title="Super AI Assistant", page_icon="🤖", layout="centered")
st.title("🤖 My Super AI Assistant")
st.write("Chat, Upload PDFs/Images, or Ask anything seamlessly!")

# ૧. ગુગલ API કી મેળવવી
API_KEY = st.secrets["GEMINI_API_KEY"]
API_URL = f"https://googleapis.com{API_KEY}"

# ૨. ડાબી બાજુ સાઇડબારમાં ફાઈલ અપલોડર
st.sidebar.title("📁 Upload Media")
uploaded_file = st.sidebar.file_uploader(
    "Upload a PDF or an Image:", 
    type=["pdf", "png", "jpg", "jpeg"]
)

# ૩. પાયથોન મેમરીમાં ચેટ હિસ્ટ્રી સાચવવી
if "messages" not in st.session_state:
    st.session_state.messages = []

# ૪. જૂની વાતચીત સ્ક્રીન પર બતાવવી
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ૫. નવો યુઝર ઇનપુટ
if user_prompt := st.chat_input("What's on your mind?"):
    
    with st.chat_message("user"):
        st.markdown(user_prompt)
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            
            # ગુગલ API માટેનું પેલોડ માળખું
            parts_payload = [{"text": user_prompt}]
            
            # જો યુઝરે ફાઈલ અપલોડ કરી હોય
            if uploaded_file:
                file_name = uploaded_file.name.lower()
                file_bytes = uploaded_file.getvalue()
                
                # બાઇટ્સ ડેટાને Base64 ટેક્સ્ટમાં બદલવો
                base64_data = base64.b64encode(file_bytes).decode("utf-8")
                
                if file_name.endswith(('.png', '.jpg', '.jpeg')):
                    mime_type = "image/png" if file_name.endswith('.png') else "image/jpeg"
                else:
                    mime_type = "application/pdf"
                
                parts_payload.insert(0, {
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": base64_data
                    }
                })
            
            # urllib નો ઉપયોગ કરીને ડાયરેક્ટ ગુગલ સર્વર સાથે કનેક્શન
            try:
                json_payload = json.dumps({"contents": [{"parts": parts_payload}]}).encode("utf-8")
                
                req = urllib.request.Request(
                    API_URL, 
                    data=json_payload, 
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                
                with urllib.request.urlopen(req) as response:
                    response_data = json.loads(response.read().decode("utf-8"))
                    
                    # રિસ્પોન્સમાંથી સાચો ટેક્સ્ટ કાઢવો
                    ai_response = response_data['candidates'][0]['content']['parts'][0]['text']
                    
                    st.markdown(ai_response)
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                
            except Exception as e:
                st.error("Something went wrong with the API call. Please check your inputs.")