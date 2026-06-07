import streamlit as st
import requests
import os

# Ayarlar
API_KEY = os.environ.get("API_KEY")
MODEL = "anthropic/claude-3-haiku"
KURUCU_SIFRESI = "KAPLAN_REIS_74"
AVATAR_URL = "https://i.imgur.com/3EfO8Ae.jpeg"
USER_AVATAR = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
DOSYA_ADI = "sarki_id.txt"
TEMA_DOSYASI = "tema_id.txt"

# --- KALICI DOSYA FONKSİYONLARI ---
def kaydet(dosya, deger):
    with open(dosya, "w") as f: f.write(deger.strip())

def oku(dosya):
    if os.path.exists(dosya):
        with open(dosya, "r") as f: return f.read().strip()
    return ""

def sil(dosya):
    if os.path.exists(dosya): os.remove(dosya)

st.set_page_config(page_title="Aslan Parçası V14.0", page_icon="🤖")

# Session State Hazırlığı
if "messages" not in st.session_state: st.session_state.messages = []
if "is_admin" not in st.session_state: st.session_state.is_admin = False
if "isim" not in st.session_state: st.session_state.isim = "Ziyaretçi"

# --- UI LOGIC ---
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

with st.sidebar:
    # Şifre girişi
    if not st.session_state.is_admin:
        sifre = st.text_input("🔑 Şifre:", type="password")
        if sifre == KURUCU_SIFRESI:
            st.session_state.is_admin = True
            st.rerun()
    else:
        st.success("✅ Kurucu Modu Aktif")
        if st.button("🚪 Çıkış Yap"):
            st.session_state.is_admin = False
            st.rerun()

    mod = "Kurucu" if st.session_state.is_admin else "Misafir"
    
    # İsim seçimi
    if mod == "Kurucu":
        st.session_state.isim = st.selectbox("👤 Kimsin Reis?", ["Ayaz Reis", "Mehmet Reis"], index=0 if st.session_state.isim == "Ayaz Reis" else 1)
    else:
        st.session_state.isim = "Ziyaretçi"
        
    # --- TEMA SEÇİMİ ---
    assistant_box_bg, theme_map = get_theme_data(mod)
    kayitli_tema = oku(TEMA_DOSYASI)
    if kayitli_tema not in theme_map: kayitli_tema = list(theme_map.keys())[0]
    
    tema_secimi = st.selectbox("Arka Plan Seç:", list(theme_map.keys()), index=list(theme_map.keys()).index(kayitli_tema))
    if st.button("💾 Temayı Kaydet"):
        kaydet(TEMA_DOSYASI, tema_secimi)
        st.rerun()
    
    bg_color, text_color = theme_map[tema_secimi]
    
    if st.button("🔄 Sohbeti Temizle"):
        st.session_state.messages = []
        st.rerun()

    # --- MÜZİK MOTORU ---
    st.markdown("---")
    st.subheader("🎵 Müzik Motoru")
    kayitli_id = oku(DOSYA_ADI)
    yeni_id = st.text_input("YouTube Video ID'si:", value=kayitli_id)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Kaydet ve Oynat"):
            kaydet(DOSYA_ADI, yeni_id)
            st.rerun()
    with col2:
        if st.button("🗑️ Sil"):
            sil(DOSYA_ADI)
            st.rerun()

    if kayitli_id:
        st.link_button("▶️ Hata Alırsan YouTube'da İzle", f"https://www.youtube.com/watch?v={kayitli_id}")
        st.markdown(f'<iframe width="100%" height="200" src="https://www.youtube.com/embed/{kayitli_id}" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>', unsafe_allow_html=True)

# --- STYLE ---
st.markdown(f"""
    <style>
    .stApp {{ background: {bg_color}; color: {text_color} !important; }}
    .assistant-box {{ background-color: {assistant_box_bg}; padding: 15px; border-radius: 10px; border-left: 5px solid gold; margin-bottom: 10px; color: {text_color}; }}
    .user-box {{ background-color: rgba(128, 128, 128, 0.2); padding: 15px; border-radius: 10px; margin-bottom: 10px; text-align: right; color: {text_color}; }}
    .aslan-header {{ display: flex; align-items: center; gap: 10px; font-weight: bold; border-bottom: 1px solid gold; padding-bottom: 5px; margin-bottom: 5px; }}
    .user-header {{ display: flex; align-items: center; justify-content: flex-end; gap: 10px; font-weight: bold; margin-bottom: 8px; }}
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 Aslan Parçası V14.0")

for m in st.session_state.messages:
    if m["role"] == "assistant":
        st.markdown(f"""<div class="assistant-box"><div class="aslan-header"><img src="{AVATAR_URL}" width="30" style="border-radius:50%"> Aslan Parçası</div><div>{m['content']}</div></div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div class="user-box"><div class="user-header">{st.session_state.isim} <img src="{USER_AVATAR}" width="30" style="border-radius:50%"></div><div>{m['content']}</div></div>""", unsafe_allow_html=True)

def ai_cevap(mesaj_gecmisi, mod, isim):
    headers = {"Authorization": f"Bearer {API_KEY}", "HTTP-Referer": "https://aslan-parcasi-widget.onrender.com", "X-Title": "Aslan Parcasi"}
    talimat = f"Sen Aslan Parçası'sın. Kullanıcı: '{isim}', Mod: '{mod}'."
    sistem = {"role": "system", "content": talimat}
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json={"model": MODEL, "messages": [sistem] + mesaj_gecmisi[-6:]})
        return res.json()['choices'][0]['message']['content']
    except Exception: return "Sistem meşgul, Reis."

user_input = st.chat_input("Mesajını yaz...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    cevap = ai_cevap(st.session_state.messages, mod, st.session_state.isim)
    st.session_state.messages.append({"role": "assistant", "content": cevap})
    st.rerun()
 
