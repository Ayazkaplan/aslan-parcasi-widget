import streamlit as st
import requests
import os
import json
import firebase_admin
from firebase_admin import credentials, auth, firestore
import re
from datetime import datetime, timezone, timedelta
import time
import unicodedata

# --- SAYFA AYARLARI (Tüm Streamlit komutlarından önce ilk sırada olmalıdır) ---
st.set_page_config(page_title="Aslan Parçası V16.4", page_icon="🦁", layout="centered")

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

# --- YARDIMCI FONKSİYONLAR & KÜFÜR FİLTRESİ ---
def normalize_text(text):
    # Türkçe karakterleri İngilizceye çevir ve tüm işaretleri temizle
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    return re.sub(r'[^a-zA-Z0-9]', '', text.lower())

def kufur_var_mi(text):
    clean_text = normalize_text(text)
    # Global Ban List ve türevleri (Diğer dillerdeki küfürlerle birleştirilmiş)
    ban_list = [
        "amk", "aq", "orospu", "pic", "yavsak", "yavsaklik", "hiyar", "durzu", "dingil", "serefsiz", "fuck", "bitch",
        "asshole", "shit", "bastard", "cunt", "dick", "pussy", "motherfucker", "whore", "slut",
        "scheisse", "arschloch", "schlampe", "wichser", "hurensohn", "fotze",
        "kus", "kos", "rab", "sharmouta", "sharmuta", "kussak", "ayri", "khara", "sharmout",
        "puta", "puto", "cabron", "maricon", "merde"
    ]
    for word in ban_list:
        if word in clean_text:
            return True
    return False

# YouTube otomatik oynatma iframe oluşturucu
def get_video_iframe(video_id):
    # mute=0 yaptık, autoplay=0 ile kullanıcı başlatacak
    return f'''<iframe width="100%" height="150" src="https://www.youtube.com/embed/{video_id}?autoplay=0&mute=0" 
    frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'''

# Dinamik İsim Stili Oluşturucu (Görsel Sıralama Hatasını Düzeltir)
def get_styled_user_name(u_name, u_color, u_glow, u_tag, u_rozet):
    color_val = u_color if u_color else "#FFFFFF"
    
    # Güçlü neon gölge efekti
    glow_css = f"text-shadow: 0 0 10px {color_val}, 0 0 20px {color_val}, 0 0 30px {color_val};" if u_glow else ""
    
    # Sıralama: [TAG] [İSİM] [ROZET]
    tag_html = f'<span class="tag" style="color: {color_val}; font-weight: bold; {glow_css} font-size: 0.8rem; background-color: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 3px; margin-right: 5px;">[{u_tag}]</span>' if u_tag else ""
    isim_html = f'<span class="isim" style="color: {color_val}; font-weight: bold; {glow_css}">{u_name}</span>'
    rozet_html = f'<span class="rozet" style="margin-left: 5px;">{u_rozet}</span>' if u_rozet else ""
    
    parts = []
    if tag_html: parts.append(tag_html)
    parts.append(isim_html)
    if rozet_html: parts.append(rozet_html)
    
    return " ".join(parts)

# --- OTURUM YÖNETİMİ & KALICILIK ---
if "user_logged_in" not in st.session_state: st.session_state.user_logged_in = False
if "user_data" not in st.session_state: st.session_state.user_data = None
if "messages" not in st.session_state: st.session_state.messages = []
if "tema" not in st.session_state: st.session_state.tema = list(TEMALAR.values())[0]
if "valid_users_cache" not in st.session_state: st.session_state.valid_users_cache = None
if "current_page" not in st.session_state: st.session_state.current_page = "chat"
if "force_login" not in st.session_state: st.session_state.force_login = False

def set_login_state(uid):
    st.session_state.user_logged_in = True
    st.session_state.force_login = True # Oturumu mühürle
    st.query_params["session_uid"] = uid

def logout_user():
    st.session_state.force_login = False
    st.session_state.user_logged_in = False
    st.query_params.pop("session_uid", None)
    st.rerun()

# Kalıcı Oturum Desteği (Query Params ve Force Login Kontrolü)
if (not st.session_state.user_logged_in or not st.session_state.force_login) and "session_uid" in st.query_params:
    stored_uid = st.query_params["session_uid"]
    try:
        user_ref_temp = db.collection("users").document(stored_uid)
        # Giriş yapıldığında son görülmeyi anlık güncelle
        user_ref_temp.update({"son_gorulme_zamani": firestore.SERVER_TIMESTAMP})
        
        user_snap = user_ref_temp.get()
        if user_snap.exists:
            user_data = user_snap.to_dict()
            user_durum = user_data.get("durum", "Aktif")
            ban_bitis = user_data.get("ban_bitis_zamani")
            
            is_banned = False
            if user_durum == "Pasif":
                if ban_bitis:
                    if ban_bitis.tzinfo is None:
                        ban_bitis = ban_bitis.replace(tzinfo=timezone.utc)
                    now = datetime.now(timezone.utc)
                    if now < ban_bitis:
                        is_banned = True
                else:
                    is_banned = True
            
            if not is_banned:
                st.session_state.user_data = {**user_data, "uid": stored_uid}
                set_login_state(stored_uid)
                st.session_state.tema = user_data.get("tema", list(TEMALAR.values())[0])
                
                # Kalıcı Sohbet: Veritabanındaki sohbet_gecmisi alanından aktif mesajları çekiyoruz
                sohbet_list = user_data.get("sohbet_gecmisi", [])
                if isinstance(sohbet_list, list):
                    active_messages = []
                    last_separator_idx = -1
                    for idx, msg in enumerate(sohbet_list):
                        if msg.get("role") == "separator":
                            last_separator_idx = idx
                    if last_separator_idx != -1:
                        active_messages = sohbet_list[last_separator_idx + 1:]
                    else:
                        active_messages = [m for m in sohbet_list if m.get("role") in ["user", "assistant"]]
                    st.session_state.messages = active_messages
                else:
                    st.session_state.messages = []
            else:
                # Kullanıcı banlıysa kalıcı oturum parametrelerini sil
                st.session_state.force_login = False
                st.query_params.pop("session_uid", None)
    except Exception:
        pass

# --- ŞİFRE KONTROLÜ (GÜVENLİ REST API GİRİŞİ) ---
def firebase_login(email, password):
    try:
        # Firebase REST API kullanarak giriş yapma
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
        payload = {"email": email, "password": password, "returnSecureToken": True}
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        return None

# --- EMOJİ KONTROLÜ ---
def emoji_var_mi(text):
    return bool(re.search(r'[^\w\s,.]', text))

# --- GİRİŞ VE KAYIT EKRANI ---
# Her sayfa başında force_login durumunu kontrol et:
if not st.session_state.user_logged_in or not st.session_state.force_login:
    st.title("🦁 Aslan Parçası V16.4")
    
    # Force Logout sonrasında kalan süreyi veya ban hatasını gösterme
    if "ban_error_on_logout" in st.session_state:
        st.error(st.session_state.ban_error_on_logout)
    
    email = st.text_input("📧 E-posta:")
    password = st.text_input("🔑 Şifre:", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Giriş Yap"):
            st.session_state.pop("ban_error_on_logout", None) # Yeni giriş denemesinde eski hatayı temizle
            clean_email = email.strip().lower()
            auth_res = firebase_login(clean_email, password)
            if auth_res:
                users_ref = db.collection("users")
                query = users_ref.where("email", "==", clean_email).limit(1).get()
                if query:
                    user_data = query[0].to_dict()
                    user_durum = user_data.get("durum", "Aktif")
                    ban_bitis = user_data.get("ban_bitis_zamani")
                    
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
                                # Süre dolmuşsa banı otomatik kaldır ve girişe izin ver
                                db.collection("users").document(query[0].id).update({
                                    "durum": "Aktif",
                                    "ban_bitis_zamani": None
                                })
                                # E-posta kilit kaydını da sil
                                db.collection("banlanan_emails").document(clean_email).delete()
                                user_data["durum"] = "Aktif"
                                user_data["ban_bitis_zamani"] = None
                        else:
                            is_banned = True
                            st.error("❌ Hesabınız pasifleştirilmiştir. Giriş yapamazsınız!")
                    
                    if not is_banned:
                        # Giriş yapıldığında son görülme zamanını anlık güncelle
                        db.collection("users").document(query[0].id).update({
                            "son_gorulme_zamani": firestore.SERVER_TIMESTAMP
                        })
                        
                        st.session_state.user_data = {**user_data, "uid": auth_res['localId']}
                        set_login_state(auth_res['localId'])
                        st.session_state.tema = user_data.get("tema", list(TEMALAR.values())[0])
                        
                        # Kalıcı Sohbet: Veritabanındaki sohbet_gecmisi alanından aktif mesajları çekiyoruz
                        sohbet_list = user_data.get("sohbet_gecmisi", [])
                        if isinstance(sohbet_list, list):
                            active_messages = []
                            last_separator_idx = -1
                            for idx, msg in enumerate(sohbet_list):
                                if msg.get("role") == "separator":
                                    last_separator_idx = idx
                            if last_separator_idx != -1:
                                active_messages = sohbet_list[last_separator_idx + 1:]
                            else:
                                active_messages = [m for m in sohbet_list if m.get("role") in ["user", "assistant"]]
                            st.session_state.messages = active_messages
                        else:
                            st.session_state.messages = []
                            
                        st.rerun()
                else: st.error("❌ Kullanıcı verisi bulunamadı!")
            else: st.error("❌ E-posta veya şifre yanlış!")
            
    with col2:
        isim_input = st.text_input("👤 Kayıt İçin İsim:", max_chars=25)
        if st.button("Kayıt Ol"):
            st.session_state.pop("ban_error_on_logout", None)
            try:
                clean_email = email.strip().lower()
                
                # Sıkı Ban Sistemi (E-posta Kilidi) Kontrolü
                ban_doc = db.collection("banlanan_emails").document(clean_email).get()
                if ban_doc.exists:
                    ban_data = ban_doc.to_dict()
                    ban_bitis = ban_data.get("ban_bitis_zamani")
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
                            # Süre dolmuşsa kilidi kaldır
                            db.collection("banlanan_emails").document(clean_email).delete()
                    else:
                        st.error("❌ Bu e-posta adresi süresiz olarak banlandığı için kullanılamaz!")
                        st.stop()

                user = auth.create_user(email=clean_email, password=password)
                db.collection("users").document(user.uid).set({
                    "isim": isim_input, 
                    "email": clean_email, 
                    "videos": [], 
                    "tema": list(TEMALAR.values())[0],
                    "durum": "Aktif",
                    "gizli_bilgi": password,
                    "ban_bitis_zamani": None,
                    "sohbet_gecmisi": [],
                    "son_gorulme_zamani": None,
                    "okunmamis_duyurular": [],
                    "is_admin": False,
                    "tag": "",
                    "rozet": "",
                    "isim_rengi": "#FFFFFF",
                    "ismin_parlakligi": False
                })
                st.success("✅ Kayıt başarılı! Giriş yapabilirsin.")
            except Exception as e: st.error(f"❌ Hata: {e}")
            
    st.divider()
    if st.button("🔑 Şifremi Unuttum"):
        if email:
            try:
                reset_link = auth.generate_password_reset_link(email.strip().lower())
                st.success("✅ Şifre sıfırlama bağlantınız oluşturuldu!")
                st.info(f"Link: {reset_link}")
            except Exception as e: st.error(f"❌ Link oluşturulamadı: {e}")
        else: st.warning("Lütfen önce e-posta girin.")
    st.stop()

# --- ANA EKRAN AYARLARI ---
uid = st.session_state.user_data['uid']
user_ref = db.collection("users").document(uid)

# Son Görülme Kaydı: Her sayfa yenilemesinde veya işlem yapıldığında son görülme zamanını anlık SERVER_TIMESTAMP yap
try:
    user_ref.update({"son_gorulme_zamani": firestore.SERVER_TIMESTAMP})
except Exception:
    pass

user_snap = user_ref.get()

# Veritabanında kullanıcı yoksa oturumu temizle
if not user_snap.exists:
    st.query_params.pop("session_uid", None) # Tarayıcı oturum kalıcılık parametresini kaldır
    st.error("❌ Hesabınız silinmiş veya bulunamadı!")
    st.session_state.clear()
    st.rerun()

user_doc = user_snap.to_dict()

# Anlık Ban Kontrolü (Force Logout)
user_durum = user_doc.get("durum", "Aktif")
ban_bitis = user_doc.get("ban_bitis_zamani")

if user_durum == "Pasif":
    is_banned = False
    ban_hata_mesaji = ""
    if ban_bitis:
        if ban_bitis.tzinfo is None:
            ban_bitis = ban_bitis.replace(tzinfo=timezone.utc)
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
            # Süre dolmuşsa aktif hale getir
            db.collection("users").document(uid).update({
                "durum": "Aktif",
                "ban_bitis_zamani": None
            })
            # E-posta kilidini kaldır
            u_email = user_doc.get("email", "").strip().lower()
            db.collection("banlanan_emails").document(u_email).delete()
            user_doc["durum"] = "Aktif"
            user_doc["ban_bitis_zamani"] = None
            st.rerun()
    else:
        is_banned = True
        ban_hata_mesaji = "❌ Hesabınız yönetici tarafından pasif duruma getirilmiştir!"

if user_durum == "Pasif" and is_banned:
    st.session_state.user_logged_in = False
    st.session_state.user_data = None
    st.session_state.ban_error_on_logout = ban_hata_mesaji
    logout_user()

# Kalıcı Sohbet: Veritabanından aktif mesajları çekme
sohbet_list = user_doc.get("sohbet_gecmisi", [])
if isinstance(sohbet_list, list):
    active_messages = []
    last_separator_idx = -1
    for idx, msg in enumerate(sohbet_list):
        if msg.get("role") == "separator":
            last_separator_idx = idx
    if last_separator_idx != -1:
        active_messages = sohbet_list[last_separator_idx + 1:]
    else:
        active_messages = [m for m in sohbet_list if m.get("role") in ["user", "assistant"]]
    st.session_state.messages = active_messages
else:
    st.session_state.messages = []

# Güncel temayı veritabanından tazele
st.session_state.tema = user_doc.get("tema", list(TEMALAR.values())[0])

is_kurucu = user_doc.get('email') == KURUCU_EMAIL
is_admin_user = user_doc.get("is_admin", False)
saved_videos = user_doc.get("videos", [])
kullanici_ismi = user_doc.get('isim')

# --- YETKİ KISITLAMALARI VE GÜVENLİK KONTROLLERİ ---
if st.session_state.current_page in ["admin_main", "admin_users", "admin_role_management"] and not is_kurucu:
    st.session_state.current_page = "chat"
    st.rerun()

if st.session_state.current_page == "admin_announcement" and not (is_kurucu or is_admin_user):
    st.session_state.current_page = "chat"
    st.rerun()

# --- SİDEBAR PROFİL GÖRÜNÜMÜ DETAYLARI ---
# Sol sidebar profil görünümünü de sohbetteki gibi dinamik, parlayan ve tag-rozetli yapma
u_color = user_doc.get("isim_rengi", "#FFFFFF")
u_glow = user_doc.get("ismin_parlakligi", False)
u_tag = user_doc.get("tag", "")
u_rozet = user_doc.get("rozet", "")

if is_kurucu:
    if "isim_rengi" not in user_doc or not user_doc.get("isim_rengi"):
        u_color = "#FF0000"
        u_glow = True
    if "rozet" not in user_doc or not user_doc.get("rozet"):
        u_rozet = "🛠️"
    if "tag" not in user_doc or not user_doc.get("tag"):
        u_tag = "KURUCU"

isim_stili = get_styled_user_name(kullanici_ismi, u_color, u_glow, u_tag, u_rozet)

# --- SİDEBAR & PROFİL DÜZENLEME ---
with st.sidebar:
    st.markdown("### 👤 Profil Ayarları")
    yeni_isim = st.text_input("Yeni İsim:", value=kullanici_ismi, max_chars=25)
    
    if st.button("İsmi Güncelle"):
        if not is_kurucu and emoji_var_mi(yeni_isim):
            st.warning("⚠️ İsminizde emoji kullanamazsınız.")
        else:
            user_ref.update({"isim": yeni_isim})
            st.session_state.valid_users_cache = None  # Önbelleği temizle
            st.success("✅ İsim güncellendi!")
            st.rerun()
            
    # Dinamik, renkli, parlayan tag ve rozetli profil gösterimi
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
    
    # Sohbeti Arşivleyerek Temizleme Özelliği
    if st.button("🧹 Sohbeti Temizle"):
        user_ref.update({"sohbet_gecmisi": []})
        st.session_state.messages = []
        st.success("Sohbet başarıyla temizlendi!")
        st.rerun()
        
    if st.button("🚪 Çıkış Yap"): 
        logout_user() # Kilidi açan tek çıkış butonu
    
    # Hesabımı Sil Arayüzü (2 Aşamalı Onay)
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
                    u_email = user_doc.get("email", "").strip().lower()
                    db.collection("banlanan_emails").document(u_email).delete()
                    logout_user()
                except Exception as e:
                    st.error(f"Hata: {e}")
        with col_self_del_no:
            if st.button("Vazgeç", key="confirm_delete_self_no", use_container_width=True):
                st.session_state.confirm_delete_self = False
                st.rerun()
    
    st.divider()
    yeni_video = st.text_input("YouTube ID ekle:")
    if st.button("💾 Kaydet"):
        if yeni_video and yeni_video not in saved_videos:
            user_ref.update({"videos": firestore.ArrayUnion([yeni_video])})
            st.rerun()
    
    # Video Hafızası (Autoplay, Mute ve get_video_iframe fonksiyonu entegrasyonu)
    for v in saved_videos:
        c1, c2 = st.columns([0.8, 0.2])
        c1.markdown(get_video_iframe(v), unsafe_allow_html=True)
        if c2.button("🗑️", key=v):
            user_ref.update({"videos": firestore.ArrayRemove([v])})
            st.rerun()

    # Sidebar yönlendirme menüsü
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

# --- STYLE VE SOHBET (CSS Taşma Çözümü) ---
st.markdown(f"""<style>
    .assistant-box {{ 
        background-color: rgba(30,30,30,0.8); 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 5px solid gold; 
        margin-bottom: 15px; 
        display: flex; 
        align-items: flex-start; 
        gap: 10px; 
        color: white; 
        word-wrap: break-word !important; 
        overflow-wrap: break-word !important; 
        word-break: break-word !important;
        max-width: 100% !important; 
    }}
    .user-box {{ 
        background-color: rgba(255,255,255,0.1); 
        padding: 15px; 
        border-radius: 10px; 
        margin-bottom: 15px; 
        display: flex; 
        justify-content: flex-end; 
        align-items: flex-start; 
        gap: 10px; 
        color: white; 
        word-wrap: break-word !important; 
        overflow-wrap: break-word !important; 
        word-break: break-word !important;
        max-width: 100% !important; 
    }}
    .assistant-box *, .user-box * {{
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        word-break: break-word !important;
        max-width: 100% !important;
    }}
    .avatar {{ width: 40px; height: 40px; border-radius: 50%; }}
    .header-box {{ font-weight: bold; margin-bottom: 5px; }}
</style>""", unsafe_allow_html=True)

# --- SİNK & OTOMATİK ARINDIRMA FONKSİYONU ---
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
            
            user_info = {
                "doc": doc,
                "data": u_data,
                "id": u_id,
                "email": u_email,
                "update_time": update_time
            }
            
            if u_email not in email_to_docs:
                email_to_docs[u_email] = []
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
                if users_list:
                    valid_users.append(users_list[0])
                    
        toplam_temizlenen = temizlenen_ghost + temizlenen_duplicate
        if toplam_temizlenen > 0:
            st.toast(f"🧹 Otomatik Arındırma: {temizlenen_ghost} hayalet, {temizlenen_duplicate} mükerrer kayıt temizlendi!")
            
        return valid_users

# --- SAYFA DİNAMİK YÖNLENDİRME BLOKLARI ---

if st.session_state.current_page == "admin_main" and is_kurucu:
    # --- YÖNETİCİ ANA PANEL MENÜSÜ ---
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
    # --- ALT SAYFA: KULLANICI YÖNETİMİ ---
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
    
    # Yönetici Paneli Sekmeleri
    tab_kullanicilar, tab_bildirimler = st.tabs([
        "👥 Kullanıcılar", 
        "⚠️ Yönetici Bildirimleri (Küfür Raporları)"
    ])
    
    with tab_kullanicilar:
        arama_query = st.text_input("🔍 E-posta ile Ara (Tam Eşleşme):").strip().lower()
        
        try:
            if st.session_state.valid_users_cache is None:
                st.session_state.valid_users_cache = otomatik_arindir_ve_grup()
                
            valid_users = st.session_state.valid_users_cache
            
            if arama_query:
                filtered_users = [u for u in valid_users if u["email"] == arama_query]
            else:
                filtered_users = valid_users
                
            st.markdown(f"Toplam **{len(filtered_users)}** kayıtlı kullanıcı listeleniyor.")
            
            for item in filtered_users:
                u_data = item["data"]
                u_id = item["id"]
                u_email = item["email"]
                u_isim = u_data.get("isim", "Bilinmiyor")
                u_durum = u_data.get("durum", "Aktif")
                u_sifre = u_data.get("gizli_bilgi", "Mevcut Değil (Eski Kayıt)")
                u_ban_bitis = u_data.get("ban_bitis_zamani")
                u_sohbet_gecmisi = u_data.get("sohbet_gecmisi", [])
                u_son_gorulme = u_data.get("son_gorulme_zamani")
                
                if u_email == KURUCU_EMAIL:
                    continue
                    
                # Çevrimiçi / Çevrimdışı Mantığı & Son Görülme Süresi Farkı Hesaplama
                is_online = False
                son_gorulme_str = ""
                if u_son_gorulme:
                    if u_son_gorulme.tzinfo is None:
                        u_son_gorulme = u_son_gorulme.replace(tzinfo=timezone.utc)
                    now = datetime.now(timezone.utc)
                    diff = now - u_son_gorulme
                    
                    total_seconds = int(diff.total_seconds())
                    if total_seconds < 0:
                        total_seconds = 0
                    
                    if total_seconds <= 300: # 5 dakika (5 * 60)
                        is_online = True
                    else:
                        is_online = False
                        days = total_seconds // 86400
                        hours = (total_seconds % 86400) // 3600
                        minutes = (total_seconds % 3600) // 60
                        
                        parts = []
                        if days > 0:
                            parts.append(f"{days} gün")
                        if hours > 0:
                            parts.append(f"{hours} saat")
                        if minutes > 0 or not parts:
                            parts.append(f"{minutes} dakika")
                        
                        son_gorulme_str = "Son görülme: " + ", ".join(parts) + " önce"
                else:
                    son_gorulme_str = "Son görülme: Bilinmiyor"
                    
                with st.container(border=True):
                    col_info, col_sec, col_act = st.columns([4, 3, 3])
                    
                    with col_info:
                        st.markdown(f"### 👤 {u_isim}")
                        st.markdown(f"📧 **E-posta:** `{u_email}`")
                        
                        # Çevrimiçi/Çevrimdışı Durumu Gösterimi
                        if is_online:
                            st.markdown("🟢 **Çevrimiçi**")
                        else:
                            st.markdown("🔴 **Çevrimdışı**")
                            st.markdown(f"_<span style='font-size:0.85rem; color:#888;'>{son_gorulme_str}</span>_", unsafe_allow_html=True)
                        
                        st.markdown("---")
                        
                        if u_durum == "Pasif":
                            if u_ban_bitis:
                                if u_ban_bitis.tzinfo is None:
                                    u_ban_bitis = u_ban_bitis.replace(tzinfo=timezone.utc)
                                now = datetime.now(timezone.utc)
                                if now < u_ban_bitis:
                                    kalan = u_ban_bitis - now
                                    dk = int(kalan.total_seconds() / 60)
                                    if dk < 1:
                                        st.markdown(f"📌 **Durum:** 🔴 Pasif (Kalan: {int(kalan.total_seconds())} sn)")
                                    else:
                                        st.markdown(f"📌 **Durum:** 🔴 Pasif (Kalan: {dk} dk)")
                                else:
                                    st.markdown("📌 **Durum:** 🟢 Pasif (Süre Doldu, İlk Girişte Aktifleşecek)")
                            else:
                                st.markdown("📌 **Durum:** 🔴 Pasif (Süresiz)")
                        else:
                            st.markdown("📌 **Durum:** 🟢 Aktif")
                        
                        # Yönetici Panelinde Sınırlı Sohbet Geçmişi İzleme (Otomatik 10 Mesaj Sınırı)
                        if isinstance(u_sohbet_gecmisi, list) and u_sohbet_gecmisi:
                            gosterilecek_mesajlar = u_sohbet_gecmisi[-10:] # Sadece son 10 mesaj
                            formatted_lines = []
                            for msg in gosterilecek_mesajlar:
                                role = msg.get("role")
                                content = msg.get("content", "")
                                if role == "separator":
                                    formatted_lines.append(f"\n{content}\n")
                                elif role == "user":
                                    formatted_lines.append(f"[Kullanıcı]: {content}")
                                elif role == "assistant":
                                    formatted_lines.append(f"[Aslan Parçası]: {content}")
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
                        st.markdown(f"**Şifre (Gizli):** `{u_sifre}`")
                        st.markdown(f"**UID:** `{u_id}`")
                        
                    with col_act:
                        st.write("") 
                        
                        # Zaman Ayarlı Pasifleştirme (Ban) ve Aktifleştirme Arayüzü
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
                                        db.collection("users").document(u_id).update({
                                            "durum": "Pasif",
                                            "ban_bitis_zamani": ban_bitis_zamani
                                        })
                                        # Sıkı ban sistemi için kilitleme tablosuna e-posta ekle
                                        db.collection("banlanan_emails").document(u_email).set({
                                            "ban_bitis_zamani": ban_bitis_zamani,
                                            "email": u_email
                                        })
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
                                db.collection("users").document(u_id).update({
                                    "durum": "Aktif",
                                    "ban_bitis_zamani": None
                                })
                                # E-posta kilit kaydını da kaldır
                                db.collection("banlanan_emails").document(u_email).delete()
                                st.session_state.valid_users_cache = None
                                st.success("Hesap aktifleştirildi.")
                                st.rerun()
                            
                        # 2 Aşamalı Yönetici Silme Butonu
                        show_del_confirm = st.session_state.get(f"show_del_confirm_{u_id}", False)
                        if not show_del_confirm:
                            if st.button("🗑️ Sil", key=f"del_{u_id}", type="primary", use_container_width=True):
                                st.session_state[f"show_del_confirm_{u_id}"] = True
                                st.rerun()
                        else:
                            st.warning("⚠️ Emin misiniz?")
                            col_del_yes, col_del_no = st.columns(2)
                            with col_del_yes:
                                if st.button("Evet, Kalıcı Olarak Sil", key=f"confirm_del_yes_{u_id}", type="primary", use_container_width=True):
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
        st.write("Sistem tarafından tespit edilip engellenen küfürlü mesajların kayıtları aşağıda listelenmiştir.")
        
        try:
            bildirimler = db.collection("yonetici_bildirimleri").order_by("tarih", direction=firestore.Query.DESCENDING).get()
            
            # TEK TUŞLA TOPLU TEMİZLEME ALANI
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
                    
                    tarih_str = ""
                    if b_tarih:
                        if b_tarih.tzinfo is None:
                            b_tarih = b_tarih.replace(tzinfo=timezone.utc)
                        tarih_str = b_tarih.strftime("%Y-%m-%d %H:%M:%S")
                    
                    with st.container(border=True):
                        col_rep_info, col_rep_btn = st.columns([8, 2])
                        with col_rep_info:
                            st.markdown(f"👤 **Kullanıcı:** {b_isim} (`{b_email}`)")
                            st.markdown(f"📅 **Tarih:** `{tarih_str}`")
                            st.error(f"💬 **Engellenen Küfürlü Mesaj:** {b_mesaj}")
                        with col_rep_btn:
                            st.write("") # Hizalama boşluğu
                            if st.button("🗑️ Raporu Sil", key=f"clear_rep_{b_id}", use_container_width=True):
                                db.collection("yonetici_bildirimleri").document(b_id).delete()
                                st.success("Rapor silindi.")
                                st.rerun()
            else:
                st.info("Harika! Henüz bildirilmiş küfürlü mesaj bulunmuyor.")
        except Exception as e:
            st.error(f"Bildirimler alınamadı: {e}")

elif st.session_state.current_page == "admin_announcement" and (is_kurucu or is_admin_user):
    # --- ALT SAYFA: DUYURU VE BİLGİLENDİRME GÖNDERİMİ (Sadece Kurucu ve Yöneticiler Girebilir) ---
    st.title("📣 Duyuru ve Bilgilendirme Sayfası")
    
    col_back_main, col_back_chat = st.columns([5, 5])
    with col_back_main:
        if is_kurucu:
            if st.button("⬅️ Yönetici Ana Paneline Dön", key="back_to_main_from_ann", use_container_width=True):
                st.session_state.current_page = "admin_main"
                st.rerun()
        else:
            st.info("Sadece duyuru gönderme yetkiniz bulunmaktadır.")
    with col_back_chat:
        if st.button("💬 Sohbet Ekranına Dön", key="back_to_chat_from_ann", use_container_width=True):
            st.session_state.current_page = "chat"
            st.rerun()
            
    st.divider()
    
    st.markdown("### 📣 Kullanıcılara Duyuru Gönder")
    st.write("Sistemdeki tüm kullanıcılara veya el ile yazacağınız belirli bir e-posta adresine anlık duyuru gönderebilirsiniz.")
    
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
            duyuru_id = f"announcement_{int(datetime.now(timezone.utc).timestamp())}"
            duyuru_payload = {
                "id": duyuru_id,
                "metin": duyuru_metni.strip(),
                "tarih": firestore.SERVER_TIMESTAMP,
                "hedef": "Tümü" if hedef_tipi == "Tüm Kullanıcılar" else secilen_email,
                "gonderen_email": user_doc.get("email", ""), # Loglama için eklenen alanlar
                "gonderen_isim": user_doc.get("isim", "Bilinmeyen")
            }
            
            # Küresel duyurular koleksiyonuna yaz
            db.collection("duyurular").document(duyuru_id).set(duyuru_payload)
            pushed_announcement = {"id": duyuru_id, "metin": duyuru_metni.strip()}
            
            # Veritabanı sorgusuyla kullanıcıları tarıyoruz
            all_users_snap = db.collection("users").get()
            
            if hedef_tipi == "Tüm Kullanıcılar":
                batch = db.batch()
                for u_doc_item in all_users_snap:
                    u_data = u_doc_item.to_dict()
                    if u_data.get("email", "").strip().lower() != KURUCU_EMAIL:
                        batch.update(u_doc_item.reference, {
                            "okunmamis_duyurular": firestore.ArrayUnion([pushed_announcement])
                        })
                batch.commit()
                st.success("Duyuru tüm kullanıcılara başarıyla yayınlandı!")
            else:
                target_found = False
                for u_doc_item in all_users_snap:
                    u_data = u_doc_item.to_dict()
                    if u_data.get("email", "").strip().lower() == secilen_email:
                        u_doc_item.reference.update({
                            "okunmamis_duyurular": firestore.ArrayUnion([pushed_announcement])
                        })
                        target_found = True
                        break
                if target_found:
                    st.success(f"Duyuru başarıyla {secilen_email} adresine iletildi!")
                else:
                    st.error("Yazılan e-posta adresiyle eşleşen bir kullanıcı bulunamadı.")
            
            st.session_state.valid_users_cache = None
            time.sleep(1)
            st.rerun()

elif st.session_state.current_page == "admin_role_management" and is_kurucu:
    # --- ALT SAYFA: YÖNETİCİ YÖNETİM SAYFASI (Yalnızca Kurucu Girebilir) ---
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
    
    # --- KURUCU KENDİ PROFİLİNİ DÜZENLEME PANELİ (Sadece Kurucuya Görünür) ---
    with st.expander("👑 Kendi Profil Stilimi Düzenle", expanded=False):
        st.markdown("### 👑 Kendi Profil Stilimi Düzenle")
        st.write("Buradan sohbette ve yan menüde görünecek olan size özel renk, parlaklık, tag ve rozet ayarlarını belirleyebilirsiniz.")
        
        f_color = st.color_picker("Kendi İsim Renginiz (Hex):", value=user_doc.get("isim_rengi", "#FF0000"))
        f_glow = st.checkbox("Kendi Yazı Parlaklığınız (Neon Efekti):", value=user_doc.get("ismin_parlakligi", True))
        f_tag = st.text_input("Kendi Tagınız (Örn: KURUCU, REİS):", value=user_doc.get("tag", "KURUCU"), max_chars=20)
        f_rozet = st.text_input("Kendi Rozetiniz (Örn: 🛠️, 👑):", value=user_doc.get("rozet", "🛠️"), max_chars=10)
        
        if st.button("💾 Kendi Stilimi Kaydet", type="primary", use_container_width=True):
            user_ref.update({
                "isim_rengi": f_color,
                "ismin_parlakligi": f_glow,
                "tag": f_tag.strip(),
                "rozet": f_rozet.strip()
            })
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
            
            # Form Alanları (Salt Okunur Değerler ve Değiştirilebilir Özellikler)
            st.text_input("Kullanıcı İsmi (Salt Okunur):", value=target_data.get("isim", "Bilinmeyen"), disabled=True)
            st.text_input("Kullanıcı E-postası (Salt Okunur):", value=target_data.get("email", ""), disabled=True)
            
            isim_rengi = st.color_picker("İsim Rengi (Hex):", value=target_data.get("isim_rengi", "#FFFFFF"))
            ismin_parlakligi = st.checkbox("Yazı Parlaklığı (CSS Gölge Efekti):", value=target_data.get("ismin_parlakligi", False))
            tag_val = st.text_input("Kullanıcı Tagı (Örn: Moderatör, Vip):", value=target_data.get("tag", ""), max_chars=20)
            rozet_val = st.text_input("Kullanıcı Rozeti (Örn: 🛡️, 💎):", value=target_data.get("rozet", ""), max_chars=10)
            is_admin_flag = st.checkbox("Yönetici Yap (is_admin):", value=target_data.get("is_admin", False))
            
            if st.button("💾 Değişiklikleri Kaydet", type="primary", use_container_width=True):
                db.collection("users").document(target_id).update({
                    "isim_rengi": isim_rengi,
                    "ismin_parlakligi": ismin_parlakligi,
                    "tag": tag_val.strip(),
                    "rozet": rozet_val.strip(),
                    "is_admin": is_admin_flag
                })
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
        # Kurucu dışındaki tüm alt yöneticileri filtrele
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
                        # 2 Aşamalı Onay Mekanizmasıyla Yöneticilikten Çıkarma
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
                                    db.collection("users").document(a_id).update({
                                        "is_admin": False
                                    })
                                    st.session_state[f"show_demote_{a_id}"] = False
                                    st.success(f"✅ {a_name} yöneticilikten çıkarıldı.")
                                    st.session_state.valid_users_cache = None
                                    time.sleep(1)
                                    st.rerun()
                            with c_n:
                                if st.button("Hayır", key=f"demote_no_{a_id}", use_container_width=True):
                                    st.session_state[f"show_demote_{a_id}"] = False
                                    st.rerun()
                    
                    # --- YÖNETİCİ DUYURU GEÇMİŞİ LOGLAMA ALANI ---
                    # Hata vermemesi ve firebase indeks gerektirmemesi için tüm duyuruları çekip Python tarafında bellek içi filtreleme-sıralama yapıyoruz
                    try:
                        admin_duyurulari = db.collection("duyurular").where("gonderen_email", "==", a_email).get()
                        
                        # Tarih alanına göre azalan (kronolojik) sıralama fonksiyonu
                        def get_tarih_val(doc):
                            t = doc.to_dict().get("tarih")
                            if t is None:
                                return datetime.min.replace(tzinfo=timezone.utc)
                            if t.tzinfo is None:
                                t = t.replace(tzinfo=timezone.utc)
                            return t
                        
                        sorted_duyurular = sorted(admin_duyurulari, key=get_tarih_val, reverse=True)
                        
                        with st.expander("📋 Yapılan Duyuru Geçmişi"):
                            if sorted_duyurular:
                                for d_doc in sorted_duyurular:
                                    d_data = d_doc.to_dict()
                                    d_metin = d_data.get("metin", "")
                                    d_hedef = d_data.get("hedef", "Tümü")
                                    d_tarih = d_data.get("tarih")
                                    
                                    tarih_formatted = ""
                                    if d_tarih:
                                        if d_tarih.tzinfo is None:
                                            d_tarih = d_tarih.replace(tzinfo=timezone.utc)
                                        tarih_formatted = d_tarih.strftime("%Y-%m-%d %H:%M:%S")
                                        
                                    st.markdown(f"**📅 Tarih:** `{tarih_formatted}` | **🎯 Hedef:** `{d_hedef}`")
                                    st.info(d_metin)
                                    st.write("---")
                            else:
                                st.caption("Bu yönetici henüz herhangi bir duyuru yayınlamadı.")
                    except Exception as e:
                        st.caption(f"Duyuru geçmişi yüklenirken hata oluştu: {e}")
                        
        else:
            st.error("❌ Eşleşen bir kullanıcı bulunamadı.")
            
    except Exception as e:
        st.error(f"Yöneticiler yüklenirken hata oluştu: {e}")

else:
    # --- YÖNETİCİ PANELİ (Sadece Kurucuya Özel - Expander Korundu) ---
    if is_kurucu:
        with st.expander("🛠️ YÖNETİCİ PANELİ (Kurucu Özel)"):
            st.write("Kurucu paneline hoş geldiniz, Reis.")
            st.info("Kullanıcıların detaylı listesine ulaşmak, arama yapmak ve şifreleri incelemek için aşağıdaki butona tıklayabilirsiniz.")
            if st.button("👥 Kullanıcı Yönetim Sayfasını Aç", key="open_admin_page", use_container_width=True):
                st.session_state.current_page = "admin_main"
                st.rerun()

    # --- KULLANICI EKRANINDA DUYURU GÖSTERİMİ VE SİLİNMESİ ---
    if st.session_state.current_page == "chat":
        okunmamis = user_doc.get("okunmamis_duyurular", [])
        if isinstance(okunmamis, list) and okunmamis:
            duyuru_obj = okunmamis[0]
            d_metin = duyuru_obj.get("metin", "")
            
            # Üst kısımda duyuruyu 5 saniye göstermek için dinamik container oluşturma
            announcement_placeholder = st.empty()
            with announcement_placeholder.container():
                st.markdown(f"""
                <div style="background-color: rgba(255, 0, 0, 0.12); border-left: 5px solid red; padding: 15px; border-radius: 5px; margin-bottom: 20px; box-shadow: 0 0 10px rgba(255, 0, 0, 0.7);">
                    <strong style="color: #ff3333; text-shadow: 0 0 8px rgba(255, 51, 51, 0.7); font-size: 1.15rem;">
                        AyazREİS_DEV 🛠️:
                    </strong> 
                    <span style="color: white; font-size: 1.1rem; margin-left: 5px; line-height: 1.4;">{d_metin}</span>
                </div>
                """, unsafe_allow_html=True)
            
            # 5 Saniye bekle
            time.sleep(5)
            
            # Veritabanındaki listeden bu duyuruyu çıkar
            user_ref.update({
                "okunmamis_duyurular": firestore.ArrayRemove([duyuru_obj])
            })
            
            # Container'ı temizle ve sayfayı tazeleyerek arayüzü sıfırla
            announcement_placeholder.empty()
            st.rerun()

    # --- SOHBET ARAYÜZÜ ---
    st.title("🤖 Aslan Parçası V16.4")

    # Veritabanından en güncel ismi çek
    user_doc_fresh = user_ref.get().to_dict()
    kullanici_ismi_fresh = user_doc_fresh.get('isim', kullanici_ismi)

    # Sohbet Ekranında İsimlerin HTML/CSS Çıktısı (Visual Sıralama ve Tasarım Onarımı)
    u_color_fresh = user_doc_fresh.get("isim_rengi", "#FFFFFF")
    u_glow_fresh = user_doc_fresh.get("ismin_parlakligi", False)
    u_tag_fresh = user_doc_fresh.get("tag", "")
    u_rozet_fresh = user_doc_fresh.get("rozet", "")

    if is_kurucu:
        # Kurucunun varsayılan tasarımı (Kendisi düzenlemediyse kırmızı parlayan tag & rozet)
        if "isim_rengi" not in user_doc_fresh or not user_doc_fresh.get("isim_rengi"):
            u_color_fresh = "#FF0000"
            u_glow_fresh = True
        if "rozet" not in user_doc_fresh or not user_doc_fresh.get("rozet"):
            u_rozet_fresh = "🛠️"
        if "tag" not in user_doc_fresh or not user_doc_fresh.get("tag"):
            u_tag_fresh = "KURUCU"

    display_name = get_styled_user_name(kullanici_ismi_fresh, u_color_fresh, u_glow_fresh, u_tag_fresh, u_rozet_fresh)

    for m in st.session_state.messages:
        if m["role"] == "assistant":
            st.markdown(f'''<div class="assistant-box"><img src="{AVATAR_URL}" class="avatar"><div><div class="header-box">Aslan Parçası</div><div>{m["content"]}</div></div></div>''', unsafe_allow_html=True)
        else:
            st.markdown(f'''<div class="user-box"><div><div class="header-box" style="text-align: right;">{display_name}</div><div>{m["content"]}</div></div><img src="{USER_AVATAR}" class="avatar"></div>''', unsafe_allow_html=True)

    def ai_cevap(mesajlar):
        current_doc = user_ref.get().to_dict()
        current_name = current_doc.get("isim", "Kullanıcı")
        
        kurucu_durumu = "SİZ KURUCUSUNUZ (AYAZ KAPLAN)." if is_kurucu else f"Kullanıcının ismi: {current_name}."
        
        sistem_mesaji = (
            "Senin ismin Aslan Parçası, kurucun Ayaz Kaplan. Şirketin MEAY Aslan Parçası AI Anonim Şirketi. "
            "Bu bilgileri aslan_canli_akis.txt dosyasından okumuyorsan, doğrudan sistem talimatlarının en başına ekleyerek kullan. "
            f"Durum: {kurucu_durumu} "
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

    # Küfür uyarısı arayüzde gösterimi
    if "kufur_warning" in st.session_state:
        st.error(st.session_state.kufur_warning)

    # Kalıcı Sohbet: Mesajlar st.session_state.messages'a eklenirken, Firestore veritabanına da eşzamanlı olarak anında append (ArrayUnion) edilir.
    def send_message():
        val = st.session_state.my_input.strip()
        if val:
            # Otomatik Küfür Denetimi ve Engelleme
            if kufur_var_mi(val):
                # Raporu 'yonetici_bildirimleri' koleksiyonuna ekle
                bildirim_id = f"kufur_{int(datetime.now(timezone.utc).timestamp())}_{uid}"
                db.collection("yonetici_bildirimleri").document(bildirim_id).set({
                    "uid": uid,
                    "email": user_doc.get("email", ""),
                    "isim": user_doc.get("isim", "Bilinmeyen"),
                    "mesaj": val,
                    "tarih": firestore.SERVER_TIMESTAMP
                })
                st.session_state.kufur_warning = "⚠️ Mesajınız uygunsuz içerik nedeniyle engellendi!"
                st.session_state.my_input = "" 
                st.session_state.input_key += 1
                return
            
            # Küfür yoksa normal sohbet akışına devam et
            st.session_state.pop("kufur_warning", None)
            
            # 1. Kullanıcı mesajını yerel oturuma ekle
            st.session_state.messages.append({"role": "user", "content": val})
            # 2. Kullanıcı mesajını anlık olarak veritabanına ekle
            user_ref.update({
                "sohbet_gecmisi": firestore.ArrayUnion([{"role": "user", "content": val}])
            })
            
            # AI cevabını al
            cevap = ai_cevap(st.session_state.messages[-6:])
            
            # 3. Asistan cevabını yerel oturuma ekle
            st.session_state.messages.append({"role": "assistant", "content": cevap})
            # 4. Asistan cevabını anlık olarak veritabanına ekle
            user_ref.update({
                "sohbet_gecmisi": firestore.ArrayUnion([{"role": "assistant", "content": cevap}])
            })
            
            st.session_state.my_input = "" 
            st.session_state.input_key += 1

    st.text_area("Mesajını yaz:", key="my_input", height=100)
    st.button("🚀 Gönder", on_click=send_message)
