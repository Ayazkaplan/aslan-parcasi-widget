import streamlit as st
import requests
import os
import json
import firebase_admin
from firebase_admin import credentials, auth, firestore

# --- AYARLAR ---
KURUCU_EMAIL = "ayazscma92@gmail.com"
MODEL = "anthropic/claude-3-haiku"
FIREBASE_API_KEY = os.environ.get("FIREBASE_API_KEY") 

# --- FIREBASE BAŞLATMA ---
if not firebase_admin._apps:
    try:
        secret_path = "/etc/secrets/firebase-key.json"
        local_path = "firebase-key.json"
        path_to_use = secret_path if os.path.exists(secret_path) else (local_path if os.path.exists(local_path) else None)
        with open(path_to_use, 'r') as f: 
            cred = credentials.Certificate(json.load(f))
            firebase_admin.initialize_app(cred)
    except: st.error("Firebase Hatası!"); st.stop()

db = firestore.client()

# --- OTURUM YÖNETİMİ ---
if "user_logged_in" not in st.session_state: st.session_state.user_logged_in = False
if "user_data" not in st.session_state: st.session_state.user_data = None
if "messages" not in st.session_state: st.session_state.messages = []

# --- TEMALAR ---
TEMALAR = {
    "Aslan İni": "#1A1A1A", 
    "Orman Derinliği": "#0B2422", 
    "Kraliyet": "#2E0854", 
    "Teknoloji": "#003366", 
    "Uzay": "#000022"
}

# --- GİRİŞ VE KAYIT ---
if not st.session_state.user_logged_in:
    st.set_page_config(page_title="Aslan Parçası V16.4", page_icon="🦁")
    st.title("🦁 Aslan Parçası V16.4")
    email = st.text_input("📧 E-posta:")
    password = st.text_input("🔑 Şifre:", type="password")
    isim_input = st.text_input("👤 Hesap İsmi:")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Giriş Yap"):
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
            res = requests.post(url, json={"email": email, "password": password, "returnSecureToken": True})
            if res.status_code == 200:
                uid = res.json()['localId']
                user_doc = db.collection("users").document(uid).get()
                if user_doc.exists and user_doc.to_dict().get("isim").strip() == isim_input.strip():
                    st.session_state.user_data = {**user_doc.to_dict(), "uid": uid}
                    st.session_state.user_logged_in = True
                    st.rerun()
                else: st.error("❌ İsim veya bilgiler hatalı!")
            else: st.error("❌ Giriş başarısız!")
    with col2:
        if st.button("Kayıt Ol"):
            try:
                user = auth.create_user(email=email, password=password)
                db.collection("users").document(user.uid).set({"isim": isim_input.strip(), "email": email, "videos": []})
                st.success("✅ Kayıt başarılı!")
            except Exception as e: st.error(f"❌ Hata: {e}")
    st.stop()

# --- ANA EKRAN ---
st.set_page_config(page_title="Aslan Parçası V16.4", layout="wide")
uid = st.session_state.user_data['uid']
user_ref = db.collection("users").document(uid)
user_doc = user_ref.get().to_dict()
isim = user_doc.get('isim')
is_kurucu = user_doc.get('email') == KURUCU_EMAIL

# Tema Seçimi
tema = st.sidebar.selectbox("🎨 Tema Seç:", list(TEMALAR.keys()))
st.markdown(f"""<style>.stApp {{ background-color: {TEMALAR[tema]}; color: white; }}</style>""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    renk = "gold" if is_kurucu else "white"
    rozet = " 🛠️" if is_kurucu else ""
    st.markdown(f"### 👤 <span style='color:{renk}'>{isim}{rozet}</span>", unsafe_allow_html=True)
    if st.button("🚪 Çıkış Yap"): st.session_state.clear(); st.rerun()
    st.divider()
    yeni_video = st.text_input("YouTube ID ekle:")
    if st.button("💾 Kaydet"):
        if yeni_video:
            user_ref.update({"videos": firestore.ArrayUnion([yeni_video])}); st.rerun()
    
    for v in user_doc.get("videos", []):
        st.markdown(f'<iframe width="100%" height="150" src="https://www.youtube.com/embed/{v}" frameborder="0"></iframe>', unsafe_allow_html=True)
        if st.button("🗑️ Sil", key=v):
            user_ref.update({"videos": firestore.ArrayRemove([v])}); st.rerun()

# Sohbet
st.title("🤖 Aslan Parçası V16.4")
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.write(m["content"])

def send_message():
    val = st.session_state.my_input
    if val:
        st.session_state.messages.append({"role": "user", "content": val})
        payload = {
            "model": MODEL, 
            "messages": [{"role": "system", "content": f"Sen Aslan Parçası'sın. Kurucun Ayaz Kaplan. Kullanıcın: {isim}. Nazik ve bilgili bir asistansın."}] + st.session_state.messages
        }
        headers = {"Authorization": f"Bearer {os.environ.get('API_KEY')}"}
        try:
            res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
            cevap = res.json()['choices'][0]['message']['content']
        except: cevap = "Sistem yorgun, Reis."
        st.session_state.messages.append({"role": "assistant", "content": cevap})
        st.session_state.my_input = "" 

st.chat_input("Mesajını yaz:", key="my_input", on_submit=send_message)
 
