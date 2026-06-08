import streamlit as st
import requests
import os
import json
import firebase_admin
from firebase_admin import credentials, auth, firestore

# --- SAYFA AYARI (TEK SEFER) ---
st.set_page_config(page_title="Aslan Parçası V16.4", page_icon="🦁", layout="centered")

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
    except Exception as e: 
        st.error(f"Firebase başlatılamadı: {e}"); st.stop()

db = firestore.client()

# --- OTURUM YÖNETİMİ ---
if "user_logged_in" not in st.session_state: st.session_state.user_logged_in = False
if "user_data" not in st.session_state: st.session_state.user_data = None
if "messages" not in st.session_state: st.session_state.messages = []

# --- ŞİFRE KONTROLÜ (REST API) ---
def firebase_login(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    res = requests.post(url, json=payload)
    if res.status_code == 200:
        return res.json()
    else:
        # HATA AYIKLAMA: Firebase'in gerçek hata mesajını döndür
        return {"error": res.json().get('error', {}).get('message', 'Bilinmeyen Hata')}

# --- GİRİŞ VE KAYIT EKRANI ---
if not st.session_state.user_logged_in:
    st.title("🦁 Aslan Parçası V16.4")
    email = st.text_input("📧 E-posta:")
    password = st.text_input("🔑 Şifre:", type="password")
    isim_input = st.text_input("👤 Hesap İsmi:")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Giriş Yap"):
            auth_res = firebase_login(email, password)
            if auth_res and 'localId' in auth_res:
                user_doc = db.collection("users").document(auth_res['localId']).get()
                if user_doc.exists:
                    data = user_doc.to_dict()
                    # İsim kontrolünü gevşetelim, bazen boşluk karakteri vs takılabilir
                    if data.get("isim").strip() == isim_input.strip():
                        st.session_state.user_data = {**data, "uid": auth_res['localId']}
                        st.session_state.user_logged_in = True
                        st.rerun()
                    else: st.error("❌ Kayıtlı isim ile girdiğin isim eşleşmiyor!")
                else: st.error("❌ Kullanıcı hesabı bulunamadı!")
            else: st.error(f"❌ Giriş hatası: {auth_res.get('error') if auth_res else 'API Hatası'}")
            
    with col2:
        if st.button("Kayıt Ol"):
            try:
                user = auth.create_user(email=email, password=password)
                db.collection("users").document(user.uid).set({"isim": isim_input.strip(), "email": email, "videos": []})
                st.success("✅ Kayıt başarılı! Sayfayı yenileyip giriş yap.")
            except Exception as e: st.error(f"❌ Kayıt hatası: {e}")
    st.stop()

# --- ANA EKRAN ---
# (Buradaki kod aynı, değişmedi)
uid = st.session_state.user_data['uid']
user_ref = db.collection("users").document(uid)
user_doc = user_ref.get().to_dict()
gorunen_isim = user_doc.get('isim', 'Kullanıcı')
saved_videos = user_doc.get("videos", [])

with st.sidebar:
    st.markdown(f"**👤 Profil:** {gorunen_isim}")
    if st.button("🚪 Çıkış Yap"): st.session_state.clear(); st.rerun()
    st.divider()
    yeni_video = st.text_input("YouTube ID ekle:")
    if st.button("💾 Kaydet"):
        if yeni_video and yeni_video not in saved_videos:
            user_ref.update({"videos": firestore.ArrayUnion([yeni_video])}); st.rerun()
    for v in saved_videos:
        c1, c2 = st.columns([0.8, 0.2])
        c1.markdown(f'<iframe width="100%" height="150" src="https://www.youtube.com/embed/{v}" frameborder="0"></iframe>', unsafe_allow_html=True)
        if c2.button("🗑️", key=v):
            user_ref.update({"videos": firestore.ArrayRemove([v])}); st.rerun()

st.title("🤖 Aslan Parçası V16.4")
for m in st.session_state.messages:
    role = "assistant" if m["role"] == "assistant" else "user"
    with st.chat_message(role): st.write(m["content"])

def send_message():
    if st.session_state.my_input:
        st.session_state.messages.append({"role": "user", "content": st.session_state.my_input})
        # AI Yanıtı
        payload = {"model": MODEL, "messages": [{"role": "system", "content": "Nazik bir asistansın."}] + st.session_state.messages}
        headers = {"Authorization": f"Bearer {os.environ.get('API_KEY')}"}
        try:
            res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
            cevap = res.json()['choices'][0]['message']['content']
        except: cevap = "Sistem yorgun, Reis."
        st.session_state.messages.append({"role": "assistant", "content": cevap})
        st.session_state.my_input = "" 

st.chat_input("Mesajını yaz:", key="my_input", on_submit=send_message)
