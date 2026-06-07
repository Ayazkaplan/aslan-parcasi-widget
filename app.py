import streamlit as st
import requests
import os
import sqlite3
from duckduckgo_search import DDGS
from datetime import datetime, timedelta

# --- VERİTABANI KURULUMU ---
def get_db():
    conn = sqlite3.connect("aslan_parcasi.db", check_same_thread=False)
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    # Rol, isim ve şifre kalıcı olarak saklanır
    cursor.execute('''CREATE TABLE IF NOT EXISTS kullanicilar 
                      (isim TEXT PRIMARY KEY, sifre TEXT, rol TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- AYARLAR ---
API_KEY = os.environ.get("API_KEY")
MODEL = "anthropic/claude-3-haiku"
KURUCU_ANAHTARI = "NiHAi_-kuRucU-AyAz" # Bypass şifren
AVATAR_URL = "https://i.imgur.com/3EfO8Ae.jpeg"
USER_AVATAR = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
DOSYA_ADI = "sarki_id.txt"
TEMA_KURUCU = "tema_kurucu.txt"
TEMA_MISAFIR = "tema_misafir.txt"

# --- FONKSİYONLAR ---
def kaydet(dosya, deger):
    with open(dosya, "w") as f: f.write(deger.strip())

def oku(dosya):
    if os.path.exists(dosya):
        with open(dosya, "r") as f: return f.read().strip()
    return ""

def web_ara(sorgu):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(sorgu, max_results=3))
            return "Güncel bilgiler: " + "\n".join([r['body'] for r in results])
    except: return "İnternete erişemiyorum Reis."

st.set_page_config(page_title="Aslan Parçası V16.4", page_icon="🦁")

# --- OTURUM YÖNETİMİ ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "current_user" not in st.session_state: st.session_state.current_user = None
if "rol" not in st.session_state: st.session_state.rol = "Misafir"
if "messages" not in st.session_state: st.session_state.messages = []
if "input_key" not in st.session_state: st.session_state.input_key = 0
if "admin_panel_open" not in st.session_state: st.session_state.admin_panel_open = False

# --- GİRİŞ EKRANI ---
if not st.session_state.logged_in:
    st.title("🦁 Aslan Parçası - Giriş Sistemi")
    menu = st.radio("Seçim:", ["Giriş Yap", "Kayıt Ol"])
    u_isim = st.text_input("Kullanıcı Adı")
    u_sifre = st.text_input("Şifre", type="password")
    
    if st.button("🚀 İşlemi Başlat"):
        conn = get_db()
        cursor = conn.cursor()
        if menu == "Kayıt Ol":
            try:
                cursor.execute("INSERT INTO kullanicilar VALUES (?, ?, ?)", (u_isim, u_sifre, "Misafir"))
                conn.commit(); st.success("Kayıt başarılı!"); st.rerun()
            except: st.error("İsim zaten alınmış!")
        else:
            cursor.execute("SELECT * FROM kullanicilar WHERE isim=? AND sifre=?", (u_isim, u_sifre))
            user = cursor.fetchone()
            if user:
                st.session_state.logged_in = True
                st.session_state.current_user = u_isim
                st.session_state.rol = user[2]
                st.rerun()
            else: st.error("Hatalı bilgiler!")
        conn.close()

    # --- SANA ÖZEL GİZLİ BYPASS (Sadece Kurucu değilsen gözükür) ---
    if st.session_state.rol != "Kurucu":
        st.sidebar.markdown("---")
        gizli_bypass = st.sidebar.text_input("🔧 Sistem Ayarları", type="password")
        if gizli_bypass == KURUCU_ANAHTARI:
            yeni_kurucu_adi = st.sidebar.text_input("Kurucu Adın:")
            if st.sidebar.button("Kurucu Hesabı Oluştur"):
                st.session_state.logged_in = True
                st.session_state.current_user = yeni_kurucu_adi
                st.session_state.rol = "Kurucu"
                st.rerun()
    st.stop()

# --- GİRİŞ YAPMIŞ ALAN ---
mod = st.session_state.rol
isim = st.session_state.current_user

with st.sidebar:
    st.write(f"Hoş geldin Reis: {isim} ({mod})")
    if st.button("🚪 Çıkış Yap"): st.session_state.logged_in = False; st.session_state.rol = "Misafir"; st.rerun()
    
    tema_dosyasi = TEMA_KURUCU if mod == "Kurucu" else TEMA_MISAFIR
    assistant_box_bg = "rgba(30, 30, 30, 0.9)" if mod == "Kurucu" else "rgba(144, 238, 144, 0.3)"
    theme_map = {"Aslan İni": ("linear-gradient(to bottom, #1a1a00, #000000)", "white")} if mod == "Kurucu" else {"Gün Işığı": ("#f0f2f6", "black")}
    
    tema_secimi = st.selectbox("Arka Plan:", list(theme_map.keys()))
    if st.button("💾 Temayı Kaydet"): kaydet(tema_dosyasi, tema_secimi); st.rerun()
    bg_color, text_color = theme_map[tema_secimi]
    if st.button("🔄 Sohbeti Temizle"): st.session_state.messages = []; st.rerun()

    st.markdown("---")
    st.subheader("🎵 Müzik Motoru")
    kayitli_id = oku(DOSYA_ADI)
    yeni_id = st.text_input("Video ID:", value=kayitli_id)
    if st.button("💾 Kaydet"): kaydet(DOSYA_ADI, yeni_id); st.rerun()
    if kayitli_id: st.markdown(f'<iframe width="100%" height="200" src="https://www.youtube.com/embed/{kayitli_id}" frameborder="0"></iframe>', unsafe_allow_html=True)

# --- STYLE ---
st.markdown(f"""<style>.stApp {{ background: {bg_color}; color: {text_color} !important; }} .assistant-box {{ background-color: {assistant_box_bg}; padding: 15px; border-radius: 10px; border-left: 5px solid gold; }} .user-box {{ background-color: rgba(128, 128, 128, 0.2); padding: 15px; border-radius: 10px; text-align: right; }}</style>""", unsafe_allow_html=True)

# --- MAIN ---
st.title("🤖 Aslan Parçası V16.4")
if mod == "Kurucu":
    if st.button("⚙️ Yönetici Paneli"): st.session_state.admin_panel_open = not st.session_state.admin_panel_open; st.rerun()
    if st.session_state.admin_panel_open:
        with st.container(border=True):
            st.subheader("🛠️ Yönetici Paneli")
            if st.button("❌ Paneli Kapat"): st.session_state.admin_panel_open = False; st.rerun()

def ai_cevap(mesaj_gecmisi, mod, isim, kullanici_mesaji):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    ek_bilgi = f"\n[Bilgi]: Saat {(datetime.utcnow() + timedelta(hours=3)).strftime('%H:%M')}."
    if any(k in kullanici_mesaji.lower() for k in ["hava", "ara", "nedir"]): ek_bilgi += f"\n[İnternet]: {web_ara(kullanici_mesaji)}"
    karakter = "Sen neşeli, samimi ve sadık bir asistansın." if mod == "Kurucu" else "Sen ciddi ve otoriter bir asistansın."
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json={"model": MODEL, "messages": [{"role": "system", "content": f"{karakter} Adın Aslan Parçası. {ek_bilgi}"}] + mesaj_gecmisi[-6:]})
        return res.json()['choices'][0]['message']['content']
    except: return "Sistem meşgul, Reis."

for m in st.session_state.messages:
    if m["role"] == "assistant": st.markdown(f'<div class="assistant-box">{m["content"]}</div>', unsafe_allow_html=True)
    else: st.markdown(f'<div class="user-box">{m["content"]}</div>', unsafe_allow_html=True)

user_input = st.text_area("Mesajını yaz:", key=f"chat_input_{st.session_state.input_key}")
if st.button("🚀 Gönder"):
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        cevap = ai_cevap(st.session_state.messages, mod, isim, user_input)
        st.session_state.messages.append({"role": "assistant", "content": cevap})
        st.session_state.input_key += 1
        st.rerun()
