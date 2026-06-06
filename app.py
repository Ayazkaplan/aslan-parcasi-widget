import streamlit as st
import requests

# Secrets'tan anahtarı çekiyoruz
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except Exception:
    st.error("HATA: GOOGLE_API_KEY bulunamadı! Lütfen Streamlit Secrets ayarlarını kontrol et.")
    st.stop()

st.title("🤖 ASLAN PARÇASI V8.9")

if prompt := st.chat_input("Reis bir şey de..."):
    st.chat_message("user").markdown(prompt)
    
    with st.chat_message("assistant"):
        # Google Gemini API URL
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
        
        headers = {"Content-Type": "application/json"}
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        
        try:
            # API'ye isteği gönderiyoruz
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                answer = result['candidates'][0]['content']['parts'][0]['text']
                st.markdown(answer)
            else:
                st.error(f"Hata Kodu: {response.status_code} - Lütfen anahtarını ve bağlantını kontrol et.")
                st.write(response.json())
        except Exception as e:
            st.error(f"Sistem Hatası: {e}")
