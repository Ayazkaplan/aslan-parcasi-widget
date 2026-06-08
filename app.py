import streamlit as st
import requests
import os
import json
import firebase_admin
from firebase_admin import credentials, auth, firestore
from datetime import datetime, timedelta

# --- AYARLAR ---
KURUCU_EMAIL = "ayazscma92@gmail.com" # Burayı kendi mailinle güncelle
AVATAR_URL = "https://i.imgur.com/3EfO8Ae.jpeg"
USER_AVATAR = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
DOSYA_ADI = "sarki_id.txt"

# --- STREAMLIT CONFIG ---
st.set_page_config(page_title="Aslan Parçası V16.4", page_icon="🦁")

# --- FIREBASE BAŞLATMA ---
if not firebase_admin._apps:
    secret_path = "/etc/secrets/firebase-key.json"
    local_path = "firebase-key.json"
    path_to_use = secret_path if os.path.exists(secret_path) else (local_path if os.path.exists(local_path) else None)
    
    if path_to_use:
        with open(path_to_use, 'r') as f:
            key_dict = json.load(f)
        cred = credentials.Certificate(key_dict)
        firebase_admin.initialize_app(cred)
    else:
        st.error("Firebase anahtarı bulunamadı!")
        st.stop()

db = firestore.client()

# --- YARDIMCI FONKSİYONLAR ---
def kaydet(dosya, deger): 
    with open(dosya, "w") as f: f.write(deger.strip())

def oku(dosya): 
    return open(dosya, "r").read().strip() if os.path.exists(dosya) else ""

# --- OTURUM YÖNETİMİ ---
if "user_logged_in" not in st.session_state: st.session_state.user_logged_in = False
if "user_data" not in st.session_state: st.session_state.user_data = {"isim": "", "email": ""}
if "messages" not in st.session_state: st.session_state.messages = []
if "is_kurucu" not in st.session_state: st.session_state.is_kurucu = False

# --- GİRİŞ EKRANI ---
if not st.session_state.user_logged_in:
    st.title("🦁 Aslan Parçası V16.4 - Giriş")
    email = st.text_input("📧 E-posta:")
    password = st.text_input("🔑 Şifre:", type="password")
    
    if st.button("Giriş Yap"):
        try:
            user = auth.get_user_by_email(email)
            user_doc = db.collection("users").document(user.uid).get()
            if user_doc.exists:
                st.session_state.user_data = user_doc.to_dict()
                st.session_state.user_logged_in = True
                # Kurucu kontrolü
                if email.lower() == KURUCU_EMAIL.lower():
                    st.session_state.is_kurucu = True
                st.rerun()
        except: st.error("❌ Giriş başarısız.")
    st.stop()

# --- ANA EKRAN ---
with st.sidebar:
    st.markdown("### 👤 Profilim")
    if st.session_state.is_kurucu:
        st.markdown("👑 **STATÜ:** KURUCU")
    st.success(f"**İsim:** {st.session_state.user_data.get('isim')}")
    
    if st.button("🚪 Çıkış Yap"): 
        st.session_state.clear()
        st.rerun()
    
    st.divider()
    tema_secimi = st.selectbox("Arka Plan:", ["Aslan İni", "Kraliyet", "Uzay"])
    theme_map = {"Aslan İni": "#1a1a00", "Kraliyet": "#2c0000", "Uzay": "#1a0033"}
    
    kayitli_id = oku(DOSYA_ADI)
    yeni_id = st.text_input("YouTube ID:", value=kayitli_id)
    if st.button("💾 Kaydet"): kaydet(DOSYA_ADI, yeni_id); st.rerun()
    if kayitli_id: st.markdown(f'<iframe width="100%" height="150" src="https://www.youtube.com/embed/{kayitli_id}" frameborder="0"></iframe>', unsafe_allow_html=True)

# --- STYLE ---
st.markdown(f"""<style>
    .stApp {{ background: linear-gradient(to bottom, {theme_map[tema_secimi]}, #000000); color: white; }} 
    .assistant-box {{ background-color: rgba(30,30,30,0.9); padding: 15px; border-radius: 10px; border-left: 5px solid {'gold' if not st.session_state.is_kurucu else 'red'}; margin-bottom: 15px; }} 
    .user-box {{ background-color: rgba(128,128,128,0.2); padding: 15px; border-radius: 10px; margin-bottom: 15px; text-align: right; }}
</style>""", unsafe_allow_html=True)

st.title("🤖 Aslan Parçası V16.4")

# --- SOHBET ---
for m in st.session_state.messages:
    role_icon = AVATAR_URL if m["role"] == "assistant" else USER_AVATAR
    st.markdown(f"""<div class="{'assistant-box' if m['role']=='assistant' else 'user-box'}">{m['content']}</div>""", unsafe_allow_html=True)

if user_input := st.chat_input("Mesajını yaz..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # AI Çağrısı
    headers = {"Authorization": f"Bearer {os.environ.get('API_KEY')}"}
    payload = {
        "model": "anthropic/claude-3-haiku",
        "messages": [{"role": "system", "content": "Sen Aslan Parçası'sın. Kurucu ayazscma92."}] + st.session_state.messages
    }
    res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    cevap = res.json()['choices'][0]['message']['content']
    
    st.session_state.messages.append({"role": "assistant", "content": cevap})
    st.rerun()
