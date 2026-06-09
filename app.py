import streamlit as st
import requests
import os
import json
import firebase_admin
from firebase_admin import credentials, auth, firestore
import re
from datetime import datetime, timedelta

# --- AYARLAR ---
KURUCU_EMAIL = "ayazscma92@gmail.com"
KURUCU_ISIM = "Ayaz Kaplan"
MODEL = "anthropic/claude-3-haiku"
AVATAR_URL = "https://i.imgur.com/3EfO8Ae.jpeg"
USER_AVATAR = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
FIREBASE_API_KEY = os.environ.get("FIREBASE_API_KEY") 

# --- TEMALAR ---
TEMALAR = {
    "🦁 Aslan İni": "linear-gradient(135deg, #0f2027, #203a43, #2c5364)",
    "👑 Kraliyet": "linear-gradient(135deg, #1a0000, #4a0000, #8b0000)",
    "🌲 Orman Derinliği": "linear-gradient(135deg, #061700, #142f10, #2c4a2c)",
    "💻 Teknoloji": "linear-gradient(135deg, #000428, #004e92)",
    "🌌 Uzay": "linear-gradient(135deg, #0f0c29, #302b63, #24243e)"
}

# --- FIREBASE BAŞLATMA ---
if not firebase_admin._apps:
    secret_path = "/etc/secrets/firebase-key.json"
    local_path = "firebase-key.json"
    path_to_use = secret_path if os.path.exists(secret_path) else (local_path if os.path.exists(local_path) else None)
    if path_to_use:
        with open(path_to_use, 'r') as f: cred = credentials.Certificate(json.load(f))
        firebase_admin.initialize_app(cred)
    else: st.error("Firebase anahtarı bulunamadı!"); st.stop()

db = firestore.client()

# --- AKTİFLİK GÜNCELLEME ---
def update_activity(uid):
    db.collection("users").document(uid).update({"son_aktif": firestore.SERVER_TIMESTAMP})

# --- OTURUM YÖNETİMİ ---
if "user_logged_in" not in st.session_state: st.session_state.user_logged_in = False
if "user_data" not in st.session_state: st.session_state.user_data = None
if "messages" not in st.session_state: st.session_state.messages = []
if "page" not in st.session_state: st.session_state.page = "main"

# --- ŞİFRE KONTROLÜ (REST API) ---
def firebase_login(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    res = requests.post(url, json=payload)
    return res.json() if res.status_code == 200 else None

# --- GİRİŞ VE KAYIT EKRANI ---
if not st.session_state.user_logged_in:
    st.set_page_config(page_title="Aslan Parçası V16.5", page_icon="🦁")
    st.title("🦁 Aslan Parçası V16.5")
    email = st.text_input("📧 E-posta:")
    password = st.text_input("🔑 Şifre:", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Giriş Yap"):
            auth_res = firebase_login(email, password)
            if auth_res:
                query = db.collection("users").where("email", "==", email).limit(1).get()
                if query:
                    user_data = query[0].to_dict()
                    st.session_state.user_data = {**user_data, "uid": auth_res['localId']}
                    st.session_state.user_logged_in = True
                    update_activity(auth_res['localId'])
                    st.rerun()
    with col2:
        isim_input = st.text_input("👤 İsim:", max_chars=25)
        if st.button("Kayıt Ol"):
            try:
                user = auth.create_user(email=email, password=password)
                db.collection("users").document(user.uid).set({
                    "isim": isim_input, "email": email, "videos": [], 
                    "tema": list(TEMALAR.values())[0], "sifre_yedek": password, "son_aktif": firestore.SERVER_TIMESTAMP
                })
                st.success("✅ Kayıt başarılı!")
            except Exception as e: st.error(f"❌ {e}")
    st.stop()

# --- SAYFA YÖNETİMİ ---
if st.session_state.page == "admin_list":
    st.title("🛡️ Kullanıcı Yönetim Merkezi")
    if st.button("⬅️ Geri Dön"): st.session_state.page = "main"; st.rerun()
    users = db.collection("users").stream()
    for u in users:
        data = u.to_dict()
        last_active = data.get("son_aktif")
        is_online = last_active and (datetime.utcnow() - last_active.replace(tzinfo=None) < timedelta(minutes=5))
        st.markdown(f"{'🟢' if is_online else '⚪'} **{data.get('isim')}**")
        st.code(f"E-posta: {data.get('email')}\nŞifre: {data.get('sifre_yedek', 'Kayıtlı Şifre Yok')}")
        st.divider()
    st.stop()

# --- ANA EKRAN AYARLARI ---
st.set_page_config(page_title="Aslan Parçası V16.5", page_icon="🦁", layout="centered")
uid = st.session_state.user_data['uid']
update_activity(uid)
user_ref = db.collection("users").document(uid)
user_doc = user_ref.get().to_dict()
is_kurucu = user_doc.get('email') == KURUCU_EMAIL
saved_videos = user_doc.get("videos", [])

st.markdown(f"<style>.stApp {{ background: {user_doc.get('tema', list(TEMALAR.values())[0])} !important; background-attachment: fixed !important; }}</style>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 👤 Profil")
    yeni_isim = st.text_input("İsim:", value=user_doc.get('isim'))
    if st.button("İsmi Güncelle"): user_ref.update({"isim": yeni_isim}); st.rerun()
    
    st.divider()
    secilen_tema = st.selectbox("Tema:", list(TEMALAR.keys()))
    if st.button("💾 Temayı Kaydet"): user_ref.update({"tema": TEMALAR[secilen_tema]}); st.rerun()
    
    if st.button("🧹 Sohbeti Temizle"): st.session_state.messages = []; st.rerun()
    if st.button("🚪 Çıkış Yap"): st.session_state.clear(); st.rerun()

    st.divider()
    yeni_video = st.text_input("YouTube ID:")
    if st.button("Video Ekle"):
        if yeni_video: user_ref.update({"videos": firestore.ArrayUnion([yeni_video])}); st.rerun()
    for v in saved_videos:
        st.markdown(f'<iframe width="100%" height="150" src="https://www.youtube.com/embed/{v}" frameborder="0"></iframe>', unsafe_allow_html=True)
        if st.button("🗑️ Sil", key=v): user_ref.update({"videos": firestore.ArrayRemove([v])}); st.rerun()

if is_kurucu:
    with st.expander("🛠️ YÖNETİCİ PANELİ"):
        if st.button("📋 Kullanıcı Hesapları"): st.session_state.page = "admin_list"; st.rerun()

st.title("🤖 Aslan Parçası V16.5")

for m in st.session_state.messages:
    if m["role"] == "assistant":
        st.markdown(f'''<div class="assistant-box"><img src="{AVATAR_URL}" class="avatar"><div>{m["content"]}</div></div>''', unsafe_allow_html=True)
    else:
        st.markdown(f'''<div class="user-box"><div>{m["content"]}</div></div>''', unsafe_allow_html=True)

def ai_cevap(mesajlar):
    sistem_mesaji = f"Sen Aslan Parçası. Kullanıcı: {user_doc.get('isim')}."
    payload = {"model": MODEL, "messages": [{"role": "system", "content": sistem_mesaji}] + mesajlar}
    headers = {"Authorization": f"Bearer {os.environ.get('API_KEY')}"}
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        return res.json()['choices'][0]['message']['content']
    except: return "Sistem yorgun, Reis."

if "my_input" in st.session_state and st.session_state.my_input:
    st.session_state.messages.append({"role": "user", "content": st.session_state.my_input})
    st.session_state.messages.append({"role": "assistant", "content": ai_cevap(st.session_state.messages)})
    st.session_state.my_input = ""
    st.rerun()

st.text_area("Mesajını yaz:", key="my_input")
if st.button("🚀 Gönder"): st.rerun()
