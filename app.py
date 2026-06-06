import streamlit as st
import google.generativeai as genai
import json

# Streamlit'ten anahtarı çek
api_key = st.secrets["GOOGLE_API_KEY"]

# Service Account anahtarları JSON formatındadır veya string olarak doğrudan client'a verilir.
# Eğer API_KEY değişkenin uzun bir JSON string'i ise:
try:
    # Eğer anahtarın JSON formatındaysa burayı kullan
    info = json.loads(api_key)
    genai.configure(credentials=info)
except:
    # Eğer sadece o AQ... ile başlayan string ise bunu kullan
    # Bu yöntem çoğu modern Google Cloud servisinde çalışır
    genai.configure(api_key=api_key)

model = genai.GenerativeModel('gemini-1.5-flash')

st.title("🤖 ASLAN PARÇASI V8.9")

if prompt := st.chat_input("Reis bir şey de..."):
    st.chat_message("user").markdown(prompt)
    with st.chat_message("assistant"):
        try:
            response = model.generate_content(prompt)
            st.markdown(response.text)
        except Exception as e:
            st.error(f"Hata: {e}")
