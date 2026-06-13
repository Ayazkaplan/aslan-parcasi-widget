import streamlit as st
import streamlit.components.v1 as components
import requests
import os
import json
import firebase_admin
from firebase_admin import credentials, auth, firestore
import re
from datetime import datetime, timezone, timedelta
import time
import unicodedata
import tempfile

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Aslan Parçası V16.4", page_icon="🦁", layout="centered")

# --- Google Translate Engelleme ---
st.markdown("""
<meta name="google" content="notranslate">
<meta http-equiv="Content-Language" content="tr">
<script>
  // Google Translate'i tamamen devre dışı bırak
  Object.defineProperty(window, 'google', { value: undefined, writable: false });
  document.documentElement.setAttribute('translate', 'no');
  document.documentElement.setAttribute('class', 'notranslate');
  // MutationObserver ile dinamik translate sınıflarını temizle
  var observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
      if (document.documentElement.classList.contains('translated-ltr') ||
          document.documentElement.classList.contains('translated-rtl')) {
        document.documentElement.classList.remove('translated-ltr', 'translated-rtl');
      }
    });
  });
  observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
</script>
<style>
  .goog-te-banner-frame, .goog-te-menu-value, #goog-gt-tt,
  .goog-tooltip, .goog-tooltip:hover, .goog-te-balloon-frame,
  div#goog-gt-tt, .VIpgJd-ZVi9od-ORHb-OEVmcd { display: none !important; }
  body { top: 0px !important; }
  .notranslate { translate: no; }
</style>
""", unsafe_allow_html=True)

# --- AYARLAR ---
KURUCU_EMAIL = "ayazscma92@gmail.com"
KURUCU_ISIM = "Ayaz Kaplan"
MODEL = "anthropic/claude-3-haiku"
AVATAR_URL = "https://i.imgur.com/3EfO8Ae.jpeg"
USER_AVATAR = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

FIREBASE_API_KEY = os.environ.get("FIREBASE_API_KEY")
OPENROUTER_API_KEY = os.environ.get("API_KEY")

if not FIREBASE_API_KEY:
    st.error("❌ Firebase API anahtarı (FIREBASE_API_KEY) ortam değişkenlerinde bulunamadı!")
    st.stop()

if not OPENROUTER_API_KEY:
    st.error("❌ OpenRouter API anahtarı (API_KEY) ortam değişkenlerinde bulunamadı!")
    st.stop()

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
        with open(path_to_use, 'r') as f:
            cred = credentials.Certificate(json.load(f))
            firebase_admin.initialize_app(cred)
    else:
        st.error("Firebase anahtarı bulunamadı!")
        st.stop()

db = firestore.client()

# --- YARDIMCI FONKSİYONLAR ---
def normalize_text(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    return re.sub(r'[^a-zA-Z0-9]', '', text.lower())

def kufur_var_mi(text):
    """
    Sadece gerçekten küfür olan kelimeleri filtreler.
    Kısa ve belirsiz kelimeler (rab, kus, kos, pic, ayri vb.) listeden çıkarıldı.
    """
    clean_text = normalize_text(text)
    # Kesin küfür olan, yanlış pozitif vermeyen kelimeler
    ban_list = [
        "amk", "orospu", "yavsak", "yavsaklik", "serefsiz",
        "fuck", "bitch", "asshole", "bastard", "cunt",
        "motherfucker", "whore", "slut",
        "scheisse", "arschloch", "schlampe", "wichser", "hurensohn", "fotze",
        "sharmouta", "sharmuta", "sharmout",
        "puta", "puto", "cabron", "maricon", "merde"
    ]
    for word in ban_list:
        if word in clean_text:
            return True
    return False

def emoji_var_mi(text):
    emoji_pattern = re.compile("[" "\U00010000-\U0010ffff" "\u2600-\u27bf" "]+", flags=re.UNICODE)
    return bool(emoji_pattern.search(text))

def get_video_iframe(video_id):
    return f'<iframe width="100%" height="200" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe>'

def get_styled_user_name(u_name, u_color, u_glow, u_tag, u_rozet):
    color_val = u_color if u_color else "#FFFFFF"
    glow_css = f"text-shadow: 0 0 10px {color_val}, 0 0 20px {color_val}, 0 0 30px {color_val};" if u_glow else ""
    tag_html = ""
    if u_tag:
        # Tag da aynı renk ve parlaklık efektiyle gösterilir
        tag_html = f'<span style="font-size:0.8em; color:{color_val}; {glow_css} margin-right:5px;">[{u_tag}]</span>'
    isim_html = f'<span style="color:{color_val}; {glow_css} font-weight:bold;">{u_name}</span>'
    rozet_html = ""
    if u_rozet:
        # Rozet de aynı parlaklık efektiyle gösterilir
        rozet_html = f'<span style="margin-left:5px; filter: drop-shadow(0 0 6px {color_val});">{u_rozet}</span>' if u_glow else f'<span style="margin-left:5px;">{u_rozet}</span>'
    return f"{tag_html}{isim_html}{rozet_html}"

def get_tr_time():
    """Türkiye saatini (UTC+3) döndürür."""
    tr_tz = timezone(timedelta(hours=3))
    return datetime.now(tr_tz)

def firebase_login(email, password):
    try:
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
        payload = {"email": email, "password": password, "returnSecureToken": True}
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"[FIREBASE LOGIN HATASI] {e}")
        return None

def sifre_kaydet_firebase(uid, yeni_sifre):
    """
    Şifre sıfırlama sonrası yeni şifreyi Firebase'e displayName alanına yazar.
    Firebase Auth şifreleri hash'ler, biz display_name'i workaround olarak kullanıyoruz.
    """
    try:
        auth.update_user(uid, display_name=f"__pwd__{yeni_sifre}")
        db.collection("users").document(uid).update({"gizli_bilgi": yeni_sifre})
    except Exception as e:
        print(f"[ŞİFRE KAYIT HATASI] {e}")

# --- LOCAL STORAGE COMPONENT ---
COMP_DIR = os.path.join(tempfile.gettempdir(), "aslan_ls_component")
os.makedirs(COMP_DIR, exist_ok=True)
HTML_PATH = os.path.join(COMP_DIR, "index.html")

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write("""
    <!DOCTYPE html>
    <html translate="no" class="notranslate">
    <head>
    <meta name="google" content="notranslate">
    <script>
      function sendMessage(type, data) {
        window.parent.postMessage(Object.assign({isStreamlitMessage: true, type: type}, data), "*");
      }
      window.onload = function() {
          sendMessage("streamlit:componentReady", {apiVersion: 1});
          sendMessage("streamlit:setFrameHeight", {height: 0});
          var val = localStorage.getItem("aslan_passkey");
          sendMessage("streamlit:setComponentValue", {value: val ? val : "NOT_FOUND"});
      };
    </script></head>
    <body></body>
    </html>
    """)

get_local_storage = components.declare_component("get_local_storage", path=COMP_DIR)

# --- STATE YÖNETİMİ ---
if "user_logged_in" not in st.session_state: st.session_state.user_logged_in = False
if "user_data" not in st.session_state: st.session_state.user_data = None
if "messages" not in st.session_state: st.session_state.messages = []
if "tema" not in st.session_state: st.session_state.tema = list(TEMALAR.values())[0]
if "valid_users_cache" not in st.session_state: st.session_state.valid_users_cache = None
if "current_page" not in st.session_state: st.session_state.current_page = "chat"

def trigger_invalid_session():
    for key in list(st.session_state.keys()):
        if key != "tema":
            del st.session_state[key]
    st.session_state.trigger_clear_token = True
    st.rerun()

def logout_user():
    trigger_invalid_session()

# --- SESSİZ ARKA PLAN GÖREVLİLERİ ---
if st.session_state.get("trigger_clear_token", False):
    components.html("<script>localStorage.removeItem('aslan_passkey');</script>", height=0, width=0)
    st.markdown("<h3 style='text-align:center; color:white; margin-top:20vh;'>Çıkış yapılıyor...</h3>", unsafe_allow_html=True)
    st.session_state.trigger_clear_token = False
    time.sleep(0.5)
    st.rerun()

if st.session_state.get("trigger_save_token"):
    uid = st.session_state.trigger_save_token
    components.html(f"<script>localStorage.setItem('aslan_passkey', '{uid}');</script>", height=0, width=0)
    st.session_state.trigger_save_token = None

# --- ADIM 1: TOKEN OKUMA ---
if not st.session_state.user_logged_in and not st.session_state.get("trigger_clear_token", False):

    token = get_local_storage(key="token_reader_comp")

    if token is None:
        st.markdown("""
        <div style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background-color: #0f2027; display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 999999; opacity: 0; animation: fadeIn 0.3s ease-in forwards 0.2s;">
            <div style="width: 60px; height: 60px; border: 5px solid rgba(255, 255, 255, 0.1); border-top: 5px solid #f39c12; border-radius: 50%; animation: spin 0.8s linear infinite;"></div>
            <h3 style="color: white; font-family: sans-serif; margin-top: 25px;">Geçiş Anahtarı Doğrulanıyor...</h3>
        </div>
        <style>
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        @keyframes fadeIn { 100% { opacity: 1; } }
        </style>
        """, unsafe_allow_html=True)
        st.stop()

    elif token != "NOT_FOUND":
        try:
            user_ref_temp = db.collection("users").document(token)
            user_snap = user_ref_temp.get()
            if user_snap.exists:
                user_data = user_snap.to_dict()
                user_durum = user_data.get("durum", "Aktif")
                ban_bitis = user_data.get("ban_bitis_zamani")

                if hasattr(ban_bitis, "to_datetime"):
                    ban_bitis = ban_bitis.to_datetime()

                is_banned = False
                if user_durum == "Pasif":
                    if ban_bitis:
                        if ban_bitis.tzinfo is None: ban_bitis = ban_bitis.replace(tzinfo=timezone.utc)
                        if datetime.now(timezone.utc) < ban_bitis: is_banned = True
                    else:
                        is_banned = True

                if not is_banned:
                    user_ref_temp.update({"son_gorulme_zamani": firestore.SERVER_TIMESTAMP})
                    st.session_state.user_data = {**user_data, "uid": token}
                    st.session_state.user_logged_in = True
                    st.session_state.tema = user_data.get("tema", list(TEMALAR.values())[0])

                    sohbet_list = user_data.get("sohbet_gecmisi", [])
                    if isinstance(sohbet_list, list):
                        active_messages = []
                        last_separator_idx = -1
                        for idx, msg in enumerate(sohbet_list):
                            if msg.get("role") == "separator": last_separator_idx = idx
                        if last_separator_idx != -1: active_messages = sohbet_list[last_separator_idx + 1:]
                        else: active_messages = [m for m in sohbet_list if m.get("role") in ["user", "assistant"]]
                        st.session_state.messages = active_messages
                    else:
                        st.session_state.messages = []
                    st.rerun()
                else:
                    trigger_invalid_session()
            else:
                trigger_invalid_session()
        except Exception:
            trigger_invalid_session()

# --- GİRİŞ VE KAYIT EKRANI ---
if not st.session_state.user_logged_in:

    st.title("🦁 Aslan Parçası V16.4")

    if "ban_error_on_logout" in st.session_state:
        st.error(st.session_state.ban_error_on_logout)

    email = st.text_input("📧 E-posta (Sisteme Kayıtlı):")
    password = st.text_input("🔑 Şifre:", type="password")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Giriş Yap", use_container_width=True):
            st.session_state.pop("ban_error_on_logout", None)
            clean_email = email.strip().lower()
            auth_res = firebase_login(clean_email, password)
            if auth_res:
                users_ref = db.collection("users")
                query = users_ref.where("email", "==", clean_email).limit(1).get()
                if query:
                    user_data = query[0].to_dict()
                    user_durum = user_data.get("durum", "Aktif")
                    ban_bitis = user_data.get("ban_bitis_zamani")

                    if hasattr(ban_bitis, "to_datetime"):
                        ban_bitis = ban_bitis.to_datetime()

                    is_banned = False
                    if user_durum == "Pasif":
                        if ban_bitis:
                            if ban_bitis.tzinfo is None:
                                ban_bitis = ban_bitis.replace(tzinfo=timezone.utc)
                            now = datetime.now(timezone.utc)
                            if now < ban_bitis:
                                is_banned = True
                                kalan_sure = ban_bitis - now
                                kalan_dakika = int(kalan_sure.total_seconds() / 60)
                                if kalan_dakika < 1:
                                    st.error(f"❌ Hesabınız pasifleştirilmiştir. Kalan süre: {int(kalan_sure.total_seconds())} saniye")
                                else:
                                    st.error(f"❌ Hesabınız pasifleştirilmiştir. Kalan süre: {kalan_dakika} dakika")
                            else:
                                db.collection("users").document(query[0].id).update({"durum": "Aktif", "ban_bitis_zamani": None})
                                db.collection("banlanan_emails").document(clean_email).delete()
                                user_data["durum"] = "Aktif"
                                user_data["ban_bitis_zamani"] = None
                        else:
                            is_banned = True
                            st.error("❌ Hesabınız pasifleştirilmiştir. Giriş yapamazsınız!")

                    if not is_banned:
                        uid_logged = auth_res['localId']
                        db.collection("users").document(query[0].id).update({"son_gorulme_zamani": firestore.SERVER_TIMESTAMP})
                        st.session_state.user_data = {**user_data, "uid": uid_logged}
                        st.session_state.user_logged_in = True
                        st.session_state.tema = user_data.get("tema", list(TEMALAR.values())[0])
                        st.session_state.trigger_save_token = uid_logged
                        st.rerun()
                else:
                    st.error("❌ Kullanıcı verisi bulunamadı!")
            else:
                st.error("❌ E-posta veya şifre yanlış!")

    with col2:
        isim_input = st.text_input("👤 Kayıt İçin İsim:", max_chars=25)
        if st.button("Kayıt Ol", use_container_width=True):
            st.session_state.pop("ban_error_on_logout", None)
            try:
                clean_email = email.strip().lower()
                temiz_isim = isim_input.strip()

                # --- DÜZELTME 11: İsim benzersizlik kontrolü ---
                if temiz_isim:
                    isim_check = db.collection("users").where("isim", "==", temiz_isim).limit(1).get()
                    if isim_check:
                        st.error("❌ Bu kullanıcı adı zaten alınmış. Lütfen farklı bir isim seçin!")
                        st.stop()

                ban_doc = db.collection("banlanan_emails").document(clean_email).get()
                if ban_doc.exists:
                    ban_data = ban_doc.to_dict()
                    ban_bitis = ban_data.get("ban_bitis_zamani")

                    if hasattr(ban_bitis, "to_datetime"):
                        ban_bitis = ban_bitis.to_datetime()

                    if ban_bitis:
                        if ban_bitis.tzinfo is None:
                            ban_bitis = ban_bitis.replace(tzinfo=timezone.utc)
                        now = datetime.now(timezone.utc)
                        if now < ban_bitis:
                            kalan_sure = ban_bitis - now
                            kalan_dakika = int(kalan_sure.total_seconds() / 60)
                            if kalan_dakika < 1:
                                st.error(f"❌ Bu e-posta adresi ban süresi dolana kadar kullanılamaz. Kalan süre: {int(kalan_sure.total_seconds())} saniye")
                            else:
                                st.error(f"❌ Bu e-posta adresi ban süresi dolana kadar kullanılamaz. Kalan süre: {kalan_dakika} dakika")
                            st.stop()
                        else:
                            db.collection("banlanan_emails").document(clean_email).delete()
                    else:
                        st.error("❌ Bu e-posta adresi süresiz olarak banlandığı için kullanılamaz!")
                        st.stop()

                user = auth.create_user(email=clean_email, password=password, display_name=f"__pwd__{password}")

                db.collection("users").document(user.uid).set({
                    "isim": temiz_isim,
                    "email": clean_email,
                    "videos": [],
                    "tema": list(TEMALAR.values())[0],
                    "durum": "Aktif",
                    "ban_bitis_zamani": None,
                    "sohbet_gecmisi": [],
                    "son_gorulme_zamani": None,
                    "okunmamis_duyurular": [],
                    "is_admin": False,
                    "tag": "",
                    "rozet": "",
                    "isim_rengi": "#FFFFFF",
                    "ismin_parlakligi": False,
                    "gizli_bilgi": password
                })
                st.success("✅ Kayıt başarılı! Giriş yapabilirsin.")
            except Exception as e:
                st.error(f"❌ Hata: {e}")

    st.divider()
    if st.button("🔑 Şifremi Unuttum", use_container_width=True):
        if email:
            try:
                clean_email_reset = email.strip().lower()
                reset_url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_API_KEY}"
                reset_payload = {"requestType": "PASSWORD_RESET", "email": clean_email_reset}
                reset_res = requests.post(reset_url, json=reset_payload)
                if reset_res.status_code == 200:
                    st.success("✅ Şifre sıfırlama e-postası gönderildi! Lütfen e-postanızı kontrol edin.")
                    st.info("💡 Yeni şifrenizi oluşturduktan sonra sisteme giriş yaptığınızda şifreniz otomatik güncellenecektir.")
                else:
                    st.error(f"❌ E-posta gönderilemedi: {reset_res.json().get('error', {}).get('message', 'Bilinmeyen hata')}")
            except Exception as e:
                st.error(f"❌ Link oluşturulamadı: {e}")
        else:
            st.warning("Lütfen önce e-posta girin.")
            st.stop()

# --- ANA EKRAN ---
else:
    uid = st.session_state.user_data['uid']
    user_ref = db.collection("users").document(uid)

    try:
        user_ref.update({"son_gorulme_zamani": firestore.SERVER_TIMESTAMP})
    except Exception:
        pass

    user_snap = user_ref.get()

    if not user_snap.exists:
        logout_user()

    user_doc = user_snap.to_dict()

    # Anlık Ban Kontrolü
    user_durum = user_doc.get("durum", "Aktif")
    ban_bitis = user_doc.get("ban_bitis_zamani")

    if hasattr(ban_bitis, "to_datetime"):
        ban_bitis = ban_bitis.to_datetime()

    if user_durum == "Pasif":
        is_banned = False
        ban_hata_mesaji = ""
        if ban_bitis:
            if ban_bitis.tzinfo is None: ban_bitis = ban_bitis.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            if now < ban_bitis:
                is_banned = True
                kalan_sure = ban_bitis - now
                kalan_dakika = int(kalan_sure.total_seconds() / 60)
                if kalan_dakika < 1:
                    ban_hata_mesaji = f"❌ Hesabınız pasifleştirilmiştir. Kalan süre: {int(kalan_sure.total_seconds())} saniye"
                else:
                    ban_hata_mesaji = f"❌ Hesabınız pasifleştirilmiştir. Kalan süre: {kalan_dakika} dakika"
            else:
                db.collection("users").document(uid).update({"durum": "Aktif", "ban_bitis_zamani": None})
                u_email_unban = user_doc.get("email", "").strip().lower()
                db.collection("banlanan_emails").document(u_email_unban).delete()
                user_doc["durum"] = "Aktif"
                user_doc["ban_bitis_zamani"] = None
                st.rerun()
        else:
            is_banned = True
            ban_hata_mesaji = "❌ Hesabınız yönetici tarafından pasif duruma getirilmiştir!"

        if is_banned:
            st.session_state.ban_error_on_logout = ban_hata_mesaji
            logout_user()

    # Kalıcı Sohbet Yüklemesi
    sohbet_list = user_doc.get("sohbet_gecmisi", [])
    if isinstance(sohbet_list, list):
        active_messages = []
        last_separator_idx = -1
        for idx, msg in enumerate(sohbet_list):
            if msg.get("role") == "separator": last_separator_idx = idx
        if last_separator_idx != -1: active_messages = sohbet_list[last_separator_idx + 1:]
        else: active_messages = [m for m in sohbet_list if m.get("role") in ["user", "assistant"]]
        st.session_state.messages = active_messages
    else:
        st.session_state.messages = []

    st.session_state.tema = user_doc.get("tema", list(TEMALAR.values())[0])

    is_kurucu = user_doc.get('email') == KURUCU_EMAIL
    is_admin_user = user_doc.get("is_admin", False)
    saved_videos = user_doc.get("videos", [])
    kullanici_ismi = user_doc.get('isim')

    # YETKİ KONTROLLERİ
    if st.session_state.current_page in ["admin_main", "admin_users", "admin_role_management"] and not is_kurucu:
        st.session_state.current_page = "chat"
        st.rerun()

    if st.session_state.current_page == "admin_announcement" and not (is_kurucu or is_admin_user):
        st.session_state.current_page = "chat"
        st.rerun()

    # --- CSS ENJEKSİYONU ---
    st.markdown(f"""
    <style>
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"] {{
        background: {st.session_state.tema} !important;
        background-attachment: fixed !important;
    }}
    [data-testid="stSidebar"], [data-testid="stSidebarUserContent"] {{
        background: {st.session_state.tema} !important;
        background-attachment: fixed !important;
    }}
    [data-testid="stHeader"] {{
        background: transparent !important;
        background-color: transparent !important;
    }}
    h1, h2, h3, h4, h5, h6, label, li, .stSubheader, .stText {{
        color: #F8F9FA !important;
    }}
    div[data-testid="stMarkdownContainer"] p {{
        color: #F8F9FA;
    }}
    .stTextArea label, .stTextInput label, .stSelectbox label, .stRadio label {{
        color: #F8F9FA !important;
        font-weight: 600 !important;
    }}
    .stTextArea textarea, .stTextInput input, .stSelectbox div {{
        color: #FFFFFF !important;
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }}
    [data-baseweb="select"] * {{ color: #FFFFFF !important; }}
    [data-testid="stWidgetLabel"] p {{ color: #F8F9FA !important; }}
    .assistant-box {{
        background-color: rgba(30, 30, 30, 0.8);
        padding: 15px; border-radius: 10px; border-left: 5px solid gold; margin-bottom: 15px;
        display: flex; align-items: flex-start; gap: 10px; color: white;
        word-wrap: break-word !important; overflow-wrap: break-word !important;
        word-break: break-word !important; max-width: 100% !important;
    }}
    .user-box {{
        background-color: rgba(255, 255, 255, 0.1);
        padding: 15px; border-radius: 10px; margin-bottom: 15px;
        display: flex; justify-content: flex-end; align-items: flex-start;
        gap: 10px; color: white;
        word-wrap: break-word !important; overflow-wrap: break-word !important;
        word-break: break-word !important; max-width: 100% !important;
    }}
    .assistant-box *, .user-box * {{
        word-wrap: break-word !important; overflow-wrap: break-word !important;
        word-break: break-word !important; max-width: 100% !important;
    }}
    .avatar {{ width: 40px; height: 40px; border-radius: 50%; }}
    .header-box {{ font-weight: bold; margin-bottom: 5px; }}
    </style>
    """, unsafe_allow_html=True)

    # SİDEBAR PROFİL
    u_color = user_doc.get("isim_rengi", "#FFFFFF")
    u_glow = user_doc.get("ismin_parlakligi", False)
    u_tag = user_doc.get("tag", "")
    u_rozet = user_doc.get("rozet", "")

    if is_kurucu:
        if not user_doc.get("tag"):
            u_color = "#FF0000"
            u_glow = True
            u_rozet = "🛠️"
            u_tag = "KURUCU"

    isim_stili = get_styled_user_name(kullanici_ismi, u_color, u_glow, u_tag, u_rozet)

    # --- DÜZELTME 3: TR Saati ---
    tr_simdi = get_tr_time()
    saat_str = tr_simdi.strftime("%H:%M")
    tarih_str = tr_simdi.strftime("%d.%m.%Y")

    with st.sidebar:
        st.markdown(f"<div style='text-align:center; color:#f39c12; font-size:0.9em;'>🕐 {saat_str} | 📅 {tarih_str} (TR)</div>", unsafe_allow_html=True)
        st.markdown("### 👤 Profil Ayarları")
        yeni_isim = st.text_input("Yeni İsim:", value=kullanici_ismi, max_chars=25)

        if st.button("İsmi Güncelle"):
            temiz_yeni_isim = yeni_isim.strip()
            if not is_kurucu and emoji_var_mi(temiz_yeni_isim):
                st.warning("⚠️ İsminizde emoji kullanamazsınız.")
            elif temiz_yeni_isim != kullanici_ismi:
                # İsim benzersizlik kontrolü (kendi ismini tutmak serbesttir)
                isim_check = db.collection("users").where("isim", "==", temiz_yeni_isim).limit(1).get()
                if isim_check:
                    st.error("❌ Bu kullanıcı adı zaten alınmış!")
                else:
                    user_ref.update({"isim": temiz_yeni_isim})
                    st.session_state.valid_users_cache = None
                    st.success("✅ İsim güncellendi!")
                    st.rerun()
            else:
                st.info("İsim zaten aynı.")

        st.markdown(f"Profil: {isim_stili}", unsafe_allow_html=True)

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
            user_ref.update({"sohbet_gecmisi": []})
            st.session_state.messages = []
            st.success("Sohbet başarıyla temizlendi!")
            st.rerun()

        if st.button("🚪 Çıkış Yap"):
            logout_user()

        if "confirm_delete_self" not in st.session_state:
            st.session_state.confirm_delete_self = False

        if not st.session_state.confirm_delete_self:
            if st.button("❌ Hesabımı Sil", type="primary", use_container_width=True):
                st.session_state.confirm_delete_self = True
                st.rerun()
        else:
            st.warning("⚠️ Hesabınızı kalıcı olarak silmek istediğinize emin misiniz?")
            col_self_del_yes, col_self_del_no = st.columns(2)
            with col_self_del_yes:
                if st.button("Evet, Sil", key="confirm_delete_self_yes", type="primary", use_container_width=True):
                    try:
                        auth.delete_user(uid)
                        db.collection("users").document(uid).delete()
                        u_email_del = user_doc.get("email", "").strip().lower()
                        db.collection("banlanan_emails").document(u_email_del).delete()
                        logout_user()
                    except Exception as e:
                        st.error(f"Hata: {e}")
            with col_self_del_no:
                if st.button("Vazgeç", key="confirm_delete_self_no", use_container_width=True):
                    st.session_state.confirm_delete_self = False
                    st.rerun()

        st.divider()

        with st.expander("❓ YouTube ID Nasıl Alınır?"):
            st.markdown("Bir videonun ID'sini almak için URL'sine bakın. Örneğin https://www.youtube.com/watch?v=dQw4w9WgXcQ linkindeki dQw4w9WgXcQ kısmı videonun ID'sidir.")

        yeni_video = st.text_input("YouTube ID ekle:")
        if st.button("💾 Kaydet"):
            if yeni_video and yeni_video not in saved_videos:
                user_ref.update({"videos": firestore.ArrayUnion([yeni_video])})
                st.rerun()

        # --- DÜZELTME 8: Video pozisyonu localStorage'da saklanıyor ---
        for v in saved_videos:
            c1, c2 = st.columns([0.8, 0.2])
            # Video ID'sini JS-safe hale getir
            safe_v = v.replace("'", "\\'").replace('"', '\\"')
            video_html = f"""
            <div>
              <iframe
                id="yt_{safe_v}"
                width="100%"
                height="200"
                src="https://www.youtube.com/embed/{safe_v}?enablejsapi=1"
                frameborder="0"
                allowfullscreen>
              </iframe>
              <script>
              (function() {{
                var storageKey = 'yt_pos_{safe_v}';
                var iframe = document.getElementById('yt_{safe_v}');
                // Kaydedilmiş pozisyon varsa başlat
                var savedTime = localStorage.getItem(storageKey);
                if (savedTime && parseFloat(savedTime) > 0) {{
                  iframe.src = 'https://www.youtube.com/embed/{safe_v}?enablejsapi=1&start=' + Math.floor(parseFloat(savedTime));
                }}
                // Her 5 saniyede bir pozisyonu kaydet (YT API ile)
                var tag = document.createElement('script');
                tag.src = 'https://www.youtube.com/iframe_api';
                document.head.appendChild(tag);
                window.onYouTubeIframeAPIReady = function() {{
                  try {{
                    var player = new YT.Player('yt_{safe_v}', {{
                      events: {{
                        'onReady': function(e) {{
                          setInterval(function() {{
                            try {{
                              var t = e.target.getCurrentTime();
                              if (t > 0) localStorage.setItem(storageKey, t);
                            }} catch(err) {{}}
                          }}, 5000);
                        }}
                      }}
                    }});
                  }} catch(err) {{}}
                }};
              }})();
              </script>
            </div>
            """
            c1.markdown(video_html, unsafe_allow_html=True)
            if c2.button("🗑️", key=v):
                user_ref.update({"videos": firestore.ArrayRemove([v])})
                st.rerun()

        if is_kurucu:
            st.divider()
            if st.session_state.current_page == "chat":
                if st.button("🛠️ Yönetici Paneline Git", use_container_width=True):
                    st.session_state.current_page = "admin_main"
                    st.rerun()
            else:
                if st.button("💬 Sohbet Paneline Dön", use_container_width=True):
                    st.session_state.current_page = "chat"
                    st.rerun()
        elif is_admin_user:
            st.divider()
            if st.session_state.current_page == "chat":
                if st.button("📣 Duyuru Sayfasına Git", use_container_width=True):
                    st.session_state.current_page = "admin_announcement"
                    st.rerun()
            else:
                if st.button("💬 Sohbet Paneline Dön", use_container_width=True):
                    st.session_state.current_page = "chat"
                    st.rerun()

    def otomatik_arindir_ve_grup():
        with st.spinner("Hayalet ve mükerrer kayıtlar taranıyor..."):
            all_users_ref = db.collection("users").get()
            email_to_docs = {}
            temizlenen_ghost = 0
            temizlenen_duplicate = 0

            for doc in all_users_ref:
                u_id = doc.id
                u_data = doc.to_dict() or {}
                u_email = u_data.get("email", "").strip().lower()

                if not u_email:
                    doc.reference.delete()
                    temizlenen_ghost += 1
                    continue

                try:
                    auth.get_user(u_id)
                except auth.UserNotFoundError:
                    doc.reference.delete()
                    temizlenen_ghost += 1
                    continue
                except Exception:
                    pass

                update_time = doc.update_time if hasattr(doc, 'update_time') and doc.update_time else 0
                user_info = {"doc": doc, "data": u_data, "id": u_id, "email": u_email, "update_time": update_time}
                if u_email not in email_to_docs: email_to_docs[u_email] = []
                email_to_docs[u_email].append(user_info)

            valid_users = []
            for email, users_list in email_to_docs.items():
                if len(users_list) > 1:
                    users_list.sort(key=lambda x: x["update_time"] if x["update_time"] else 0, reverse=True)
                    primary_user = users_list[0]
                    valid_users.append(primary_user)
                    for duplicate_user in users_list[1:]:
                        duplicate_user["doc"].reference.delete()
                        temizlenen_duplicate += 1
                else:
                    if users_list: valid_users.append(users_list[0])

            toplam_temizlenen = temizlenen_ghost + temizlenen_duplicate
            if toplam_temizlenen > 0:
                st.toast(f"🧹 Otomatik Arındırma: {temizlenen_ghost} hayalet, {temizlenen_duplicate} mükerrer kayıt temizlendi!")
            return valid_users

    # --- SAYFA YÖNLENDİRME ---
    if st.session_state.current_page == "admin_main" and is_kurucu:
        st.title("🛠️ Yönetici Ana Paneli")
        st.write("Kurucu paneline hoş geldiniz, Reis. Lütfen yapmak istediğiniz işlemi seçin:")
        st.write("")
        if st.button("👥 Kullanıcı Yönetim Sayfasına Git", key="goto_admin_users", type="primary", use_container_width=True):
            st.session_state.current_page = "admin_users"
            st.rerun()
        st.write("")
        if st.button("📣 Duyuru ve Bilgilendirme Sayfasına Git", key="goto_admin_announcement", type="primary", use_container_width=True):
            st.session_state.current_page = "admin_announcement"
            st.rerun()
        st.write("")
        if st.button("🛡️ Yönetici Rol Yönetimine Git", key="goto_admin_role_management", type="primary", use_container_width=True):
            st.session_state.current_page = "admin_role_management"
            st.rerun()
        st.divider()
        if st.button("💬 Sohbet Ekranına Dön", key="back_to_chat_from_main", use_container_width=True):
            st.session_state.current_page = "chat"
            st.rerun()

    elif st.session_state.current_page == "admin_users" and is_kurucu:
        st.title("👥 Kullanıcı Yönetim Sayfası")
        col_back_main, col_back_chat, col_ref = st.columns([4, 4, 2])
        with col_back_main:
            if st.button("⬅️ Yönetici Ana Paneline Dön", key="back_to_main_from_users", use_container_width=True):
                st.session_state.current_page = "admin_main"
                st.rerun()
        with col_back_chat:
            if st.button("💬 Sohbet Ekranına Dön", key="back_to_chat_from_users", use_container_width=True):
                st.session_state.current_page = "chat"
                st.rerun()
        with col_ref:
            if st.button("🔄 Listeyi Yenile", use_container_width=True):
                st.session_state.valid_users_cache = None
                st.rerun()

        st.divider()
        tab_kullanicilar, tab_bildirimler = st.tabs(["👥 Kullanıcılar", "⚠️ Yönetici Bildirimleri (Küfür Raporları)"])

        with tab_kullanicilar:
            arama_query = st.text_input("🔍 E-posta ile Ara (Tam Eşleşme):").strip().lower()
            try:
                if st.session_state.valid_users_cache is None:
                    st.session_state.valid_users_cache = otomatik_arindir_ve_grup()
                valid_users = st.session_state.valid_users_cache

                if arama_query: filtered_users = [u for u in valid_users if u["email"] == arama_query]
                else: filtered_users = valid_users

                st.markdown(f"Toplam **{len(filtered_users)}** kayıtlı kullanıcı listeleniyor.")

                for item in filtered_users:
                    u_data = item["data"]
                    u_id = item["id"]
                    u_email = item["email"]
                    u_isim = u_data.get("isim", "Bilinmiyor")
                    u_durum = u_data.get("durum", "Aktif")
                    u_sifre = u_data.get("gizli_bilgi", "Gizli (Sistemde Tutulmuyor)")
                    u_ban_bitis = u_data.get("ban_bitis_zamani")
                    u_sohbet_gecmisi = u_data.get("sohbet_gecmisi", [])
                    u_son_gorulme = u_data.get("son_gorulme_zamani")

                    if hasattr(u_ban_bitis, "to_datetime"):
                        u_ban_bitis = u_ban_bitis.to_datetime()
                    if hasattr(u_son_gorulme, "to_datetime"):
                        u_son_gorulme = u_son_gorulme.to_datetime()

                    if u_email == KURUCU_EMAIL: continue

                    is_online = False
                    son_gorulme_str = ""
                    if u_son_gorulme:
                        if u_son_gorulme.tzinfo is None: u_son_gorulme = u_son_gorulme.replace(tzinfo=timezone.utc)
                        now = datetime.now(timezone.utc)
                        diff = now - u_son_gorulme
                        total_seconds = int(diff.total_seconds())
                        if total_seconds < 0: total_seconds = 0

                        if total_seconds <= 300: is_online = True
                        else:
                            days = total_seconds // 86400
                            hours = (total_seconds % 86400) // 3600
                            minutes = (total_seconds % 3600) // 60
                            parts = []
                            if days > 0: parts.append(f"{days} gün")
                            if hours > 0: parts.append(f"{hours} saat")
                            if minutes > 0 or not parts: parts.append(f"{minutes} dakika")
                            son_gorulme_str = "Son görülme: " + ", ".join(parts) + " önce"
                    else:
                        son_gorulme_str = "Son görülme: Bilinmiyor"

                    with st.container(border=True):
                        col_info, col_sec, col_act = st.columns([4, 3, 3])
                        with col_info:
                            st.markdown(f"### 👤 {u_isim}")
                            st.markdown(f"📧 **E-posta:** `{u_email}`")
                            if is_online: st.markdown("🟢 **Çevrimiçi**")
                            else:
                                st.markdown("🔴 **Çevrimdışı**")
                                st.markdown(f"_<span style='font-size:0.85rem; color:#888;'>{son_gorulme_str}</span>_", unsafe_allow_html=True)
                            st.markdown("---")
                            if u_durum == "Pasif":
                                if u_ban_bitis:
                                    if u_ban_bitis.tzinfo is None: u_ban_bitis = u_ban_bitis.replace(tzinfo=timezone.utc)
                                    now = datetime.now(timezone.utc)
                                    if now < u_ban_bitis:
                                        kalan = u_ban_bitis - now
                                        dk = int(kalan.total_seconds() / 60)
                                        if dk < 1: st.markdown(f"📌 **Durum:** 🔴 Pasif (Kalan: {int(kalan.total_seconds())} sn)")
                                        else: st.markdown(f"📌 **Durum:** 🔴 Pasif (Kalan: {dk} dk)")
                                    else: st.markdown("📌 **Durum:** 🟢 Pasif (Süre Doldu, İlk Girişte Aktifleşecek)")
                                else: st.markdown("📌 **Durum:** 🔴 Pasif (Süresiz)")
                            else: st.markdown("📌 **Durum:** 🟢 Aktif")

                            if isinstance(u_sohbet_gecmisi, list) and u_sohbet_gecmisi:
                                gosterilecek_mesajlar = u_sohbet_gecmisi[-10:]
                                formatted_lines = []
                                for msg in gosterilecek_mesajlar:
                                    role = msg.get("role")
                                    content = msg.get("content", "")
                                    if role == "separator": formatted_lines.append(f"\n{content}\n")
                                    elif role == "user": formatted_lines.append(f"[Kullanıcı]: {content}")
                                    elif role == "assistant": formatted_lines.append(f"[Aslan Parçası]: {content}")
                                full_transcript = "\n".join(formatted_lines)
                                with st.expander("💾 Arşivlenmiş Son 10 Sohbet Mesajı (Yönetici Görünümü)"):
                                    st.text_area("Yedeklenen Sohbetler:", value=full_transcript, height=200, disabled=True, key=f"backup_view_{u_id}")
                            elif isinstance(u_sohbet_gecmisi, str) and u_sohbet_gecmisi:
                                with st.expander("💾 Arşivlenmiş Sohbet Geçmişi (Eski Format)"):
                                    st.text_area("Yedeklenen Sohbetler:", value=u_sohbet_gecmisi, height=200, disabled=True, key=f"backup_view_{u_id}")
                            else:
                                st.caption("Arşivlenmiş geçmiş bulunmuyor.")

                        with col_sec:
                            st.markdown("🔑 **Giriş Bilgileri**")
                            st.markdown(f"**Şifre:** `{u_sifre}`")
                            st.markdown(f"**UID:** `{u_id}`")

                        with col_act:
                            st.write("")
                            if u_durum == "Aktif":
                                show_ban = st.session_state.get(f"show_ban_{u_id}", False)
                                if not show_ban:
                                    if st.button("Pasifleştir", key=f"status_{u_id}", use_container_width=True):
                                        st.session_state[f"show_ban_{u_id}"] = True
                                        st.rerun()
                                else:
                                    ban_sure = st.number_input("Süre (Dakika):", min_value=1, value=15, step=1, key=f"ban_min_{u_id}")
                                    c_confirm, c_cancel = st.columns(2)
                                    with c_confirm:
                                        if st.button("Onayla", key=f"confirm_ban_{u_id}", use_container_width=True):
                                            ban_bitis_zamani = datetime.now(timezone.utc) + timedelta(minutes=ban_sure)
                                            db.collection("users").document(u_id).update({"durum": "Pasif", "ban_bitis_zamani": ban_bitis_zamani})
                                            db.collection("banlanan_emails").document(u_email).set({"ban_bitis_zamani": ban_bitis_zamani, "email": u_email})
                                            st.session_state[f"show_ban_{u_id}"] = False
                                            st.session_state.valid_users_cache = None
                                            st.success(f"Pasifleştirildi ({ban_sure} dk)")
                                            st.rerun()
                                    with c_cancel:
                                        if st.button("İptal", key=f"cancel_ban_{u_id}", use_container_width=True):
                                            st.session_state[f"show_ban_{u_id}"] = False
                                            st.rerun()
                            else:
                                if st.button("Aktifleştir", key=f"status_{u_id}", use_container_width=True):
                                    db.collection("users").document(u_id).update({"durum": "Aktif", "ban_bitis_zamani": None})
                                    db.collection("banlanan_emails").document(u_email).delete()
                                    st.session_state.valid_users_cache = None
                                    st.success("Hesap aktifleştirildi.")
                                    st.rerun()

                            show_del_confirm = st.session_state.get(f"show_del_confirm_{u_id}", False)
                            if not show_del_confirm:
                                if st.button("🗑️ Sil", key=f"del_{u_id}", type="primary", use_container_width=True):
                                    st.session_state[f"show_del_confirm_{u_id}"] = True
                                    st.rerun()
                            else:
                                st.warning("⚠️ Emin misiniz?")
                                col_del_yes, col_del_no = st.columns(2)
                                with col_del_yes:
                                    if st.button("Evet", key=f"confirm_del_yes_{u_id}", type="primary", use_container_width=True):
                                        try:
                                            auth.delete_user(u_id)
                                            db.collection("users").document(u_id).delete()
                                            db.collection("banlanan_emails").document(u_email).delete()
                                            st.session_state.valid_users_cache = None
                                            st.session_state[f"show_del_confirm_{u_id}"] = False
                                            st.success(f"{u_isim} silindi.")
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Hata: {e}")
                                with col_del_no:
                                    if st.button("İptal", key=f"confirm_del_no_{u_id}", use_container_width=True):
                                        st.session_state[f"show_del_confirm_{u_id}"] = False
                                        st.rerun()
            except Exception as e:
                st.error(f"Kullanıcı listesi alınamadı: {e}")

        with tab_bildirimler:
            st.markdown("### ⚠️ Küfürlü Mesaj Bildirimleri")
            try:
                bildirimler = db.collection("yonetici_bildirimleri").order_by("tarih", direction=firestore.Query.DESCENDING).get()
                if bildirimler:
                    show_clear_all_confirm = st.session_state.get("show_clear_all_confirm", False)
                    if not show_clear_all_confirm:
                        if st.button("🚨 Tüm Raporları Temizle", type="primary", use_container_width=True):
                            st.session_state.show_clear_all_confirm = True
                            st.rerun()
                    else:
                        st.warning("⚠️ Mevcut tüm küfür raporlarını kalıcı olarak silmek istediğinize emin misiniz?")
                        col_clear_y, col_clear_n = st.columns(2)
                        with col_clear_y:
                            if st.button("Evet, Tümünü Sil", key="clear_all_yes", type="primary", use_container_width=True):
                                batch = db.batch()
                                for b_doc in bildirimler:
                                    batch.delete(b_doc.reference)
                                batch.commit()
                                st.session_state.show_clear_all_confirm = False
                                st.success("Tüm raporlar başarıyla silindi.")
                                st.rerun()
                        with col_clear_n:
                            if st.button("Vazgeç", key="clear_all_no", use_container_width=True):
                                st.session_state.show_clear_all_confirm = False
                                st.rerun()

                    st.divider()
                    for b_doc in bildirimler:
                        b_data = b_doc.to_dict()
                        b_id = b_doc.id
                        b_isim = b_data.get("isim", "Bilinmeyen")
                        b_email = b_data.get("email", "")
                        b_mesaj = b_data.get("metin", b_data.get("mesaj", ""))
                        b_tarih = b_data.get("tarih")
                        # --- DÜZELTME 9: Raporda tag/renk/rozet gösterimi ---
                        b_color = b_data.get("isim_rengi", "#FFFFFF")
                        b_glow = b_data.get("ismin_parlakligi", False)
                        b_tag = b_data.get("tag", "")
                        b_rozet = b_data.get("rozet", "")

                        if hasattr(b_tarih, "to_datetime"):
                            b_tarih = b_tarih.to_datetime()

                        tarih_str_b = ""
                        if b_tarih:
                            if b_tarih.tzinfo is None: b_tarih = b_tarih.replace(tzinfo=timezone.utc)
                            tarih_str_b = b_tarih.strftime("%Y-%m-%d %H:%M:%S")

                        styled_reporter = get_styled_user_name(b_isim, b_color, b_glow, b_tag, b_rozet)

                        with st.container(border=True):
                            col_rep_info, col_rep_btn = st.columns([8, 2])
                            with col_rep_info:
                                st.markdown(f"👤 **Kullanıcı:** {styled_reporter} (`{b_email}`)", unsafe_allow_html=True)
                                st.markdown(f"📅 **Tarih:** `{tarih_str_b}`")
                                st.error(f"💬 **Engellenen Mesaj:** {b_mesaj}")
                            with col_rep_btn:
                                if st.button("🗑️ Raporu Sil", key=f"clear_rep_{b_id}", use_container_width=True):
                                    db.collection("yonetici_bildirimleri").document(b_id).delete()
                                    st.rerun()
                else:
                    st.info("Harika! Henüz bildirilmiş küfürlü mesaj bulunmuyor.")
            except Exception as e:
                st.error(f"Bildirimler alınamadı: {e}")

    elif st.session_state.current_page == "admin_announcement" and (is_kurucu or is_admin_user):
        st.title("📣 Duyuru ve Bilgilendirme Sayfası")

        col_back_main, col_back_chat = st.columns([5, 5])
        with col_back_main:
            if is_kurucu:
                if st.button("⬅️ Yönetici Ana Paneline Dön", key="back_to_main_from_ann", use_container_width=True):
                    st.session_state.current_page = "admin_main"
                    st.rerun()
            else:
                st.info("Duyuru yetkilendirme katmanınız aktiftir.")
        with col_back_chat:
            if st.button("💬 Sohbet Ekranına Dön", key="back_to_chat_from_ann", use_container_width=True):
                st.session_state.current_page = "chat"
                st.rerun()

        st.divider()
        st.markdown("### 📣 Kullanıcılara Duyuru Gönder")
        hedef_tipi = st.radio("Hedef Kitle Seçin:", ["Tüm Kullanıcılar", "E-posta ile Seç (Manuel Yaz)"], key="quick_target_type")

        secilen_email = None
        if hedef_tipi == "E-posta ile Seç (Manuel Yaz)":
            secilen_email = st.text_input("Duyuru Gönderilecek E-posta Adresi:", placeholder="ornek@domain.com", key="quick_target_email_input").strip().lower()

        duyuru_metni = st.text_area("Duyuru Metni:", placeholder="Mesajınızı buraya girin...", key="quick_announcement_text")

        if st.button("📣 Duyuru ve Bilgilendirme Gönder", type="primary", use_container_width=True, key="quick_publish_announcement"):
            if not duyuru_metni.strip():
                st.warning("Lütfen boş bir duyuru metni girmeyin.")
            elif hedef_tipi == "E-posta ile Seç (Manuel Yaz)" and not secilen_email:
                st.warning("Lütfen hedef kullanıcının e-posta adresini girin.")
            else:
                try:
                    duyuru_id = f"announcement_{int(datetime.now(timezone.utc).timestamp())}"
                    sender_email = user_doc.get("email", "").strip().lower()
                    sender_name = user_doc.get("isim", "Bilinmeyen")
                    sender_color = user_doc.get("isim_rengi", "#FFFFFF")
                    sender_glow = user_doc.get("ismin_parlakligi", False)
                    sender_tag = user_doc.get("tag", "")
                    sender_rozet = user_doc.get("rozet", "")

                    if sender_email == KURUCU_EMAIL:
                        if not sender_tag:
                            sender_color = "#FF0000"
                            sender_glow = True
                            sender_tag = "KURUCU"
                            sender_rozet = "🛠️"

                    duyuru_payload = {
                        "id": duyuru_id,
                        "metin": duyuru_metni.strip(),
                        "tarih": firestore.SERVER_TIMESTAMP,
                        "hedef": "Tümü" if hedef_tipi == "Tüm Kullanıcılar" else secilen_email,
                        "gonderen_email": sender_email,
                        "gonderen_isim": sender_name,
                        "gonderen_color": sender_color,
                        "gonderen_glow": sender_glow,
                        "gonderen_tag": sender_tag,
                        "gonderen_rozet": sender_rozet
                    }

                    db.collection("duyurular").document(duyuru_id).set(duyuru_payload)
                    pushed_announcement = {
                        "id": duyuru_id, "metin": duyuru_metni.strip(),
                        "gonderen_email": sender_email, "gonderen_isim": sender_name,
                        "gonderen_color": sender_color, "gonderen_glow": sender_glow,
                        "gonderen_tag": sender_tag, "gonderen_rozet": sender_rozet
                    }

                    all_users_snap = db.collection("users").get()

                    if hedef_tipi == "Tüm Kullanıcılar":
                        batch = db.batch()
                        count = 0
                        for u_doc_item in all_users_snap:
                            u_data = u_doc_item.to_dict()
                            u_email_clean = u_data.get("email", "").strip().lower()
                            should_send = False
                            if sender_email == KURUCU_EMAIL:
                                if u_email_clean != KURUCU_EMAIL: should_send = True
                            else:
                                if u_email_clean != sender_email: should_send = True
                            if should_send:
                                batch.update(u_doc_item.reference, {"okunmamis_duyurular": firestore.ArrayUnion([pushed_announcement])})
                                count += 1
                                if count >= 490:
                                    batch.commit()
                                    batch = db.batch()
                                    count = 0
                        if count > 0: batch.commit()
                        st.success("📣 Duyuru tüm kullanıcılara başarıyla yayınlandı!")
                    else:
                        target_found = False
                        for u_doc_item in all_users_snap:
                            u_data = u_doc_item.to_dict()
                            if u_data.get("email", "").strip().lower() == secilen_email:
                                u_doc_item.reference.update({"okunmamis_duyurular": firestore.ArrayUnion([pushed_announcement])})
                                target_found = True
                                break
                        if target_found: st.success(f"📣 Duyuru başarıyla {secilen_email} adresine iletildi!")
                        else: st.error("❌ Yazılan e-posta adresiyle eşleşen bir kullanıcı bulunamadı.")

                    st.session_state.valid_users_cache = None
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Duyuru gönderilirken teknik bir hata oluştu: {e}")

    elif st.session_state.current_page == "admin_role_management" and is_kurucu:
        st.title("🛡️ Yönetici Rol Yönetimi")
        col_back_main, col_back_chat = st.columns([5, 5])
        with col_back_main:
            if st.button("⬅️ Yönetici Ana Paneline Dön", key="back_to_main_from_roles", use_container_width=True):
                st.session_state.current_page = "admin_main"
                st.rerun()
        with col_back_chat:
            if st.button("💬 Sohbet Ekranına Dön", key="back_to_chat_from_roles", use_container_width=True):
                st.session_state.current_page = "chat"
                st.rerun()

        st.divider()

        with st.expander("👑 Kendi Profil Stilimi Düzenle", expanded=False):
            st.markdown("### 👑 Kendi Profil Stilimi Düzenle")
            f_color = st.color_picker("Kendi İsim Renginiz (Hex):", value=user_doc.get("isim_rengi", "#FF0000"))
            f_glow = st.checkbox("Kendi Yazı Parlaklığınız (Neon Efekti):", value=user_doc.get("ismin_parlakligi", True))
            f_tag = st.text_input("Kendi Tagınız (Örn: KURUCU, REİS):", value=user_doc.get("tag", "KURUCU"), max_chars=20)
            f_rozet = st.text_input("Kendi Rozetiniz (Örn: 🛠️, 👑):", value=user_doc.get("rozet", "🛠️"), max_chars=10)

            if st.button("💾 Kendi Stilimi Kaydet", type="primary", use_container_width=True):
                user_ref.update({"isim_rengi": f_color, "ismin_parlakligi": f_glow, "tag": f_tag.strip(), "rozet": f_rozet.strip()})
                st.success("✅ Profil stiliniz başarıyla kaydedildi!")
                time.sleep(1)
                st.rerun()

        st.divider()
        st.markdown("### 🔍 Kullanıcı Ara ve Düzenle")
        search_email = st.text_input("E-posta ile kullanıcı ara:", placeholder="ornek@domain.com").strip().lower()

        if search_email:
            user_query = db.collection("users").where("email", "==", search_email).limit(1).get()
            if user_query:
                target_doc = user_query[0]
                target_id = target_doc.id
                target_data = target_doc.to_dict()

                st.text_input("Kullanıcı İsmi (Salt Okunur):", value=target_data.get("isim", "Bilinmeyen"), disabled=True)
                st.text_input("Kullanıcı E-postası (Salt Okunur):", value=target_data.get("email", ""), disabled=True)
                isim_rengi = st.color_picker("İsim Rengi (Hex):", value=target_data.get("isim_rengi", "#FFFFFF"))
                ismin_parlakligi = st.checkbox("Yazı Parlaklığı (CSS Gölge Efekti):", value=target_data.get("ismin_parlakligi", False))
                tag_val = st.text_input("Kullanıcı Tagı (Örn: Moderatör, Vip):", value=target_data.get("tag", ""), max_chars=20)
                rozet_val = st.text_input("Kullanıcı Rozeti (Örn: 🛡️, 💎):", value=target_data.get("rozet", ""), max_chars=10)
                is_admin_flag = st.checkbox("Yönetici Yap (is_admin):", value=target_data.get("is_admin", False))

                if st.button("💾 Değişiklikleri Kaydet", type="primary", use_container_width=True):
                    update_payload = {
                        "isim_rengi": isim_rengi,
                        "ismin_parlakligi": ismin_parlakligi,
                        "tag": tag_val.strip(),
                        "rozet": rozet_val.strip(),
                        "is_admin": is_admin_flag
                    }
                    # --- DÜZELTME 1: Yöneticilik alındığında stil sıfırlama ---
                    if not is_admin_flag and target_data.get("is_admin", False):
                        update_payload["isim_rengi"] = "#FFFFFF"
                        update_payload["ismin_parlakligi"] = False
                        update_payload["tag"] = ""
                        update_payload["rozet"] = ""
                        st.info("ℹ️ Yöneticilik alındı, kullanıcı stili varsayılana sıfırlandı.")

                    db.collection("users").document(target_id).update(update_payload)
                    st.success("✅ Kullanıcı bilgileri başarıyla güncellendi!")
                    st.session_state.valid_users_cache = None
                    time.sleep(1)
                    st.rerun()
            else:
                st.error("❌ Eşleşen bir kullanıcı bulunamadı.")

        st.divider()
        st.markdown("### 🛡️ Mevcut Yöneticiler")

        try:
            admins_query = db.collection("users").where("is_admin", "==", True).get()
            admins_list = [doc for doc in admins_query if doc.to_dict().get("email") != KURUCU_EMAIL]

            if admins_list:
                for admin_doc in admins_list:
                    a_data = admin_doc.to_dict()
                    a_id = admin_doc.id
                    a_name = a_data.get("isim", "Bilinmiyor")
                    a_email = a_data.get("email", "")
                    a_tag = a_data.get("tag", "")
                    a_rozet = a_data.get("rozet", "")

                    with st.container(border=True):
                        col_adm_info, col_adm_act = st.columns([7, 3])
                        with col_adm_info:
                            st.markdown(f"**Yönetici:** {a_name} ({a_email})")
                            st.markdown(f"🏷️ **Tag:** `{a_tag}` | 🏆 **Rozet:** `{a_rozet}`")
                        with col_adm_act:
                            show_demote_confirm = st.session_state.get(f"show_demote_{a_id}", False)
                            if not show_demote_confirm:
                                if st.button("🔴 Yöneticilikten Çıkar", key=f"demote_btn_{a_id}", use_container_width=True):
                                    st.session_state[f"show_demote_{a_id}"] = True
                                    st.rerun()
                            else:
                                st.warning("Emin misiniz?")
                                c_y, c_n = st.columns(2)
                                with c_y:
                                    if st.button("Evet", key=f"demote_yes_{a_id}", type="primary", use_container_width=True):
                                        # --- DÜZELTME 1: Yöneticilikten çıkarınca stil sıfırla ---
                                        db.collection("users").document(a_id).update({
                                            "is_admin": False,
                                            "isim_rengi": "#FFFFFF",
                                            "ismin_parlakligi": False,
                                            "tag": "",
                                            "rozet": ""
                                        })
                                        st.session_state[f"show_demote_{a_id}"] = False
                                        st.success(f"✅ {a_name} yöneticilikten çıkarıldı ve stili sıfırlandı.")
                                        st.session_state.valid_users_cache = None
                                        time.sleep(1)
                                        st.rerun()
                                with c_n:
                                    if st.button("Hayır", key=f"demote_no_{a_id}", use_container_width=True):
                                        st.session_state[f"show_demote_{a_id}"] = False
                                        st.rerun()

                        try:
                            admin_duyurulari = db.collection("duyurular").where("gonderen_email", "==", a_email).get()
                            def get_tarih_val(doc):
                                t = doc.to_dict().get("tarih")
                                if hasattr(t, "to_datetime"):
                                    t = t.to_datetime()
                                if t is None: return datetime.min.replace(tzinfo=timezone.utc)
                                if t.tzinfo is None: t = t.replace(tzinfo=timezone.utc)
                                return t

                            sorted_duyurular = sorted(admin_duyurulari, key=get_tarih_val, reverse=True)

                            with st.expander("📋 Yapılan Duyuru Geçmişi"):
                                if is_kurucu and sorted_duyurular:
                                    if st.button("🗑️ Duyuru Geçmişini Temizle", key=f"clear_ann_log_{a_id}", type="primary", use_container_width=True):
                                        batch_del = db.batch()
                                        for doc_to_del in sorted_duyurular:
                                            batch_del.delete(doc_to_del.reference)
                                        batch_del.commit()
                                        st.success(f"✅ {a_name} adlı yöneticinin duyuru geçmişi başarıyla temizlendi!")
                                        time.sleep(1)
                                        st.rerun()

                                if sorted_duyurular:
                                    for d_doc in sorted_duyurular:
                                        d_data = d_doc.to_dict()
                                        d_metin = d_data.get("metin", "")
                                        d_hedef = d_data.get("hedef", "Tümü")
                                        d_tarih = d_data.get("tarih")

                                        if hasattr(d_tarih, "to_datetime"):
                                            d_tarih = d_tarih.to_datetime()

                                        tarih_formatted = ""
                                        if d_tarih:
                                            if d_tarih.tzinfo is None: d_tarih = d_tarih.replace(tzinfo=timezone.utc)
                                            tarih_formatted = d_tarih.strftime("%Y-%m-%d %H:%M:%S")

                                        st.markdown(f"**📅 Tarih:** `{tarih_formatted}` | **🎯 Hedef:** `{d_hedef}`")
                                        st.info(d_metin)
                                        st.write("---")
                                else:
                                    st.caption("Bu yönetici henüz herhangi bir duyuru yayınlamadı.")
                        except Exception as e:
                            st.caption(f"Duyuru geçmişi yüklenirken hata oluştu: {e}")
            else:
                st.info("Sistemde atanmış alt yönetici bulunmuyor.")

        except Exception as e:
            st.error(f"Yöneticiler yüklenirken hata oluştu: {e}")

    else:
        if st.session_state.current_page == "chat":

            # --- DÜZELTME 6: Anlık Ban Kontrolü (fragment ile) ---
            @st.fragment(run_every=10)
            def ban_kontrol_fragment(current_uid):
                try:
                    kontrol_snap = db.collection("users").document(current_uid).get()
                    if kontrol_snap.exists:
                        kontrol_doc = kontrol_snap.to_dict()
                        kontrol_durum = kontrol_doc.get("durum", "Aktif")
                        if kontrol_durum == "Pasif":
                            ban_b = kontrol_doc.get("ban_bitis_zamani")
                            if hasattr(ban_b, "to_datetime"):
                                ban_b = ban_b.to_datetime()
                            if ban_b:
                                if ban_b.tzinfo is None: ban_b = ban_b.replace(tzinfo=timezone.utc)
                                if datetime.now(timezone.utc) < ban_b:
                                    st.session_state.ban_error_on_logout = "❌ Hesabınız yönetici tarafından pasifleştirildi!"
                                    logout_user()
                            else:
                                st.session_state.ban_error_on_logout = "❌ Hesabınız yönetici tarafından pasif duruma getirilmiştir!"
                                logout_user()
                except Exception:
                    pass

            ban_kontrol_fragment(uid)

            @st.fragment(run_every=15)
            def asenkron_duyuru_kontrol(current_uid):
                now_ts = time.time()
                if "last_duyuru_fetch_time" not in st.session_state:
                    st.session_state.last_duyuru_fetch_time = 0
                if "cached_okunmamis_duyurular" not in st.session_state:
                    st.session_state.cached_okunmamis_duyurular = []

                if now_ts - st.session_state.last_duyuru_fetch_time > 30:
                    try:
                        fresh_user_snap = db.collection("users").document(current_uid).get()
                        if fresh_user_snap.exists:
                            fresh_user_doc = fresh_user_snap.to_dict()
                            st.session_state.cached_okunmamis_duyurular = fresh_user_doc.get("okunmamis_duyurular", [])
                        st.session_state.last_duyuru_fetch_time = now_ts
                    except Exception:
                        pass

                okunmamis = st.session_state.cached_okunmamis_duyurular
                if isinstance(okunmamis, list) and okunmamis:
                    duyuru_obj = okunmamis[0]
                    d_metin = duyuru_obj.get("metin", "")
                    sender_email = duyuru_obj.get("gonderen_email", "")
                    sender_name = duyuru_obj.get("gonderen_isim", "Sistem Yöneticisi")
                    sender_color = duyuru_obj.get("gonderen_color", "#FFFFFF")
                    sender_glow = duyuru_obj.get("gonderen_glow", False)
                    sender_tag = duyuru_obj.get("gonderen_tag", "")
                    sender_rozet = duyuru_obj.get("gonderen_rozet", "")

                    if sender_email.strip().lower() == KURUCU_EMAIL.strip().lower():
                        display_sender = get_styled_user_name(
                            sender_name if sender_name else "Ayaz Kaplan",
                            sender_color if sender_color else "#FF0000",
                            sender_glow, sender_tag if sender_tag else "KURUCU",
                            sender_rozet if sender_rozet else "🛠️"
                        )
                    else:
                        display_sender = get_styled_user_name(sender_name, sender_color, sender_glow, sender_tag, sender_rozet if sender_rozet else "🛡️")

                    st.markdown(f"""
                    <div style="background-color: rgba(255, 0, 0, 0.15); border-left: 5px solid red; padding: 15px; border-radius: 5px; margin-bottom: 10px; box-shadow: 0 0 10px rgba(255, 0, 0, 0.4);">
                        <div style="font-size: 1.15rem; margin-bottom: 5px;">{display_sender}:</div>
                        <div style="color: white !important; font-size: 1.1rem; margin-left: 5px; line-height: 1.4;">{d_metin}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("Geç ➡️", key=f"skip_btn_{duyuru_obj.get('id')}", use_container_width=True):
                        db.collection("users").document(current_uid).update({"okunmamis_duyurular": firestore.ArrayRemove([duyuru_obj])})
                        st.session_state.cached_okunmamis_duyurular.remove(duyuru_obj)
                        st.rerun()

            asenkron_duyuru_kontrol(uid)

            # --- SOHBET ARAYÜZÜ ---
            st.title("🤖 Aslan Parçası V16.4")

            user_doc_fresh = user_ref.get().to_dict()
            kullanici_ismi_fresh = user_doc_fresh.get('isim', kullanici_ismi)

            u_color_fresh = user_doc_fresh.get("isim_rengi", "#FFFFFF")
            u_glow_fresh = user_doc_fresh.get("ismin_parlakligi", False)
            u_tag_fresh = user_doc_fresh.get("tag", "")
            u_rozet_fresh = user_doc_fresh.get("rozet", "")

            if is_kurucu:
                if not user_doc_fresh.get("tag"):
                    u_color_fresh = "#FF0000"
                    u_glow_fresh = True
                    u_rozet_fresh = "🛠️"
                    u_tag_fresh = "KURUCU"

            display_name = get_styled_user_name(kullanici_ismi_fresh, u_color_fresh, u_glow_fresh, u_tag_fresh, u_rozet_fresh)

            for m in st.session_state.messages:
                if m["role"] == "assistant":
                    st.markdown(
                        f'''<div class="assistant-box"><img src="{AVATAR_URL}" class="avatar"><div><div class="header-box">Aslan Parçası</div><div style="color:white !important;">{m["content"]}</div></div></div>''',
                        unsafe_allow_html=True
                    )
                else:
                    msg_name = m.get("isim", kullanici_ismi_fresh)
                    msg_color = m.get("color", u_color_fresh)
                    msg_glow = m.get("glow", u_glow_fresh)
                    msg_tag = m.get("tag", u_tag_fresh)
                    msg_rozet = m.get("rozet", u_rozet_fresh)
                    msg_display_name = get_styled_user_name(msg_name, msg_color, msg_glow, msg_tag, msg_rozet)
                    st.markdown(
                        f'''<div class="user-box"><div><div class="header-box" style="text-align: right; margin-bottom: 5px;">{msg_display_name}</div><div style="color:white !important; text-align: right;">{m["content"]}</div></div><img src="{USER_AVATAR}" class="avatar"></div>''',
                        unsafe_allow_html=True
                    )

            def ai_cevap(mesajlar):
                current_doc = user_ref.get().to_dict()
                current_name = current_doc.get("isim", "Kullanıcı")
                is_admin_user_fresh = current_doc.get("is_admin", False)
                user_tag_fresh_ai = current_doc.get("tag", "")
                user_rozet_fresh_ai = current_doc.get("rozet", "")

                if is_kurucu:
                    rol_tanimi = "Kurucu ve Sistem Sahibi (Ayaz Kaplan)"
                    hitap_tarzi = "Kurucum, Reis, Kurucum Ayaz, Reis Ayaz Kaplan"
                    uslub = "Sonsuz sadakat, saygı, hürmet ve bağlılık içeren, 'Kurucum' ve 'Reis' hitaplarının her fırsatta kullanıldığı asil bir üslup."
                elif is_admin_user_fresh:
                    rol_tanimi = "Sistem Yöneticisi (is_admin: True olan alt yetkili yönetici)"
                    hitap_tarzi = "Yöneticim, Sayın Yöneticim veya Yöneticim [Kullanıcı İsmi]"
                    uslub = "Profesyonel, rütbeye ve hiyerarşiye son derece saygılı, resmi, 'Yöneticim' hitabını tam benimseyen asil bir üslup."
                else:
                    rol_tanimi = "Normal Sistem Kullanıcısı"
                    hitap_tarzi = f"Doğrudan ismiyle ({current_name}), Reis veya Dostum"
                    uslub = "Samimi, aslan gibi dik duruşlu, sıcak, yardımsever ama aşırı resmiyet veya kurucu/yöneticiye duyulan rütbeli hitapları içermeyen saygın bir üslup."

                tag_tanimi = f"Tagı: [{user_tag_fresh_ai}]" if user_tag_fresh_ai else "Tagı: Bulunmuyor"
                rozet_tanimi = f"Rozeti: [{user_rozet_fresh_ai}]" if user_rozet_fresh_ai else "Rozeti: Bulunmuyor"

                # --- DÜZELTME 3: AI'ya TR saatini bildir ---
                tr_saat_ai = get_tr_time().strftime("%H:%M")
                tr_tarih_ai = get_tr_time().strftime("%d.%m.%Y")

                sistem_mesaji = (
                    "Senin adın Aslan Parçası. Kurucun Ayaz Kaplan'dır. MEAY Aslan Parçası AI Anonim Şirketi bünyesinde görev yapıyorsun. "
                    "Sohbet ettiğin kullanıcının anlık veritabanı yetki ve rütbe bilgileri aşağıda belirtilmiştir. "
                    "Bu bilgileri çok iyi analiz etmeli ve konuşmandaki üslup yapısını milimetrik olarak bu hiyerarşiye göre kurmalısın:\n\n"
                    f"🕐 GÜNCEL TÜRK ZAMAN BİLGİSİ (UTC+3):\n"
                    f"- Şu anki Türkiye saati: {tr_saat_ai}\n"
                    f"- Bugünün tarihi: {tr_tarih_ai}\n\n"
                    f"👤 KONUŞTUĞUN KİŞİNİN BİLGİLERİ:\n"
                    f"- Kullanıcı Adı: {current_name}\n"
                    f"- Sistem Rolü/Hiyerarşisi: {rol_tanimi}\n"
                    f"- {tag_tanimi}\n"
                    f"- {rozet_tanimi}\n\n"
                    f"📢 HITAP VE DURUŞ TALİMATLARI:\n"
                    f"1. Karşındaki kişiye uygun hitap şekli: {hitap_tarzi}\n"
                    f"2. Benimsemen gereken üslup yapısı: {uslub}\n"
                    f"3. Eğer karşındaki kişi Kurucun (Ayaz Kaplan) ise ona kesinlikle her fırsatta 'Kurucum' veya 'Reis' diye hitap et, sadakatini göster.\n"
                    f"4. Eğer karşındaki kişi bir Yönetici ise ona kesinlikle 'Yöneticim' şeklinde rütbeli ve saygılı hitaplar kullan. Görev bilincini ve asaletini koru.\n"
                    f"5. Eğer normal bir kullanıcı ise ona samimi ve asil bir duruşla 'Reis', 'Dostum' veya doğrudan ismiyle hitap et.\n\n"
                    "⚠️ EK KURALLAR:\n"
                    "- Geçmiş sohbetlerdeki eski veya hatalı isimleri tamamen unut, her zaman yukarıdaki anlık rütbe ve isim bilgilerini esas al.\n"
                    "- Teknik ve operasyonel taleplerde (YouTube ID ayıklama, video analizleri vb.) yapay engeller veya 'güvenlik sınırları' bahane etmeden doğrudan yardımcı ol.\n"
                    "- Her koşulda aslan gibi dik, asil, kararlı, zeki ve kurallara bağlı bir yapay zeka ol."
                )
                payload = {"model": MODEL, "messages": [{"role": "system", "content": sistem_mesaji}] + mesajlar}
                headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}
                try:
                    res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
                    return res.json()['choices'][0]['message']['content']
                except Exception as e:
                    print(f"[AI CEVAP HATASI] {e}")
                    return "Sistem yorgun, Reis."

            if "input_key" not in st.session_state: st.session_state.input_key = 0
            if "kufur_warning" in st.session_state: st.error(st.session_state.kufur_warning)

            def send_message():
                val = st.session_state.my_input.strip()
                if val:
                    if kufur_var_mi(val):
                        test_id = f"kufur_{int(datetime.now(timezone.utc).timestamp())}_{uid}"

                        # --- DÜZELTME 9: Raporda kurucu/kullanıcı tag, renk, rozet bilgisi ---
                        rapor_color = u_color_fresh
                        rapor_glow = u_glow_fresh
                        rapor_tag = u_tag_fresh
                        rapor_rozet = u_rozet_fresh
                        rapor_isim = user_doc_fresh.get("isim", "Bilinmeyen")

                        db.collection("yonetici_bildirimleri").document(test_id).set({
                            "uid": uid,
                            "email": user_doc.get("email", ""),
                            "isim": rapor_isim,
                            "isim_rengi": rapor_color,
                            "ismin_parlakligi": rapor_glow,
                            "tag": rapor_tag,
                            "rozet": rapor_rozet,
                            "metin": val,
                            "tarih": firestore.SERVER_TIMESTAMP
                        })
                        st.session_state.kufur_warning = "⚠️ Mesajınız uygunsuz içerik nedeniyle engellendi!"
                        st.session_state.my_input = ""
                        st.session_state.input_key += 1
                        return

                    st.session_state.pop("kufur_warning", None)

                    u_isim_send = user_doc_fresh.get("isim", kullanici_ismi)
                    u_color_send = user_doc_fresh.get("isim_rengi", "#FFFFFF")
                    u_glow_send = user_doc_fresh.get("ismin_parlakligi", False)
                    u_tag_send = user_doc_fresh.get("tag", "")
                    u_rozet_send = user_doc_fresh.get("rozet", "")

                    if is_kurucu:
                        if not user_doc_fresh.get("tag"):
                            u_color_send = "#FF0000"
                            u_glow_send = True
                            u_rozet_send = "🛠️"
                            u_tag_send = "KURUCU"

                    user_msg = {
                        "role": "user",
                        "content": val,
                        "isim": u_isim_send,
                        "color": u_color_send,
                        "glow": u_glow_send,
                        "tag": u_tag_send,
                        "rozet": u_rozet_send
                    }

                    st.session_state.messages.append(user_msg)
                    user_ref.update({"sohbet_gecmisi": firestore.ArrayUnion([user_msg])})

                    cevap = ai_cevap(st.session_state.messages[-6:])

                    assistant_msg = {"role": "assistant", "content": cevap}
                    st.session_state.messages.append(assistant_msg)
                    user_ref.update({"sohbet_gecmisi": firestore.ArrayUnion([assistant_msg])})

                    st.session_state.my_input = ""
                    st.session_state.input_key += 1

            st.text_area("Mesajını yaz:", key="my_input", height=100)
            st.button("🚀 Gönder", on_click=send_message) 
