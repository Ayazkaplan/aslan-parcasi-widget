import streamlit as st
import random
from google import genai
from google.genai import types
import datetime

# --- TÜM HAVUZ AKTİF ---
API_KEYS_POOL = [
    "AQ.Ab8RN6JJrDJNHJ5cjDIt6FawWmyLNnf7GY7dNUIIQ-6HjZIUGA",
    "AQ.Ab8RN6LOxcfrob8rhLse9cH2xd5_m577F6fvWhuz51K3N95P_Q",
    "AQ.Ab8RN6LV-UQbwIzCvvIwSaTkfvmbfQEeUIJdy3-MRaw1d0hY_w",
    "AQ.Ab8RN6LbcJNkhqe2kLoX6uVdw6TE1gZmZaeZYbRfmNxGqoBK9Q",
    "AQ.Ab8RN6IvOP4C8jOATC0g7dkRqj0LThxPqfkrOw2PYvskLfJYWg",
    "AQ.Ab8RN6L_YMJUo5c5A6zS3G8a6-mXSnT3k-xTqxN_1WYGTVVEoA",
    "AQ.Ab8RN6JpcRDVlMiQFNq1YLCj9-F3O5WT6XvGJuHDR_jbgI_ZUQ",
    "AQ.Ab8RN6Kj_r0TJPyJRvN43-xl3xeEBq2cbGi94sPa3B1xmP6dkA",
    "AQ.Ab8RN6JX8-sY-NOXJ5o8V98NSrJhkjGEY0Na_PhRN5BXJ4TXLQ",
    "AQ.Ab8RN6LNtWhAsm7JquBxEdY5IeIjqI3j6jO-jHGsSVdRp7SVIA"
]

st.set_page_config(page_title="ASLAN PARÇASI V8.9", layout="centered")
st.title("🤖 ASLAN PARÇASI V8.9")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Reis bir şey de..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Her mesajda rastgele bir anahtar seçerek havuzu kullanıyoruz
            client = genai.Client(api_key=random.choice(API_KEYS_POOL))
            
            config = types.GenerateContentConfig(
                system_instruction=f"Tarih: {datetime.datetime.now()}. Reis'e delikanlıca cevap ver.",
                temperature=0.7
            )
            
            # Model ismini listeden emin olduğumuz 'gemini-1.5-flash' ile koruyoruz
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt,
                config=config
            )
            
            cevap = response.text
            st.markdown(cevap)
            st.session_state.messages.append({"role": "assistant", "content": cevap})
            
        except Exception as e:
            st.error(f"Hata detayı: {e}")
 
