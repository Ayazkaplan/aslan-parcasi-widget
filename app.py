import streamlit as st
import requests
import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- GOOGLE SHEETS BAĞLANTISI ---
def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    # Render'daki ortam değişkeninden JSON'u çekiyoruz
    creds_dict = json.loads(st.secrets["GCP_JSON"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    # Sheet isminin tam olarak 'AslanParcasiVeri' olduğundan emin ol
    return client.open("AslanParcasiVeri").sheet1

# --- YARDIMCI FONKSİYONLAR (Google Sheets için) ---
def kayit_et(isim, sifre, rol):
    sheet = get_sheet()
    sheet.append_row([isim, sifre, rol])

def kullanici_var_mi(isim):
    sheet = get_sheet()
    return isim in sheet.col_values(1)

def giris_kontrol(isim, sifre):
    sheet = get_sheet()
    data = sheet.get_all_records()
    for row in data:
        if str(row['İsim']) == isim and str(row['Şifre']) == sifre:
            return row['Rol']
    return None

def tercih_guncelle(isim, tema, sarki_id):
    # Bu kısım için ikinci bir sekme (tab) kullanmak daha temiz olur
    # Şimdilik basit tutuyoruz, Sheet'te tercihleri yönetmek biraz daha ileri seviye işlem ister.
    pass

# --- AYARLAR ---
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
        if menu == "Kayıt Ol":
            if not kullanici_var_mi(u_isim):
                kayit_et(u_isim, u_sifre, "Misafir")
                st.success("Kayıt başarılı! Şimdi giriş yapabilirsin.")
            else:
                st.error("İsim zaten alınmış!")
        else:
            rol = giris_kontrol(u_isim, u_sifre)
            if rol:
                st.session_state.logged_in = True
                st.session_state.current_user = u_isim
                st.session_state.rol = rol
                st.rerun()
            else:
                st.error("Hatalı bilgiler!")

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
st.sidebar.write(f"Hoş geldin Reis: {st.session_state.current_user} ({st.session_state.rol})")
if st.sidebar.button("🚪 Çıkış Yap"): st.session_state.logged_in = False; st.rerun()

st.title("🤖 Aslan Parçası V16.4")

# AI Cevap fonksiyonun aynı kalabilir
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
        cevap = ai_cevap(st.session_state.messages, st.session_state.rol, user_input)
        st.session_state.messages.append({"role": "assistant", "content": cevap})
        st.rerun()
 
