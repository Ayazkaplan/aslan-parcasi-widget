import streamlit as st
import google.generativeai as genai

# Sırrımızı çekiyoruz
API_KEY = st.secrets["GOOGLE_API_KEY"]

# Kütüphaneyi anahtarınla yapılandırıyoruz
genai.configure(api_key=API_KEY)

# Modeli çağırıyoruz
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
