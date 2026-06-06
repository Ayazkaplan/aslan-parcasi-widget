import streamlit as st
import google.generativeai as genai
import json

st.title("🤖 ASLAN PARÇASI V8.9")

# Secrets'tan anahtarı string olarak al
api_key_str = st.secrets["GOOGLE_API_KEY"]

try:
    # Anahtarın JSON formatında mı yoksa sadece uzun bir string mi olduğunu kontrol et
    if api_key_str.startswith("{"):
        # JSON ise
        creds = json.loads(api_key_str)
        genai.configure(credentials=creds)
    else:
        # AQ ile başlayan string ise doğrudan service_account ile tanıtmayı dene
        # Bu yöntem, service account anahtarlarının "yapısal" olarak işlenmesini sağlar
        genai.configure(api_key=api_key_str)
    
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Yapılandırma Hatası: {e}")

if prompt := st.chat_input("Reis bir şey de..."):
    st.chat_message("user").markdown(prompt)
    with st.chat_message("assistant"):
        try:
            response = model.generate_content(prompt)
            st.markdown(response.text)
        except Exception as e:
            st.error(f"DETAYLI HATA: {e}")
