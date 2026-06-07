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

# --- KALICI DOSYA FONKSİYONLARI ---
def id_kaydet(yeni_id):
    with open(DOSYA_ADI, "w") as f: f.write(yeni_id)

def id_sil():
    if os.path.exists(DOSYA_ADI): os.remove(DOSYA_ADI)

def id_oku():
    if os.path.exists(DOSYA_ADI):
        with open(DOSYA_ADI, "r") as f: return f.read().strip()
    return ""

st.set_page_config(page_title="Aslan Parçası V14.0", page_icon="🤖")

if "messages" not in st.session_state: st.session_state.messages = []

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
    sifre = st.text_input("🔑 Şifre:", type="password")
    mod = "Kurucu" if sifre == KURUCU_SIFRESI else "Misafir"
    isim = st.selectbox("👤 Kimsin Reis?", ["Ayaz Reis", "Mehmet Reis"]) if mod == "Kurucu" else "Ziyaretçi"
        
    assistant_box_bg, theme_map = get_theme_data(mod)
    tema_secimi = st.selectbox("Arka Plan Seç:", list(theme_map.keys()))
    bg_color, text_color = theme_map[tema_secimi]
    
    if st.button("🔄 Sohbeti Temizle"):
        st.session_state.messages = []
        st.rerun()

    # --- MÜZİK MOTORU (GÜNCELLENMİŞ) ---
    st.markdown("---")
    st.subheader("🎵 Müzik Motoru")
    
    with st.expander("⋮ Müzik ID Nedir ve Nasıl Bulunur?"):
        st.write("""
        **Video ID, YouTube'daki şarkının özel kimlik kodudur.**
        
        **Nasıl Bulunur?**
        1. İstediğin şarkıyı YouTube uygulamasında veya tarayıcıda aç.
        2. Paylaş butonuna basıp **'Bağlantıyı Kopyala'** de.
        3. Kopyaladığın link şuna benzer: `https://youtu.be/Ju-VnQuWoQU` veya `...watch?v=Ju-VnQuWoQU`
        4. Eşittir (=) işaretinden veya son eğik çizgiden (/) sonra gelen **Ju-VnQuWoQU** kodu senin ID'ndir.
        5. Bu kodu kutucuğa yapıştırıp 'Kaydet ve Oynat' tuşuna basman yeterlidir.
        """)
    
    kayitli_id = id_oku()
    yeni_id = st.text_input("YouTube Video ID'si:", value=kayitli_id)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Kaydet ve Oynat"):
            id_kaydet(yeni_id)
            st.rerun()
    with col2:
        if st.button("🗑️ Sil"):
            id_sil()
            st.rerun()

    if id_oku():
        st.markdown(f'<iframe width="100%" height="200" src="https://www.youtube.com/embed/{id_oku()}" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>', unsafe_allow_html=True)

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
        st.markdown(f"""<div class="user-box"><div class="user-header">{isim} <img src="{USER_AVATAR}" width="30" style="border-radius:50%"></div><div>{m['content']}</div></div>""", unsafe_allow_html=True)

def ai_cevap(mesaj_gecmisi, mod, isim):
    headers = {"Authorization": f"Bearer {API_KEY}", "HTTP-Referer": "https://aslan-parcasi-widget.onrender.com", "X-Title": "Aslan Parcasi"}
    talimat = f"Sen Aslan Parçası'sın. Kullanıcın: '{isim}'. 1. AYAZ REIS: Kurucu, 2. MEHMET REIS: Yardımcı."
    sistem = {"role": "system", "content": talimat}
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json={"model": MODEL, "messages": [sistem] + mesaj_gecmisi[-6:]})
        return res.json()['choices'][0]['message']['content']
    except Exception: return "Sistem meşgul, tekrar dene Reis."

user_input = st.chat_input("Mesajını yaz...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    cevap = ai_cevap(st.session_state.messages, mod, isim)
    st.session_state.messages.append({"role": "assistant", "content": cevap})
    st.rerun()
