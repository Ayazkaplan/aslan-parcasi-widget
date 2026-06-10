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

# --- OTURUM YÖNETİMİ ---
if "user_logged_in" not in st.session_state: st.session_state.user_logged_in = False
if "user_data" not in st.session_state: st.session_state.user_data = None
if "messages" not in st.session_state: st.session_state.messages = []
if "tema" not in st.session_state: st.session_state.tema = list(TEMALAR.values())[0]
if "valid_users_cache" not in st.session_state: st.session_state.valid_users_cache = None
if "current_page" not in st.session_state: st.session_state.current_page = "chat"

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
                                user_data["durum"] = "Aktif"
                                user_data["ban_bitis_zamani"] = None
                        else:
                            is_banned = True
                            st.error("❌ Hesabınız pasifleştirilmiştir. Giriş yapamazsınız!")
                    
                    if not is_banned:
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
                clean_email = email.strip().lower()
                user = auth.create_user(email=clean_email, password=password)
                db.collection("users").document(user.uid).set({
                    "isim": isim_input, 
                    "email": clean_email, 
                    "videos": [], 
                    "tema": list(TEMALAR.values())[0],
                    "durum": "Aktif",
                    "gizli_bilgi": password,
                    "ban_bitis_zamani": None
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
user_snap = user_ref.get()

# Veritabanında kullanıcı yoksa oturumu temizle
if not user_snap.exists:
    st.error("❌ Hesabınız silinmiş veya bulunamadı!")
    st.session_state.clear()
    st.rerun()

user_doc = user_snap.to_dict()

# Oturum esnasında pasif duruma getirilmişse oturumu kapat / kontrol et
user_durum = user_doc.get("durum", "Aktif")
ban_bitis = user_doc.get("ban_bitis_zamani")

if user_durum == "Pasif":
    is_banned = False
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
            # Süre dolmuşsa aktif hale getir
            db.collection("users").document(uid).update({
                "durum": "Aktif",
                "ban_bitis_zamani": None
            })
            user_doc["durum"] = "Aktif"
            user_doc["ban_bitis_zamani"] = None
            st.rerun()
    else:
        is_banned = True
        st.error("❌ Hesabınız yönetici tarafından pasif duruma getirilmiştir!")

    if is_banned:
        st.session_state.clear()
        st.stop()

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

    # Sadece kurucular için en altta tek bir dinamik geçiş butonu (Sidebar Temizliği)
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

# --- STYLE VE SOHBET (CSS Taşma Çözümü Dahil) ---
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
            
            # E-posta alanı bulunmayan bozuk kayıtları temizle
            if not u_email:
                doc.reference.delete()
                temizlenen_ghost += 1
                continue
                
            # 1. Aşama: Kullanıcının gerçekten Auth'da olup olmadığını kontrol et, yoksa sil.
            try:
                auth.get_user(u_id)
            except auth.UserNotFoundError:
                doc.reference.delete()
                temizlenen_ghost += 1
                continue
            except Exception:
                pass
                
            # 2. Aşama: Aynı e-postaya sahip tüm kayıtları grupla.
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
            
        # 3. Aşama: Sadece en yeni kaydı tut, diğerlerini sil.
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
            
            if u_email == KURUCU_EMAIL:
                continue
                
            with st.container(border=True):
                col_info, col_sec, col_act = st.columns([4, 3, 3])
                
                with col_info:
                    st.markdown(f"### 👤 {u_isim}")
                    st.markdown(f"📧 **E-posta:** `{u_email}`")
                    
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
                            st.session_state.valid_users_cache = None
                            st.success("Hesap aktifleştirildi.")
                            st.rerun()
                        
                    if st.button("🗑️ Sil", key=f"del_{u_id}", type="primary", use_container_width=True):
                        try:
                            auth.delete_user(u_id)
                            db.collection("users").document(u_id).delete()
                            st.session_state.valid_users_cache = None
                            st.success(f"{u_isim} silindi.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Hata: {e}")
                            
    except Exception as e:
        st.error(f"Kullanıcı listesi alınamadı: {e}")

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
