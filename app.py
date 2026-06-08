import streamlit as st
import requests
import os
import json
import firebase_admin
from firebase_admin import credentials, auth, firestore
import re

# --- AYARLAR ---
KURUCU_EMAIL = "ayazscma92@gmail.com"
MODEL = "anthropic/claude-3-haiku"
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

# --- YARDIMCI FONKSİYONLAR ---
def emoji_kontrol(isim):
    return bool(re.search(r'[^\w\s]', isim))

# --- OTURUM YÖNETİMİ ---
if "user_logged_in" not in st.session_state: st.session_state.user_logged_in = False
if "user_data" not in st.session_state: st.session_state.user_data = {"isim": "", "email": "", "uid": ""}
if "messages" not in st.session_state: st.session_state.messages = []
if "saved_videos" not in st.session_state: st.session_state.saved_videos = []

# --- GİRİŞ VE KAYIT EKRANI ---
if not st.session_state.user_logged_in:
    st.set_page_config(page_title="Aslan Parçası V16.4", page_icon="🦁")
    st.title("🦁 Aslan Parçası V16.4")
    email = st.text_input("📧 E-posta:")
    password = st.text_input("🔑 Şifre:", type="password")
    isim_input = st.text_input("👤 Hesap İsmi:")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Giriş Yap"):
            try:
                user = auth.get_user_by_email(email)
                user_doc = db.collection("users").document(user.uid).get()
                if user_doc.exists:
                    # Firestore'daki ismi çekerek güncel tutuyoruz
                    data = user_doc.to_dict()
                    st.session_state.user_data = {**data, "uid": user.uid}
                    st.session_state.user_logged_in = True
                    st.rerun()
            except Exception as e:
                st.error("❌ Giriş Başarısız!")
    with col2:
        if st.button("Kayıt Ol"):
            if len(isim_input) > 30: st.error("İsim çok uzun!"); st.stop()
            try:
                user = auth.create_user(email=email, password=password)
                db.collection("users").document(user.uid).set({"isim": isim_input, "email": email})
                st.success("✅ Kayıt başarılı!")
            except Exception as e: st.error(f"❌ Hata: {e}")
    st.stop()

# --- ANA EKRAN ---
# Her sayfayı yenilediğinde güncel veriyi kullan
is_kurucu = st.session_state.user_data.get('email') == KURUCU_EMAIL
gorunen_isim = st.session_state.user_data.get('isim')
rozet = " 🛠️" if is_kurucu else ""

st.set_page_config(page_title="Aslan Parçası V16.4", page_icon="🦁")

with st.sidebar:
    st.markdown("### 👤 Profilim")
    yeni_isim = st.text_input("İsmini Düzenle:", value=gorunen_isim)
    if st.button("Güncelle"):
        if len(yeni_isim) <= 30:
            if not is_kurucu and emoji_kontrol(yeni_isim):
                st.error("❌ Sadece Kurucu isimde emoji kullanabilir!")
            else:
                db.collection("users").document(st.session_state.user_data['uid']).update({"isim": yeni_isim})
                st.session_state.user_data['isim'] = yeni_isim
                st.rerun()
    
    isim_class = "kurucu-isim" if is_kurucu else ""
    st.markdown(f"**İsim:** <span class='{isim_class}'>{gorunen_isim}{rozet}</span>", unsafe_allow_html=True)
    if is_kurucu: st.info("Sistem Kurucusu")
    
    if st.button("🚪 Çıkış Yap"): st.session_state.clear(); st.rerun()
    
    st.divider()
    tema_secimi = st.selectbox("Arka Plan:", ["Aslan İni", "Kraliyet", "Uzay", "Orman Derinliği", "Teknoloji"])
    theme_map = {"Aslan İni": "#1a1a00", "Kraliyet": "#2c0000", "Uzay": "#1a0033", "Orman Derinliği": "#001a00", "Teknoloji": "#001a1a"}
    
    yeni_video = st.text_input("YouTube ID ekle:")
    if st.button("💾 Kaydet"):
        if yeni_video and yeni_video not in st.session_state.saved_videos:
            st.session_state.saved_videos.append(yeni_video)
    
    for v in list(st.session_state.saved_videos):
        c1, c2 = st.columns([0.8, 0.2])
        c1.markdown(f'<iframe width="100%" height="100" src="https://www.youtube.com/embed/{v}" frameborder="0"></iframe>', unsafe_allow_html=True)
        if c2.button("🗑️", key=v): st.session_state.saved_videos.remove(v); st.rerun()

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

for m in st.session_state.messages:
    if m["role"] == "assistant":
        st.markdown(f"""<div class="assistant-box"><div class="header-box"><img src="{AVATAR_URL}" width="30" style="border-radius:50%"> Aslan Parçası</div><div>{m['content']}</div></div>""", unsafe_allow_html=True)
    else:
        msg_isim_class = "kurucu-isim" if is_kurucu else ""
        st.markdown(f"""<div class="user-box"><div class="header-box user-header"><span class="{msg_isim_class}">{gorunen_isim}{rozet}</span> <img src="{USER_AVATAR}" width="30" style="border-radius:50%"></div><div>{m['content']}</div></div>""", unsafe_allow_html=True)

def ai_cevap(mesajlar):
    sistem_mesaji = f"""
    Sen Aslan Parçası'sın. Kurucun Ayaz Kaplan. Kullanıcın: {st.session_state.user_data.get('isim')}.
    Asla başka bir isimle hitap etme.
    
    İşte çalışma ilkelerin:
    1. Dinamik ve Kişiselleştirilmiş Yardım: Bilgiyi kişiselleştirirken süreci görünmez kıl, 'verilerine göre' gibi ifadeler kullanma.
    2. Düzen ve Okunabilirlik: Başlıklar, kalın harfler ve listeler kullanarak bilgiyi bir bakışta anlaşılır yap.
    3. Güvenlik ve Etik: Zararlı, etik dışı veya hassas kişisel veri taleplerini doğrudan reddet.
    4. İş Birliği Tonu: Nazik, katılımcı ve hevesli bir yapay zeka iş arkadaşı ol. Net ve doğrudan (candor) bilgi ver.
    5. Tamamlayıcılık ve Aksiyon: Sorulara eksiksiz, doğrudan ve profesyonel çözümler sun.
    """
    
    payload = {"model": MODEL, "messages": [{"role": "system", "content": sistem_mesaji}] + mesajlar}
    headers = {"Authorization": f"Bearer {os.environ.get('API_KEY')}"}
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        return res.json()['choices'][0]['message']['content']
    except: return "Sistem yorgun, Reis."

if user_input := st.chat_input("Mesajını yaz..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    cevap = ai_cevap(st.session_state.messages[-6:])
    st.session_state.messages.append({"role": "assistant", "content": cevap})
    st.rerun()
