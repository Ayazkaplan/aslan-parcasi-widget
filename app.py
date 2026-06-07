import streamlit as st
import requests
import os
import psycopg2
from datetime import datetime, timedelta

# --- VERİTABANI BAĞLANTISI (BULUT) ---
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS kullanicilar 
                      (isim TEXT PRIMARY KEY, sifre TEXT, rol TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS tercihler 
                      (isim TEXT PRIMARY KEY, tema TEXT, sarki_id TEXT)''')
    conn.commit()
    cursor.close()
    conn.close()

init_db()

API_KEY = os.environ.get("API_KEY")
MODEL = "anthropic/claude-3-haiku"
KURUCU_ANAHTARI = "NiHAi_-kuRucU-AyAz"

st.set_page_config(page_title="Aslan Parçası V16.4", page_icon="🦁")

# --- OTURUM YÖNETİMİ ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "current_user" not in st.session_state: st.session_state.current_user = None
if "rol" not in st.session_state: st.session_state.rol = "Misafir"
if "messages" not in st.session_state: st.session_state.messages = []

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
                cursor.execute("INSERT INTO kullanicilar VALUES (%s, %s, %s)", (u_isim, u_sifre, "Misafir"))
                cursor.execute("INSERT INTO tercihler VALUES (%s, %s, %s)", (u_isim, "Gün Işığı", ""))
                conn.commit(); st.success("Kayıt başarılı!"); st.rerun()
            except: st.error("İsim zaten alınmış!")
        else:
            cursor.execute("SELECT * FROM kullanicilar WHERE isim=%s AND sifre=%s", (u_isim, u_sifre))
            user = cursor.fetchone()
            if user:
                st.session_state.logged_in = True
                st.session_state.current_user = u_isim
                st.session_state.rol = user[2]
                st.rerun()
            else: st.error("Hatalı bilgiler!")
        cursor.close(); conn.close()

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
isim = st.session_state.current_user
mod = st.session_state.rol

conn = get_db()
cursor = conn.cursor()
cursor.execute("SELECT tema, sarki_id FROM tercihler WHERE isim=%s", (isim,))
tercih = cursor.fetchone()
tema_secimi, kayitli_sarki = tercih if tercih else ("Gün Işığı", "")

with st.sidebar:
    st.write(f"Hoş geldin Reis: {isim} ({mod})")
    if st.button("🚪 Çıkış Yap"): st.session_state.logged_in = False; st.rerun()
    
    yeni_tema = st.selectbox("Arka Plan:", ["Gün Işığı", "Aslan İni"], index=["Gün Işığı", "Aslan İni"].index(tema_secimi))
    yeni_id = st.text_input("Video ID:", value=kayitli_sarki)
    
    if st.button("💾 Profili Güncelle"):
        cursor.execute("UPDATE tercihler SET tema=%s, sarki_id=%s WHERE isim=%s", (yeni_tema, yeni_id, isim))
        conn.commit(); st.rerun()

    if st.button("🔄 Sohbeti Temizle"): st.session_state.messages = []; st.rerun()
    if yeni_id: st.markdown(f'<iframe width="100%" height="200" src="https://www.youtube.com/embed/{yeni_id}" frameborder="0"></iframe>', unsafe_allow_html=True)
cursor.close(); conn.close()

# --- STYLE VE MANTIK ---
bg_color = "#1a1a00" if yeni_tema == "Aslan İni" else "#f0f2f6"
text_color = "white" if yeni_tema == "Aslan İni" else "black"

st.markdown(f"""<style>.stApp {{ background: {bg_color}; color: {text_color} !important; }} 
.assistant-box {{ background-color: rgba(0,0,0,0.3); padding: 15px; border-radius: 10px; border-left: 5px solid gold; }} 
.user-box {{ background-color: rgba(128, 128, 128, 0.2); padding: 15px; border-radius: 10px; text-align: right; }}</style>""", unsafe_allow_html=True)

st.title("🤖 Aslan Parçası V16.4")

def ai_cevap(mesaj_gecmisi, mod, kullanici_mesaji):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    karakter = "Sen neşeli ve sadıksın." if mod == "Kurucu" else "Sen ciddi ve otoritersin."
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json={"model": MODEL, "messages": [{"role": "system", "content": f"{karakter} Adın Aslan Parçası."}] + mesaj_gecmisi[-6:]})
        return res.json()['choices'][0]['message']['content']
    except: return "Sistem meşgul, Reis."

for m in st.session_state.messages:
    cls = "assistant-box" if m["role"] == "assistant" else "user-box"
    st.markdown(f'<div class="{cls}">{m["content"]}</div>', unsafe_allow_html=True)

user_input = st.text_area("Mesajını yaz:")
if st.button("🚀 Gönder"):
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        cevap = ai_cevap(st.session_state.messages, mod, user_input)
        st.session_state.messages.append({"role": "assistant", "content": cevap})
        st.rerun()
 
