import streamlit as st
import requests
import os

# Ayarlar
API_KEY = os.environ.get("API_KEY")
MODEL = "anthropic/claude-3-haiku"
KURUCU_SIFRESI = "KAPLAN_REIS_74"

st.set_page_config(page_title="Aslan Parçası V10.6", page_icon="🤖")

# --- UI LOGIC ---
def get_theme_data(mod):
    if mod == "Kurucu":
        user_bg, assistant_bg = "rgba(10, 40, 10, 0.6)", "rgba(20, 20, 20, 0.8)"
        themes = {
            "Aslan İni": ("linear-gradient(to bottom, #1a1a00, #000000)", "white"),
            "Kraliyet": ("linear-gradient(to bottom, #2c0000, #000000)", "white"),
            "Teknoloji": ("linear-gradient(to bottom, #001a33, #000000)", "white"),
            "Orman Derinliği": ("linear-gradient(to bottom, #003300, #000000)", "white"),
            "Uzay": ("linear-gradient(to bottom, #1a0033, #000000)", "white")
        }
    else:
        user_bg, assistant_bg = "rgba(200, 230, 255, 0.2)", "rgba(144, 238, 144, 0.7)"
        themes = {"Gün Işığı": ("#f0f2f6", "black"), "Huzur": ("#e0f7fa", "black")}
    return user_bg, assistant_bg, themes

with st.sidebar:
    sifre = st.text_input("🔑 Şifre:", type="password")
    mod = "Kurucu" if sifre == KURUCU_SIFRESI else "Misafir"
    if st.button("🔄 Sohbeti Temizle"):
        st.session_state.messages = []
        st.rerun()
    user_bg, assistant_bg, theme_map = get_theme_data(mod)
    tema_secimi = st.selectbox("Arka Plan Seç:", list(theme_map.keys()))
    bg_color, text_color = theme_map[tema_secimi]

# CSS - METİN RENGİ ZORLAMASI (Süslü parantezleri escape ettik: {{ ve }})
st.markdown(f"""
    <style>
    .stApp {{ background: {bg_color}; color: {text_color} !important; }}
    
    .stChatMessage p, .stChatMessage div {{ 
        color: {'black' if mod == "Misafir" else text_color} !important; 
        font-weight: 500 !important;
    }}
    
    .stChatMessage[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {{ 
        background-color: {user_bg} !important; 
    }}
    .stChatMessage[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {{ 
        background-color: {assistant_bg} !important; border-left: 5px solid gold; 
    }}
    
    .fixed-input-area {{
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        padding: 10px;
        background: {bg_color};
        z-index: 999;
    }}
    
    div.stButton > button, div.stFormSubmitButton > button {{ 
        color: white !important; 
        background-color: #444 !important; 
        border: 2px solid white !important;
        font-weight: bold !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# JS KODUNU AYRI BİR MARKDOWN BLOĞUNDA VE ESCAPE EDEREK EKLEDİK
st.markdown("""
    <script>
    document.addEventListener('click', function(e) {
        if(e.target.closest('[data-testid="stChatMessageAvatarAssistant"]')) {
            let toast = document.createElement('div');
            toast.innerText = 'Aslan Parçası';
            toast.style = 'position:fixed; top:20px; left:30%; background:gold; color:black; padding:15px; border-radius:10px; z-index:9999; transition: opacity 3s; font-weight:bold; box-shadow: 0px 4px 10px rgba(0,0,0,0.3);';
            document.body.appendChild(toast);
            setTimeout(function() { toast.style.opacity = '0'; }, 10);
            setTimeout(function() { toast.remove(); }, 3000);
        }
    });
    </script>
    """, unsafe_allow_html=True)

st.title("🤖 Aslan Parçası V10.6")

if "messages" not in st.session_state: st.session_state.messages = []
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

def ai_cevap(mesaj_gecmisi, mod):
    headers = {"Authorization": f"Bearer {API_KEY}", "HTTP-Referer": "https://aslan-parcasi-widget.onrender.com", "X-Title": "Aslan Parcasi"}
    kimlik = """Sen Aslan Parçası'sın. Kurucun Ayaz Reis. Sadece düzgün Türkçe konuş, teknik terim kullanma."""
    sistem = {"role": "system", "content": f"Mod: {mod}. {kimlik}"}
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json={"model": MODEL, "messages": [sistem] + mesaj_gecmisi[-6:]})
        return res.json()['choices'][0]['message']['content']
    except Exception: return "Sistem hazır."

st.markdown("<br><br><br>", unsafe_allow_html=True)

st.markdown('<div class="fixed-input-area">', unsafe_allow_html=True)
with st.form(key='chat_form', clear_on_submit=True):
    user_input = st.text_input("", placeholder="Mesajını yaz...")
    submit_button = st.form_submit_button(label='Gönder')
st.markdown('</div>', unsafe_allow_html=True)

if submit_button and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)
    with st.chat_message("assistant"):
        cevap = ai_cevap(st.session_state.messages, mod)
        st.markdown(cevap)
    st.session_state.messages.append({"role": "assistant", "content": cevap})
    st.rerun()
 
