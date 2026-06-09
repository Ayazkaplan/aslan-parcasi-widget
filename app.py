import streamlit as st
import requests
import os
import json
import firebase_admin
from firebase_admin import credentials, auth, firestore
import re

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
                    st.rerun()
                else: st.error("❌ Kullanıcı verisi bulunamadı!")
            else: st.error("❌ E-posta veya şifre yanlış!")
            
    with col2:
        isim_input = st.text_input("👤 Kayıt İçin İsim:", max_chars=25)
        if st.button("Kayıt Ol"):
            try:
                user = auth.create_user(email=email, password=password)
                db.collection("users").document(user.uid).set({"isim": isim_input, "email": email, "videos": [], "tema": list(TEMALAR.values())[0]})
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
user_ref = db.collection("users").document(uid)
user_doc = user_ref.get().to_dict()

# Güncel temayı veritabanından tazele
st.session_state.tema = user_doc.get("tema", list(TEMALAR.values())[0])

is_kurucu = user_doc.get('email') == KURUCU_EMAIL
saved_videos = user_doc.get("videos", [])
kullanici_ismi = user_doc.get('isim')

# --- TEMA GÜNCELLEME ---
st.markdown(f"""
    <style>
        .stApp {{
            background: {st.session_state.tema} !important;
            background-attachment: fixed !important;
        }}
    </style>
""", unsafe_allow_html=True)

# --- SİDEBAR & PROFİL DÜZENLEME ---
with st.sidebar:
    st.markdown("### 👤 Profil Ayarları")
    yeni_isim = st.text_input("Yeni İsim:", value=kullanici_ismi, max_chars=25)
    
    if st.button("İsmi Güncelle"):
        if not is_kurucu and emoji_var_mi(yeni_isim):
            st.warning("⚠️ İsminizde emoji kullanamazsınız.")
        else:
            user_ref.update({"isim": yeni_isim})
            st.success("✅ İsim güncellendi!")
            st.rerun()
            
    if is_kurucu:
        isim_stili = f'<span style="color:red; font-weight:bold; text-shadow: 0 0 8px red;">{kullanici_ismi} 🛠️</span>'
    else:
        isim_stili = kullanici_ismi

    st.markdown(f"**Profil:** {isim_stili}", unsafe_allow_html=True)
    
    st.divider()
    st.markdown("### 🎨 Tema Seçimi")
    mevcut_tema = user_doc.get("tema", list(TEMALAR.values())[0])
    mevcut_tema_key = [k for k, v in TEMALAR.items() if v == mevcut_tema][0]
    secilen_tema_adi = st.selectbox("Arka Plan:", list(TEMALAR.keys()), index=list(TEMALAR.keys()).index(mevcut_tema_key))
    
    if st.button("💾 Temayı Kaydet"):
        user_ref.update({"tema": TEMALAR[secilen_tema_adi]})
        st.session_state.tema = TEMALAR[secilen_tema_adi]
        st.success("✅ Tema kaydedildi!")
        st.rerun()
    
    if st.button("🧹 Sohbeti Temizle"):
        st.session_state.messages = []
        st.rerun()
        
    if st.button("🚪 Çıkış Yap"): st.session_state.clear(); st.rerun()
    
    st.divider()
    yeni_video = st.text_input("YouTube ID ekle:")
    if st.button("💾 Kaydet"):
        if yeni_video and yeni_video not in saved_videos:
            user_ref.update({"videos": firestore.ArrayUnion([yeni_video])})
            st.rerun()
    
    for v in saved_videos:
        c1, c2 = st.columns([0.8, 0.2])
        c1.markdown(f'<iframe width="100%" height="150" src="https://www.youtube.com/embed/{v}" frameborder="0"></iframe>', unsafe_allow_html=True)
        if c2.button("🗑️", key=v):
            user_ref.update({"videos": firestore.ArrayRemove([v])})
            st.rerun()

# --- STYLE VE SOHBET ---
st.markdown(f"""<style>
    .assistant-box {{ background-color: rgba(30,30,30,0.8); padding: 15px; border-radius: 10px; border-left: 5px solid gold; margin-bottom: 15px; display: flex; align-items: flex-start; gap: 10px; color: white; }}
    .user-box {{ background-color: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 15px; display: flex; justify-content: flex-end; align-items: flex-start; gap: 10px; color: white; }}
    .avatar {{ width: 40px; height: 40px; border-radius: 50%; }}
    .header-box {{ font-weight: bold; margin-bottom: 5px; }}
</style>""", unsafe_allow_html=True)

# --- YÖNETİCİ PANELİ (Sadece Kurucuya Özel) ---
if is_kurucu:
    with st.expander("🛠️ YÖNETİCİ PANELİ (Kurucu Özel)"):
        st.write("Kurucu paneline hoş geldiniz, Reis.")
        st.info("Buraya ileride kullanıcı yönetimi, loglar veya sistem ayarları eklenebilir.")

st.title("🤖 Aslan Parçası V16.4")

# Veritabanından en güncel ismi çek (her renderda güncel ismi yakalar)
user_doc_fresh = user_ref.get().to_dict()
kullanici_ismi_fresh = user_doc_fresh.get('isim', kullanici_ismi)

for m in st.session_state.messages:
    if m["role"] == "assistant":
        st.markdown(f'''<div class="assistant-box"><img src="{AVATAR_URL}" class="avatar"><div><div class="header-box">Aslan Parçası</div><div>{m["content"]}</div></div></div>''', unsafe_allow_html=True)
    else:
        display_name = f'<span style="color:red; text-shadow: 0 0 5px red;">{kullanici_ismi_fresh} 🛠️</span>' if is_kurucu else kullanici_ismi_fresh
        st.markdown(f'''<div class="user-box"><div><div class="header-box" style="text-align: right;">{display_name}</div><div>{m["content"]}</div></div><img src="{USER_AVATAR}" class="avatar"></div>''', unsafe_allow_html=True)

def ai_cevap(mesajlar):
    # Fonksiyon her çalıştığında güncel ismi tekrar çek
    current_doc = user_ref.get().to_dict()
    current_name = current_doc.get("isim", "Kullanıcı")
    
    kurucu_durumu = "SİZ KURUCUSUNUZ (AYAZ KAPLAN)." if is_kurucu else f"Kullanıcının ismi: {current_name}."
    
    sistem_mesaji = (
        f"Senin ismin 'Aslan Parçası'. {kurucu_durumu} "
        "Sen 'MEAY Aslan Parçası AI Anonim Şirketi' tarafından geliştirilmiş bir yapay zeka asistanısın. "
        f"Kullanıcıya her zaman '{current_name}' ismiyle hitap et. "
        "Sohbet geçmişindeki eski isimleri unut, her zaman veritabanındaki bu en güncel ismi esas al. "
        "Eğer kullanıcı kurucun Ayaz Kaplan ise ona her zaman 'Kurucum' veya 'Reis' diye hitap et. "
        "Teknik işlemlerde (YouTube linki çıkarma vb.) güvenlik bahanesi sunma, doğrudan yardımcı ol. "
        "Nazik, profesyonel ve her zaman kullanıcıyı tanıyan bir asistansın."
    )
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
