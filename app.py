import streamlit as st
import requests
import os
import json
import firebase_admin
from firebase_admin import credentials, auth, firestore
import re
from datetime import datetime, timezone, timedelta

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

# --- OTURUM YÖNETİMİ & KALICILIK ---
if "user_logged_in" not in st.session_state: st.session_state.user_logged_in = False
if "user_data" not in st.session_state: st.session_state.user_data = None
if "messages" not in st.session_state: st.session_state.messages = []
if "tema" not in st.session_state: st.session_state.tema = list(TEMALAR.values())[0]
if "valid_users_cache" not in st.session_state: st.session_state.valid_users_cache = None
if "current_page" not in st.session_state: st.session_state.current_page = "chat"

# Kalıcı Oturum Desteği (Query Params Kontrolü)
if not st.session_state.user_logged_in and "session_uid" in st.query_params:
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
                st.session_state.user_logged_in = True
                st.session_state.tema = user_data.get("tema", list(TEMALAR.values())[0])
                # Tarayıcı URL kalıcılığını pekiştir
                st.query_params["session_uid"] = stored_uid
                
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
                # Kullanıcı banlıysa kalıcı oturum parametresini URL'den temizle
                st.query_params.pop("session_uid", None)
    except Exception:
        pass

# --- ŞİFRE KONTROLÜ (REST API) ---
def firebase_login(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    res = requests.post(url, json=payload)
    return res.json() if res.status_code == 200 else None

# --- EMOJİ KONTROLÜ ---
def emoji_var_mi(text):
    return bool(re.search(r'[^\w\s,.]', text))

# --- KÜFÜR KONTROL FONKSİYONU ---
def kufur_var_mi(text):
    KUFUR_LISTESI = [
        "amk", "aq", "orospu", "piç", "skm", "sik", "sikiş", "göt", "gavat", "pezevenk", "yarrak", "yarak", 
        "meme", "daşşak", "dassak", "fuck", "bitch", "asshole", "shit"
    ]
    text_lower = text.lower()
    # Kelime sınırlarına bakarak kontrol edilir, böylece "bisiklet" gibi kelimeler filtrelenmez.
    for bad_word in KUFUR_LISTESI:
        pattern = r'\b' + re.escape(bad_word) + r'\b'
        if re.search(pattern, text_lower):
            return True
    return False

# --- GİRİŞ VE KAYIT EKRANI ---
if not st.session_state.user_logged_in:
    st.set_page_config(page_title="Aslan Parçası V16.4", page_icon="🦁")
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
                        st.session_state.user_logged_in = True
                        st.session_state.tema = user_data.get("tema", list(TEMALAR.values())[0])
                        
                        # Kalıcı Oturum: Tarayıcı URL'sine session_uid parametresini ekliyoruz
                        st.query_params["session_uid"] = auth_res['localId']
                        
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
                    "son_gorulme_zamani": None
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
st.set_page_config(page_title="Aslan Parçası V16.4", page_icon="🦁", layout="centered")

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
    st.query_params.pop("session_uid", None)
    st.session_state.user_logged_in = False
    st.session_state.user_data = None
    st.session_state.ban_error_on_logout = ban_hata_mesaji
    st.rerun()

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
saved_videos = user_doc.get("videos", [])
kullanici_ismi = user_doc.get('isim')

# Kurucu değilse admin sayfasında kalmasını engelle
if st.session_state.current_page == "admin" and not is_kurucu:
    st.session_state.current_page = "chat"
    st.rerun()

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
            st.session_state.valid_users_cache = None  # Önbelleği temizle
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
    
    # Sohbeti Arşivleyerek Temizleme Özelliği (Onarılmış Sürüm)
    if st.button("🧹 Sohbeti Temizle"):
        user_ref.update({
            "sohbet_gecmisi": firestore.ArrayUnion([{"role": "separator", "content": "--- SOHBET TEMİZLENDİ ---"}])
        })
        st.session_state.messages = []
        st.success("Sohbet temizlendi!")
        st.rerun()
        
    if st.button("🚪 Çıkış Yap"): 
        st.query_params.pop("session_uid", None) # Çıkışta tarayıcı kalıcılık parametresini temizle
        st.session_state.clear()
        st.rerun()
    
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
                    st.query_params.pop("session_uid", None) # Tarayıcı oturumunu sil
                    st.session_state.clear()
                    st.rerun()
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
    
    for v in saved_videos:
        c1, c2 = st.columns([0.8, 0.2])
        c1.markdown(f'<iframe width="100%" height="150" src="https://www.youtube.com/embed/{v}" frameborder="0"></iframe>', unsafe_allow_html=True)
        if c2.button("🗑️", key=v):
            user_ref.update({"videos": firestore.ArrayRemove([v])})
            st.rerun()

    # Sadece kurucular için en altta tek bir dinamik geçiş butonu
    if is_kurucu:
        st.divider()
        if st.session_state.current_page == "chat":
            if st.button("🛠️ Yönetici Paneline Git", use_container_width=True):
                st.session_state.current_page = "admin"
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
if st.session_state.current_page == "admin" and is_kurucu:
    # --- KULLANICI YÖNETİM SAYFASI (AYRI EKRAN) ---
    st.title("👥 Kullanıcı Yönetim Sayfası")
    st.write("Yönetici paneline hoş geldiniz, Reis. Buradan kullanıcıları e-posta ile arayabilir, şifre detaylarını görebilir ve hesapları yönetebilirsiniz.")
    
    col_back, col_ref = st.columns([7, 3])
    with col_back:
        if st.button("⬅️ Sohbet Paneline Dön", type="secondary"):
            st.session_state.current_page = "chat"
            st.rerun()
    with col_ref:
        if st.button("🔄 Listeyi Yeniden Tara", use_container_width=True):
            st.session_state.valid_users_cache = None
            st.rerun()
            
    st.divider()
    
    # Yönetici Paneli Sekmeleri (Kullanıcılar ve Küfür Bildirimleri)
    tab_kullanicilar, tab_bildirimler = st.tabs(["👥 Kullanıcılar", "⚠️ Yönetici Bildirimleri (Küfür Raporları)"])
    
    with tab_kullanicilar:
        # Arama Motoru
        arama_query = st.text_input("🔍 E-posta ile Ara (Tam Eşleşme):").strip().lower()
        
        try:
            if st.session_state.valid_users_cache is None:
                st.session_state.valid_users_cache = otomatik_arindir_ve_grup()
                
            valid_users = st.session_state.valid_users_cache
            
            # Filtreleme uygulaması
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
                        
                        # Yönetici Panelinde Kesintisiz Sohbet Geçmişi İzleme
                        if isinstance(u_sohbet_gecmisi, list) and u_sohbet_gecmisi:
                            formatted_lines = []
                            for msg in u_sohbet_gecmisi:
                                role = msg.get("role")
                                content = msg.get("content", "")
                                if role == "separator":
                                    formatted_lines.append(f"\n{content}\n")
                                elif role == "user":
                                    formatted_lines.append(f"[Kullanıcı]: {content}")
                                elif role == "assistant":
                                    formatted_lines.append(f"[Aslan Parçası]: {content}")
                            full_transcript = "\n".join(formatted_lines)
                            
                            with st.expander("💾 Arşivlenmiş & Aktif Tüm Sohbet Geçmişi"):
                                st.text_area("Yedeklenen Sohbetler:", value=full_transcript, height=250, disabled=True, key=f"backup_view_{u_id}")
                        elif isinstance(u_sohbet_gecmisi, str) and u_sohbet_gecmisi:
                            with st.expander("💾 Arşivlenmiş Sohbet Geçmişi (Eski Format)"):
                                st.text_area("Yedeklenen Sohbetler:", value=u_sohbet_gecmisi, height=250, disabled=True, key=f"backup_view_{u_id}")
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
            if bildirimler:
                for b_doc in bildirimler:
                    b_data = b_doc.to_dict()
                    b_id = b_doc.id
                    b_isim = b_data.get("isim", "Bilinmeyen")
                    b_email = b_data.get("email", "")
                    b_mesaj = b_data.get("mesaj", "")
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

else:
    # --- YÖNETİCİ PANELİ (Sadece Kurucuya Özel - Expander Korundu) ---
    if is_kurucu:
        with st.expander("🛠️ YÖNETİCİ PANELİ (Kurucu Özel)"):
            st.write("Kurucu paneline hoş geldiniz, Reis.")
            st.info("Kullanıcıların detaylı listesine ulaşmak, arama yapmak ve şifreleri incelemek için aşağıdaki butona tıklayabilirsiniz.")
            if st.button("👥 Kullanıcı Yönetim Sayfasını Aç", key="open_admin_page", use_container_width=True):
                st.session_state.current_page = "admin"
                st.rerun()

    # --- SOHBET ARAYÜZÜ ---
    st.title("🤖 Aslan Parçası V16.4")

    # Veritabanından en güncel ismi çek
    user_doc_fresh = user_ref.get().to_dict()
    kullanici_ismi_fresh = user_doc_fresh.get('isim', kullanici_ismi)

    for m in st.session_state.messages:
        if m["role"] == "assistant":
            st.markdown(f'''<div class="assistant-box"><img src="{AVATAR_URL}" class="avatar"><div><div class="header-box">Aslan Parçası</div><div>{m["content"]}</div></div></div>''', unsafe_allow_html=True)
        else:
            display_name = f'<span style="color:red; text-shadow: 0 0 5px red;">{kullanici_ismi_fresh} 🛠️</span>' if is_kurucu else kullanici_ismi_fresh
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
