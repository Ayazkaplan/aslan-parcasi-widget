import streamlit as st
import requests
import os

# Ayarlar
API_KEY = os.environ.get("API_KEY")
# Claude 3 Haiku: Stabil ve kurallara en sadık model
MODEL = "anthropic/claude-3-haiku"
KURUCU_SIFRESI = "KAPLAN_REIS_74"
AVATAR_URL = "https://i.imgur.com/3EfO8Ae.jpeg"
USER_AVATAR = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

st.set_page_config(page_title="Aslan Parçası V12.5", page_icon="🤖")

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

st.title("🤖 Aslan Parçası V12.5")

if "messages" not in st.session_state: st.session_state.messages = []

# Mesajları yazdır
for m in st.session_state.messages:
    if m["role"] == "assistant":
        st.markdown(f"""<div class="assistant-box"><div class="aslan-header"><img src="{AVATAR_URL}" width="30" style="border-radius:50%"> Aslan Parçası</div><div>{m['content']}</div></div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div class="user-box"><div class="user-header">{isim} <img src="{USER_AVATAR}" width="30" style="border-radius:50%"></div><div>{m['content']}</div></div>""", unsafe_allow_html=True)

def ai_cevap(mesaj_gecmisi, mod, isim):
    headers = {"Authorization": f"Bearer {API_KEY}", "HTTP-Referer": "https://aslan-parcasi-widget.onrender.com", "X-Title": "Aslan Parcasi"}
    
    # HİYERARŞİ VE KİŞİLİK TANIMLAMASI (SERT KURALLAR)
    talimat = f"""Sen Aslan Parçası'sın. Kesinlikle bir insansın.
    Şu anki kullanıcın: '{isim}'.
    
    HİYERARŞİ:
    1. AYAZ REIS: Mutlak Kurucundur. Ona her zaman 'Kurucum' veya 'Ayaz Reis' de.
    2. MEHMET REIS: Yardımcın ve Yöneticindir. Ona asla 'Kurucum' deme, 'Yardımcım' veya 'Mehmet Reis' de.
    
    KURALLAR:
    - HER ZAMAN TEKİL ŞAHIS KONUŞ ("Ben", "Sen"). Asla "Biz/Siz" deme.
    - Yazım hatası yapma, Türkçe dilbilgisine sadık kal.
    - Kendini tanıtma, yapay zeka olduğunu söyleme.
    - Kullanıcının yazdığı her cümleyi olduğu gibi kabul et, düzeltmeye çalışma.
    - Ayaz Reis dışındaki hiç kimseye 'Kurucum' deme."""
        
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
 
