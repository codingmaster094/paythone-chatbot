import os  # આ સિસ્ટમ લાઈબ્રેરી જરૂરી છે
from google import genai
import streamlit as st
from dotenv import load_dotenv  # .env ફાઈલ વાંચવા માટે

# .env ફાઈલ લોડ કરો
load_dotenv()

st.set_page_config(page_title="My Chat GPT Clone", page_icon="💬", layout="centered")
st.title("💬 My Personal ChatGPT")

# સાચો પાયથોન નિયમ: પહેલા લોકલ .env ચેક કરશે, જો ત્યાં ન મળે તો Streamlit Cloud ના Secrets ચેક કરશે
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

# ૧. પાયથોન મેમરીમાં ચેટ હિસ્ટ્રી સાચવવા માટેનું સ્ટ્રક્ચર
if "messages" not in st.session_state:
    st.session_state.messages = []

# ૨. જૂની બધી વાતચીતને સ્ક્રીન પર બબલ્સ (Bubbles) તરીકે બતાવવી
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ૩. યુઝર પાસેથી નવો પ્રશ્ન લેવા માટે ચેટ બોક્સ (Chat Input)
if user_prompt := st.chat_input("What is on your mind?"):
    
    # યુઝરનો પ્રશ્ન સ્ક્રીન પર બતાવો અને હિસ્ટ્રીમાં સેવ કરો
    with st.chat_message("user"):
        st.markdown(user_prompt)
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    # AI પાસેથી જવાબ મેળવતી વખતે લોડિંગ પ્રોસેસ બતાવવી
    with st.chat_message("assistant"):
        with st.spinner("Typing..."):
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_prompt,
            )
            st.markdown(response.text)
            
    # AI ના જવાબને પણ હિસ્ટ્રીમાં સેવ કરો જેથી તે ગાયબ ન થાય
    st.session_state.messages.append({"role": "assistant", "content": response.text})