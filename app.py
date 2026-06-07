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
    cursor.execute('''CREATE TABLE IF NOT EXISTS kullanicilar 
                      (isim TEXT PRIMARY KEY, sifre TEXT, rol TEXT, tema TEXT, video_id TEXT, ozel_tag TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS genel_sohbet 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, gonderen TEXT, mesaj TEXT, zaman TIMESTAMP)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS loglar 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, mesaj TEXT, tip TEXT, zaman TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

# --- AYARLAR ---
API_KEY = os.environ.get("API_KEY")
MODEL = "anthropic/claude-3-haiku"
KURUCU_SIFRESI = "KAPLAN_REIS_74"
NIHAI_SIFRE = "NiHAi_-kuRucU-AyAz"
AVATAR_URL = "https://i.imgur.com/3EfO8Ae.jpeg"
USER_AVATAR = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
DOSYA_ADI = "sarki_id.txt"
MOD_DOSYASI = "mod_id.txt"
ISIM_DOSYASI = "isim_id.txt"
TEMA_KURUCU = "tema_kurucu.txt"
TEMA_MISAFIR = "tema_misafir.txt"

# --- FONKSİYONLAR ---
def kaydet(dosya, deger):
    with open(dosya, "w") as f: f.write(deger.strip())

def oku(dosya):
    if os.path.exists(dosya):
        with open(dosya, "r") as f: return f.read().strip()
    return ""

def sil(dosya):
    if os.path.exists(dosya): os.remove(dosya)

def web_ara(sorgu):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(sorgu, max_results=3))
            return "Güncel bilgiler: " + "\n".join([r['body'] for r in results])
    except: return "İnternete erişemiyorum Reis."

st.set_page_config(page_title="Aslan Parçası V16.3", page_icon="🦁")

# --- HESAP SİSTEMİ ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "current_user" not in st.session_state: st.session_state.current_user = None

def kayit_ol(isim, sifre):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO kullanicilar (isim, sifre, rol) VALUES (?, ?, ?)", (isim, sifre, "Misafir"))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

def giris_yap(isim, sifre):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM kullanicilar WHERE isim=? AND sifre=?", (isim, sifre))
    user = cursor.fetchone()
    conn.close()
    return user

# --- MOD YÖNETİMİ ---
is_admin = (oku(MOD_DOSYASI) == "Kurucu")
if "messages" not in st.session_state: st.session_state.messages = []
if "input_key" not in st.session_state: st.session_state.input_key = 0
if "ayaz_yetkili" not in st.session_state: st.session_state.ayaz_yetkili = False
if "admin_panel_open" not in st.session_state: st.session_state.admin_panel_open = False

def get_theme_data(mod):
    if mod == "Kurucu":
        assistant_box_bg = "rgba(30, 30, 30, 0.9)"
        themes = {
            "Aslan İni": ("linear-gradient(to bottom, #1a1a00, #000000)", "white"),
            "Kraliyet": ("linear-gradient(to bottom, #2c0000, #000000)", "white"),
            "Orman Derinliği": ("linear-gradient(to bottom, #003300, #000000)", "white"),
            "Uzay": ("linear-gradient(to bottom, #1a0033, #000000)", "white"),
            "Teknoloji": ("linear-gradient(to bottom, #001a33, #000000)", "white")
        }
    else:
        assistant_box_bg = "rgba(144, 238, 144, 0.3)"
        themes = {
            "Gün Işığı": ("#f0f2f6", "black"),
            "Huzur": ("#e0f7fa", "black"),
            "Orman": ("#e8f5e9", "black"),
            "Gece": ("#263238", "white"),
            "Deniz": ("#e1f5fe", "black")
        }
    return assistant_box_bg, themes

# --- GİRİŞ / BYPASS SİSTEMİ ---
if not is_admin and not st.session_state.logged_in:
    st.title("🦁 Aslan Parçası - Giriş Sistemi")
    # BYPASS: Giriş ekranında bu şifreyi girersen direkt Kurucu olursun
    bypass = st.text_input("🔑 Geçiş Anahtarı (Opsiyonel):", type="password")
    if bypass == NIHAI_SIFRE:
        kaydet(MOD_DOSYASI, "Kurucu")
        st.success("✅ Kurucu Modu Aktif Edildi!")
        st.rerun()

    menu = st.radio("Seçim:", ["Giriş Yap", "Kayıt Ol"])
    u_isim = st.text_input("Kullanıcı Adı")
    u_sifre = st.text_input("Şifre", type="password")
    
    if menu == "Kayıt Ol":
        if st.button("Kayıt Ol"):
            if kayit_ol(u_isim, u_sifre): st.success("Başarılı!")
            else: st.error("İsim alınmış!")
    else:
        if st.button("Giriş Yap"):
            if giris_yap(u_isim, u_sifre): 
                st.session_state.logged_in = True
                st.session_state.current_user = u_isim
                st.rerun()
            else: st.error("Hatalı bilgiler!")
    st.stop()

# --- GİRİŞ YAPMIŞ VEYA KURUCU ALANI ---
mod = "Kurucu" if is_admin else "Misafir"
isim = st.session_state.current_user if not is_admin else (oku(ISIM_DOSYASI) or "Mehmet Reis")

with st.sidebar:
    if not is_admin:
        st.write(f"Hoş geldin, {st.session_state.current_user}")
        if st.button("Çıkış Yap"): st.session_state.logged_in = False; st.session_state.current_user = None; st.rerun()
    else:
        st.success("✅ Kurucu Modu Aktif")
        if st.button("🚪 Kurucu Moddan Çık"): sil(MOD_DOSYASI); sil(ISIM_DOSYASI); st.session_state.ayaz_yetkili = False; st.rerun()
        secim = st.selectbox("👤 Kimsin Reis?", ["Mehmet Reis", "Ayaz Reis"], index=["Mehmet Reis", "Ayaz Reis"].index(isim) if isim in ["Mehmet Reis", "Ayaz Reis"] else 0)
        if secim == "Ayaz Reis":
            if not st.session_state.ayaz_yetkili:
                gizli_sifre = st.text_input("👑 Ayaz Reis Şifresi:", type="password")
                if st.button("Doğrula"):
                    if gizli_sifre == NIHAI_SIFRE: st.session_state.ayaz_yetkili = True; kaydet(ISIM_DOSYASI, "Ayaz Reis"); st.rerun()
                    else: st.error("❌ Hatalı!")
                isim = "Mehmet Reis"
            else: isim = "Ayaz Reis"
        else: st.session_state.ayaz_yetkili = False; kaydet(ISIM_DOSYASI, "Mehmet Reis"); isim = "Mehmet Reis"

    tema_dosyasi = TEMA_KURUCU if mod == "Kurucu" else TEMA_MISAFIR
    assistant_box_bg, theme_map = get_theme_data(mod)
    kayitli_tema = oku(tema_dosyasi)
    if kayitli_tema not in theme_map: kayitli_tema = list(theme_map.keys())[0]
    tema_secimi = st.selectbox("Arka Plan:", list(theme_map.keys()), index=list(theme_map.keys()).index(kayitli_tema))
    if st.button("💾 Temayı Kaydet"): kaydet(tema_dosyasi, tema_secimi); st.rerun()
    bg_color, text_color = theme_map[tema_secimi]
    if st.button("🔄 Sohbeti Temizle"): st.session_state.messages = []; st.rerun()

    st.markdown("---")
    st.subheader("🎵 Müzik Motoru")
    kayitli_id = oku(DOSYA_ADI)
    yeni_id = st.text_input("Video ID'si:", value=kayitli_id)
    if st.button("💾 Kaydet"): kaydet(DOSYA_ADI, yeni_id); st.rerun()
    if kayitli_id: st.markdown(f'<iframe width="100%" height="200" src="https://www.youtube.com/embed/{kayitli_id}" frameborder="0" allow="autoplay"></iframe>', unsafe_allow_html=True)

# --- STYLE ---
st.markdown(f"""<style>.stApp {{ background: {bg_color}; color: {text_color} !important; }} .assistant-box {{ background-color: {assistant_box_bg}; padding: 15px; border-radius: 10px; border-left: 5px solid gold; margin-bottom: 10px; }} .user-box {{ background-color: rgba(128, 128, 128, 0.2); padding: 15px; border-radius: 10px; margin-bottom: 10px; text-align: right; }} .aslan-header {{ display: flex; align-items: center; gap: 10px; font-weight: bold; border-bottom: 1px solid gold; padding-bottom: 5px; margin-bottom: 5px; }} .user-header {{ display: flex; align-items: center; justify-content: flex-end; gap: 10px; font-weight: bold; margin-bottom: 8px; }}</style>""", unsafe_allow_html=True)

# --- MAIN ---
col1, col2 = st.columns([4, 1])
with col1: st.title("🤖 Aslan Parçası V16.3")
with col2:
    if isim == "Ayaz Reis":
        if st.button("⚙️ Yönetici"): st.session_state.admin_panel_open = not st.session_state.admin_panel_open; st.rerun()

# Hata veren st.empty() yerine st.container kullandık
if st.session_state.admin_panel_open:
    with st.container(border=True):
        st.subheader("🛠️ Yönetici Paneli")
        if st.button("❌ Paneli Kapat"): st.session_state.admin_panel_open = False; st.rerun()

def ai_cevap(mesaj_gecmisi, mod, isim, kullanici_mesaji):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    ek_bilgi = f"\n[Bilgi]: Saat {(datetime.utcnow() + timedelta(hours=3)).strftime('%H:%M')}."
    if any(k in kullanici_mesaji.lower() for k in ["hava", "ara", "çevir", "nedir"]): ek_bilgi += f"\n[İnternet]: {web_ara(kullanici_mesaji)}"
    karakter = "Sen Ayaz Reis'in kurduğu neşeli, samimi ve sadık bir asistansın." if (mod == "Kurucu" and isim == "Ayaz Reis") else ("Sen ciddi, bilge, otoriter bir asistansın." if mod == "Kurucu" else "Sen doğal ve enerjik bir asistansın.")
    talimat = f"{karakter} Adın Aslan Parçası. {ek_bilgi}"
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json={"model": MODEL, "messages": [{"role": "system", "content": talimat}] + mesaj_gecmisi[-6:]})
        return res.json()['choices'][0]['message']['content']
    except: return "Sistem meşgul, Reis."

for m in st.session_state.messages:
    if m["role"] == "assistant": st.markdown(f'<div class="assistant-box"><div class="aslan-header"><img src="{AVATAR_URL}" width="30" style="border-radius:50%"> Aslan Parçası</div>{m["content"]}</div>', unsafe_allow_html=True)
    else: st.markdown(f'<div class="user-box"><div class="user-header">{isim} <img src="{USER_AVATAR}" width="30" style="border-radius:50%"></div>{m["content"]}</div>', unsafe_allow_html=True)

user_input = st.text_area("Mesajını yaz:", height=100, key=f"chat_input_{st.session_state.input_key}")
if st.button("🚀 Gönder"):
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        cevap = ai_cevap(st.session_state.messages, mod, isim, user_input)
        st.session_state.messages.append({"role": "assistant", "content": cevap})
        st.session_state.input_key += 1
        st.rerun()
