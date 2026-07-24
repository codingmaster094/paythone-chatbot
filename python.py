import io
import os
import google.generativeai as genai  # સ્ટેબલ ઓફિશિયલ પેકેજ
import streamlit as st
from PIL import Image

st.set_page_config(page_title="Super AI Assistant", page_icon="🤖", layout="centered")
st.title("🤖 My Super AI Assistant")
st.write("Chat, Upload PDFs/Images, or Generate Images seamlessly!")

# ૧. ગુગલ જમીની સેટઅપ (સ્ટેબલ પદ્ધતિ)
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

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
        if message["type"] == "text":
            st.markdown(message["content"])
        elif message["type"] == "image":
            st.image(message["content"])

# ૫. નવો યુઝર ઇનપુટ
if user_prompt := st.chat_input("What's on your mind?"):
    
    # યુઝરનો મેસેજ બતાવો અને હિસ્ટ્રીમાં સેવ કરો
    with st.chat_message("user"):
        st.markdown(user_prompt)
    st.session_state.messages.append({"role": "user", "content": user_prompt, "type": "text"})

    # AI નો સેક્શન ચાલુ કરવો
    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            
            # --- કન્ડિશન A: જો યુઝર ઈમેજ બનાવવાનું (Generate) કહે ---
            if "image:" in user_prompt.lower() or "generate image:" in user_prompt.lower():
                # ઇમેજ જનરેશન માટે આપણે ચેટબોટ મોડલને જ કહીશું
                image_prompt = user_prompt.lower().replace("generate image:", "").replace("image:", "").strip()
                
                # સ્ટેબલ ઇમેજ જનરેશન માટે કોલબોરેશન
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(f"Generate a highly detailed text description or prompt for an image generator based on: {image_prompt}. Keep it in English.")
                st.markdown("💡 *Note: Image generation via new SDK was unstable, so I am answering your text query instead:*")
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text, "type": "text"})
            
            # --- કન્ડિશન B: જો કોઈ ફાઈલ સાચે જ અપલોડ થયેલી હોય ---
            elif uploaded_file:
                file_name = uploaded_file.name.lower()
                
                # જો ફાઈલ ઈમેજ હોય (Pillow ની મદદથી ૧૦૦% સેફ રસ્તો)
                if file_name.endswith(('.png', '.jpg', '.jpeg')):
                    img = Image.open(uploaded_file)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content([user_prompt, img])
                
                # જો ફાઈલ PDF હોય
                elif file_name.endswith('.pdf'):
                    pdf_bytes = uploaded_file.read()
                    pdf_part = {
                        "mime_type": "application/pdf",
                        "data": pdf_bytes
                    }
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content([user_prompt, pdf_part])
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text, "type": "text"})
            
            # --- કન્ડિશન C: નોર્મલ ચેટબોટ ---
            else:
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(user_prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text, "type": "text"})