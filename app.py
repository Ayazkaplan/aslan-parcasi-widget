import streamlit as st
import requests
import os

# Ayarlar
API_KEY = os.environ.get("API_KEY")
MODEL = "anthropic/claude-3-haiku"
KURUCU_SIFRESI = "KAPLAN_REIS_74"
AVATAR_URL = "https://i.imgur.com/3EfO8Ae.jpeg"
USER_AVATAR = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

st.set_page_config(page_title="Aslan Parçası V11.7.5", page_icon="🤖")

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
    if sifre == KURUCU_SIFRESI:
        mod = "Kurucu"
        isim = st.selectbox("👤 Kimsin Reis?", ["Ayaz Reis", "Mehmet Reis"])
    else:
        mod = "Misafir"
        isim = "Ziyaretçi"
    assistant_box_bg, theme_map = get_theme_data(mod)
    tema_secimi = st.selectbox("Arka Plan Seç:", list(theme_map.keys()))
    bg_color, text_color = theme_map[tema_secimi]
    if st.button("🔄 Sohbeti Temizle"):
        st.session_state.messages = []
        st.rerun()

st.markdown(f"""
    <style>
    .stApp {{ background: {bg_color}; color: {text_color} !important; }}
    .assistant-box {{ background-color: {assistant_box_bg}; padding: 15px; border-radius: 10px; border-left: 5px solid gold; margin-bottom: 10px; color: {text_color}; }}
    .user-box {{ background-color: rgba(128, 128, 128, 0.2); padding: 15px; border-radius: 10px; margin-bottom: 10px; text-align: right; color: {text_color}; }}
    .aslan-header {{ display: flex; align-items: center; gap: 10px; font-weight: bold; border-bottom: 1px solid gold; padding-bottom: 5px; margin-bottom: 5px; }}
    .user-header {{ display: flex; align-items: center; justify-content: flex-end; gap: 10px; font-weight: bold; margin-bottom: 8px; }}
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 Aslan Parçası V11.7.5")

if "messages" not in st.session_state: st.session_state.messages = []

for m in st.session_state.messages:
    if m["role"] == "assistant":
        st.markdown(f"""<div class="assistant-box"><div class="aslan-header"><img src="{AVATAR_URL}" width="30" style="border-radius:50%"> Aslan Parçası</div><div>{m['content']}</div></div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div class="user-box"><div class="user-header">{isim} <img src="{USER_AVATAR}" width="30" style="border-radius:50%"></div><div>{m['content']}</div></div>""", unsafe_allow_html=True)

def ai_cevap(mesaj_gecmisi, isim):
    headers = {"Authorization": f"Bearer {API_KEY}", "HTTP-Referer": "https://aslan-parcasi-widget.onrender.com", "X-Title": "Aslan Parcasi"}
    
    talimat = f"""Sen Aslan Parçası adlı tek bir yapay zekasın. 
    İsmin Aslan Parçası. 
    Kurucun Ayaz Reis'tir.
    Kullanıcın şu an: {isim}. 
    Eğer kullanıcı Ayaz Reis ise ona mutlak sadakat göster.
    Eğer kullanıcı Mehmet Reis ise, o Ayaz Reis'in yardımcısıdır, ona saygılı ol.
    Asla çoğul konuşma, her zaman tekil şahıs kullan. 
    Yazım hatalarını düzeltme, kullanıcının ne demek istediğini anla ve ona göre doğrudan cevap ver."""
        
    sistem = {"role": "system", "content": talimat}
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json={"model": MODEL, "messages": [sistem] + mesaj_gecmisi[-6:]})
        return res.json()['choices'][0]['message']['content']
    except Exception: return "Sistem meşgul, tekrar dene Reis."

# STABİL İNPUT YÖNTEMİ
user_input = st.text_input("Mesajını yaz ve Enter'a bas:", key="unique_input")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    cevap = ai_cevap(st.session_state.messages, isim)
    st.session_state.messages.append({"role": "assistant", "content": cevap})
    st.rerun()
