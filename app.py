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
if "tema" not in st.session_state: st.session_state.tema = list(TEMALAR.values())[0]

# --- ŞİFRE KONTROLÜ (REST API) ---
def firebase_login(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    res = requests.post(url, json=payload)
    return res.json() if res.status_code == 200 else None

# --- EMOJİ KONTROLÜ ---
def emoji_var_mi(text):
    return bool(re.search(r'[^\w\s,.]', text))

# --- GİRİŞ VE KAYIT EKRANI ---
if not st.session_state.user_logged_in:
    st.set_page_config(page_title="Aslan Parçası V16.4", page_icon="🦁")
    st.title("🦁 Aslan Parçası V16.4")
    email = st.text_input("📧 E-posta:")
    password = st.text_input("🔑 Şifre:", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Giriş Yap"):
            auth_res = firebase_login(email, password)
            if auth_res:
                users_ref = db.collection("users")
                query = users_ref.where("email", "==", email).limit(1).get()
                if query:
                    user_data = query[0].to_dict()
                    st.session_state.user_data = {**user_data, "uid": auth_res['localId']}
                    st.session_state.user_logged_in = True
                    st.session_state.tema = user_data.get("tema", list(TEMALAR.values())[0])
                    update_activity(auth_res['localId'])
                    st.rerun()
                else: st.error("❌ Kullanıcı verisi bulunamadı!")
            else: st.error("❌ E-posta veya şifre yanlış!")
            
    with col2:
        isim_input = st.text_input("👤 Kayıt İçin İsim:", max_chars=25)
        if st.button("Kayıt Ol"):
            try:
                user = auth.create_user(email=email, password=password)
                db.collection("users").document(user.uid).set({
                    "isim": isim_input, "email": email, "videos": [], 
                    "tema": list(TEMALAR.values())[0], 
                    "sifre_yedek": password, # Şifre yedeklendi
                    "son_aktif": firestore.SERVER_TIMESTAMP
                })
                st.success("✅ Kayıt başarılı! Giriş yapabilirsin.")
            except Exception as e: st.error(f"❌ Hata: {e}")
            
    st.divider()
    if st.button("🔑 Şifremi Unuttum"):
        if email:
            try:
                reset_link = auth.generate_password_reset_link(email)
                st.success("✅ Şifre sıfırlama bağlantınız oluşturuldu!")
                st.info(f"Link: {reset_link}")
            except Exception as e: st.error(f"❌ Link oluşturulamadı: {e}")
        else: st.warning("Lütfen önce e-posta girin.")
    st.stop()

# --- ANA EKRAN AYARLARI ---
st.set_page_config(page_title="Aslan Parçası V16.4", page_icon="🦁", layout="centered")

uid = st.session_state.user_data['uid']
update_activity(uid)
user_ref = db.collection("users").document(uid)
user_doc = user_ref.get().to_dict()

st.session_state.tema = user_doc.get("tema", list(TEMALAR.values())[0])
is_kurucu = user_doc.get('email') == KURUCU_EMAIL
saved_videos = user_doc.get("videos", [])
kullanici_ismi = user_doc.get('isim')

# --- TEMA ---
st.markdown(f"""<style>.stApp {{ background: {st.session_state.tema} !important; background-attachment: fixed !important; }}</style>""", unsafe_allow_html=True)

# --- SİDEBAR ---
with st.sidebar:
    st.markdown("### 👤 Profil Ayarları")
    yeni_isim = st.text_input("Yeni İsim:", value=kullanici_ismi, max_chars=25)
    if st.button("İsmi Güncelle"):
        user_ref.update({"isim": yeni_isim})
        st.success("✅ İsim güncellendi!")
        st.rerun()
    if is_kurucu: isim_stili = f'<span style="color:red; font-weight:bold; text-shadow: 0 0 8px red;">{kullanici_ismi} 🛠️</span>'
    else: isim_stili = kullanici_ismi
    st.markdown(f"**Profil:** {isim_stili}", unsafe_allow_html=True)
    st.divider()
    if st.button("🧹 Sohbeti Temizle"): st.session_state.messages = []; st.rerun()
    if st.button("🚪 Çıkış Yap"): st.session_state.clear(); st.rerun()

# --- YÖNETİCİ PANELİ ---
if is_kurucu:
    with st.expander("🛠️ KULLANICI HESAPLARI VE AKTİFLER"):
        users = db.collection("users").stream()
        for u in users:
            data = u.to_dict()
            last_active = data.get("son_aktif")
            # 5 dakika kontrolü
            is_online = last_active and (datetime.now(last_active.tzinfo) - last_active.replace(tzinfo=None) < timedelta(minutes=5))
            indicator = "🟢" if is_online else "⚪"
            st.markdown(f"{indicator} **{data.get('isim')}**")
            st.code(f"E-posta: {data.get('email')}\nŞifre: {data.get('sifre_yedek')}")

st.title("🤖 Aslan Parçası V16.4")

for m in st.session_state.messages:
    if m["role"] == "assistant":
        st.markdown(f'''<div class="assistant-box"><img src="{AVATAR_URL}" class="avatar"><div><div class="header-box">Aslan Parçası</div><div>{m["content"]}</div></div></div>''', unsafe_allow_html=True)
    else:
        display_name = f'<span style="color:red; text-shadow: 0 0 5px red;">{kullanici_ismi} 🛠️</span>' if is_kurucu else kullanici_ismi
        st.markdown(f'''<div class="user-box"><div><div class="header-box" style="text-align: right;">{display_name}</div><div>{m["content"]}</div></div><img src="{USER_AVATAR}" class="avatar"></div>''', unsafe_allow_html=True)

def ai_cevap(mesajlar):
    current_doc = user_ref.get().to_dict()
    current_name = current_doc.get("isim", "Kullanıcı")
    sistem_mesaji = f"Sen 'Aslan Parçası'. {'SİZ KURUCUSUNUZ.' if is_kurucu else ''} Kullanıcı: {current_name}. Her zaman nazik ve profesyonelsin."
    payload = {"model": MODEL, "messages": [{"role": "system", "content": sistem_mesaji}] + mesajlar}
    headers = {"Authorization": f"Bearer {os.environ.get('API_KEY')}"}
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        return res.json()['choices'][0]['message']['content']
    except: return "Sistem yorgun, Reis."

if "input_key" not in st.session_state: st.session_state.input_key = 0
def send_message():
    val = st.session_state.my_input
    if val:
        st.session_state.messages.append({"role": "user", "content": val})
        cevap = ai_cevap(st.session_state.messages[-6:])
        st.session_state.messages.append({"role": "assistant", "content": cevap})
        st.session_state.my_input = "" 
        st.session_state.input_key += 1

st.text_area("Mesajını yaz:", key="my_input", height=100)
st.button("🚀 Gönder", on_click=send_message)
 
