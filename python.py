import io
from google import genai
from google.genai import types
import streamlit as st

st.set_page_config(page_title="Super AI Assistant", page_icon="🤖", layout="centered")
st.title("🤖 My Super AI Assistant")
st.write("Now you can Chat, Upload PDFs, or Generate Images!")

# ૧. ગુગલ ક્લાયન્ટ સેટઅપ
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# ૨. ડાબી બાજુ સાઇડબારમાં PDF અપલોડ કરવાનું બોક્સ બનાવવું
st.sidebar.title("📁 Upload Documents")
uploaded_file = st.sidebar.file_uploader("Upload a PDF file to analyze:", type=["pdf"])

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
            
            # --- કન્ડિશન A: જો યુઝર ઈમેજ બનાવવાનું કહે ---
            if "image:" in user_prompt.lower() or "generate image:" in user_prompt.lower():
                # પ્રૉમ્પટમાંથી નકામા અક્ષરો કાઢી નાખવા
                image_prompt = user_prompt.lower().replace("generate image:", "").replace("image:", "").strip()
                
                # Imagen 3 મોડલનો ઉપયોગ કરીને ફોટો બનાવવો
                result = client.models.generate_images(
                    model='imagen-3.0-generate-002',
                    prompt=image_prompt,
                    config=types.GenerateImagesConfig(
                        number_of_images=1,
                        output_mime_type="image/jpeg"
                    )
                )
                
                # ફોટો લોડ કરીને સ્ક્રીન પર બતાવવો
                for generated_image in result.generated_images:
                    image_bytes = generated_image.image.image_bytes
                    st.image(image_bytes)
                    # હિસ્ટ્રીમાં સેવ કરવો
                    st.session_state.messages.append({"role": "assistant", "content": image_bytes, "type": "image"})
            
            # --- કન્ડિશન B: જો કોઈ PDF અપલોડ કરેલી હોય ---
            elif uploaded_file is not None:
                # PDF ને રેડ કરી ગુગલ સર્વર પર ફાઈલ ઓબ્જેક્ટ બનાવવો
                pdf_data = uploaded_file.read()
                
                # Gemini ને PDF ડેટા અને યુઝરનો પ્રશ્ન બંને સાથે મોકલવા
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        types.Part.from_bytes(data=pdf_data, mime_type="application/pdf"),
                        user_prompt
                    ]
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