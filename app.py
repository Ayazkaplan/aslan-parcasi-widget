import streamlit as st
import requests
import os
import json
import firebase_admin
from firebase_admin import credentials, auth, firestore
from datetime import datetime, timedelta

# --- AYARLAR ---
KURUCU_EMAIL = "ayazscma92@gmail.com"  # KENDİ MAİLİNİ BURAYA YAZ!
AVATAR_URL = "https://i.imgur.com/3EfO8Ae.jpeg"
USER_AVATAR = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

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

# --- YARDIMCI AYARLAR ---
API_KEY = os.environ.get("API_KEY")
MODEL = "anthropic/claude-3-haiku"
DOSYA_ADI = "sarki_id.txt"

def kaydet(dosya, deger): 
    with open(dosya, "w") as f: f.write(deger.strip())

def oku(dosya): 
    return open(dosya, "r").read().strip() if os.path.exists(dosya) else ""

# --- OTURUM YÖNETİMİ ---
if "user_logged_in" not in st.session_state: st.session_state.user_logged_in = False
if "user_data" not in st.session_state: st.session_state.user_data = {"isim": "", "email": ""}
if "messages" not in st.session_state: st.session_state.messages = []

# --- GİRİŞ VE KAYIT EKRANI ---
if not st.session_state.user_logged_in:
    st.set_page_config(page_title="Aslan Parçası V16.4", page_icon="🦁")
    st.title("🦁 Aslan Parçası V16.4")
    email = st.text_input("📧 E-posta:")
    password = st.text_input("🔑 Şifre:", type="password")
    isim_input = st.text_input("👤 Profil İsmin:")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Giriş Yap"):
            if email and password:
                try:
                    user = auth.get_user_by_email(email)
                    user_doc = db.collection("users").document(user.uid).get()
                    if user_doc.exists:
                        st.session_state.user_data = user_doc.to_dict()
                        st.session_state.user_logged_in = True
                        st.rerun()
                    else:
                        st.error("❌ Kullanıcı dökümanı bulunamadı.")
                except Exception as e:
                    st.error(f"❌ Giriş başarısız: {e}")
    with col2:
        if st.button("Kayıt Ol"):
            if isim_input and email and password:
                try:
                    user = auth.create_user(email=email, password=password)
                    db.collection("users").document(user.uid).set({"isim": isim_input, "email": email})
                    st.success("✅ Kayıt başarılı!")
                except Exception as e: st.error(f"❌ Hata: {e}")
    st.stop()

# --- KURUCU KONTROLÜ (SAYFA İÇİ) ---
is_kurucu = st.session_state.user_data.get('email') == KURUCU_EMAIL
gorunen_isim = st.session_state.user_data.get('isim')

# --- ANA EKRAN ---
st.set_page_config(page_title="Aslan Parçası V16.4", page_icon="🦁")

with st.sidebar:
    st.markdown("### 👤 Profilim")
    if is_kurucu:
        st.markdown(f"**İsim:** <span style='color:#FF4B4B; font-weight:bold;'>{gorunen_isim} 👑</span>", unsafe_allow_html=True)
        st.info("Sistem Kurucusu")
    else:
        st.success(f"**İsim:** {gorunen_isim}")
    
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

# --- STYLE VE SOHBET ---
st.markdown(f"""<style>
    .stApp {{ background: linear-gradient(to bottom, {theme_map[tema_secimi]}, #000000); color: white; }} 
    .assistant-box {{ background-color: rgba(30,30,30,0.9); padding: 15px; border-radius: 10px; border-left: 5px solid gold; margin-bottom: 15px; }} 
    .user-box {{ background-color: rgba(128,128,128,0.2); padding: 15px; border-radius: 10px; margin-bottom: 15px; text-align: right; }}
    .header-box {{ display: flex; align-items: center; gap: 10px; font-weight: bold; margin-bottom: 5px; }}
    .user-header {{ justify-content: flex-end; }}
    .kurucu-isim {{ color: #FF4B4B !important; font-weight: bold; text-shadow: 0 0 5px red; }}
</style>""", unsafe_allow_html=True)

st.title("🤖 Aslan Parçası V16.4")

# --- MESAJLARI İKONLU YAZDIR ---
for m in st.session_state.messages:
    if m["role"] == "assistant":
        st.markdown(f"""<div class="assistant-box"><div class="header-box"><img src="{AVATAR_URL}" width="30" style="border-radius:50%"> Aslan Parçası</div><div>{m['content']}</div></div>""", unsafe_allow_html=True)
    else:
        isim_style = "kurucu-isim" if is_kurucu else ""
        st.markdown(f"""<div class="user-box"><div class="header-box user-header"><span class="{isim_style}">{gorunen_isim}</span> <img src="{USER_AVATAR}" width="30" style="border-radius:50%"></div><div>{m['content']}</div></div>""", unsafe_allow_html=True)

def ai_cevap(mesajlar):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    payload = {
        "model": MODEL,
        "messages": [{"role": "system", "content": f"Sen Aslan Parçası'sın. Kurucu: {is_kurucu}. Saat: {(datetime.utcnow() + timedelta(hours=3)).strftime('%H:%M')}."}] + mesajlar
    }
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        return res.json()['choices'][0]['message']['content']
    except: return "Sistem yorgun, Reis."

if user_input := st.chat_input("Mesajını yaz..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.spinner("Aslan cevaplıyor..."):
        cevap = ai_cevap(st.session_state.messages[-6:])
        st.session_state.messages.append({"role": "assistant", "content": cevap})
    st.rerun()
 
