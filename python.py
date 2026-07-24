import io
import os
from google import genai
from google.genai import types
import streamlit as st

st.set_page_config(page_title="Super AI Assistant", page_icon="🤖", layout="centered")
st.title("🤖 My Super AI Assistant")
st.write("Chat, Upload PDFs/Images, or Generate Images seamlessly!")

# ૧. ગુગલ ક્લાયન્ટ સેટઅપ
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

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
                image_prompt = user_prompt.lower().replace("generate image:", "").replace("image:", "").strip()
                
                result = client.models.generate_images(
                    model='imagen-3.0-generate-002',
                    prompt=image_prompt,
                    config=types.GenerateImagesConfig(
                        number_of_images=1,
                        output_mime_type="image/jpeg"
                    )
                )
                
                for generated_image in result.generated_images:
                    image_bytes = generated_image.image.image_bytes
                    st.image(image_bytes)
                    st.session_state.messages.append({"role": "assistant", "content": image_bytes, "type": "image"})
            
            # --- કન્ડિશન B: જો કોઈ ફાઈલ સાચે જ અપલોડ થયેલી હોય ---
            elif uploaded_file:
                file_name = uploaded_file.name.lower()
                file_bytes = uploaded_file.getvalue()
                
                # ૧૦૦% સાચો રસ્તો: જો ફાઈલ ઈમેજ (JPG, PNG) હોય
                if file_name.endswith(('.png', '.jpg', '.jpeg')):
                    # ઈમેજનો સાચો પ્રકાર નક્કી કરવો
                    mime_type = "image/png" if file_name.endswith('.png') else "image/jpeg"
                    
                    # બાઇટ્સ ડેટાને ગુગલ ટાઇપ્સ પાર્ટમાં કન્વર્ટ કરવો
                    image_part = types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
                    
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=[image_part, user_prompt]
                    )
                
                # જો ફાઈલ PDF હોય
                elif file_name.endswith('.pdf'):
                    pdf_part = types.Part.from_bytes(data=file_bytes, mime_type="application/pdf")
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=[pdf_part, user_prompt]
                    )
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text, "type": "text"})
            
            # --- કન્ડિશન C: નોર્મલ ચેટબોટ ---
            else:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=user_prompt,
                )
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text, "type": "text"})