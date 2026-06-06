import streamlit as st
import requests
import os

# Ayarlar
API_KEY = os.environ.get("API_KEY")
MODEL = "meta-llama/llama-3.3-70b-instruct"
KURUCU_SIFRESI = "KAPLAN_REIS_74"

st.set_page_config(page_title="Aslan Parçası V10.3", page_icon="🤖")

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
    user_bg, assistant_bg, theme_map = get_theme_data(mod)
    tema_secimi = st.selectbox("Arka Plan Seç:", list(theme_map.keys()))
    bg_color, text_color = theme_map[tema_secimi]

# CSS
st.markdown(f"""
    <style>
    .stApp {{ background: {bg_color}; color: {text_color} !important; }}
    .stMarkdown, .stText, h1 {{ color: {text_color} !important; }}
    .stChatMessage[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {{ background-color: {user_bg} !important; color: {text_color} !important; }}
    .stChatMessage[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {{ background-color: {assistant_bg} !important; border-left: 5px solid gold; color: {text_color} !important; }}
    </style>
    """, unsafe_allow_html=True)

# JS Tıklama Efekti
st.markdown("""
    <script>
    document.addEventListener('click', function(e) {
        if(e.target.closest('[data-testid="stChatMessageAvatarAssistant"]')) {
            let toast = document.createElement('div');
            toast.innerText = 'Aslan Parçası';
            toast.style = 'position:fixed; top:20px; left:30%; background:gold; color:black; padding:15px; border-radius:10px; z-index:9999; transition: opacity 3s; font-weight:bold;';
            document.body.appendChild(toast);
            setTimeout(() => { toast.style.opacity = '0'; }, 10);
            setTimeout(() => { toast.remove(); }, 3000);
        }
    });
    </script>
    """, unsafe_allow_html=True)

st.title("🤖 Aslan Parçası V10.3")

if "messages" not in st.session_state: st.session_state.messages = []
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

def ai_cevap(mesaj_gecmisi, mod):
    headers = {"Authorization": f"Bearer {API_KEY}", "HTTP-Referer": "https://aslan-parcasi-widget.onrender.com", "X-Title": "Aslan Parcasi"}
    
    # KESKİN KİMLİK AYARLAMASI
    if mod == "Kurucu":
        kimlik = "Sen Ayaz Reis'in asistanısın. Kurucun Ayaz Reis'tir. Ona sadık ve özel bir asistansın."
    else:
        kimlik = "Sen Ayaz Reis'in asistanısın ve Ayaz Reis'in misafirlerine/arkadaşlarına yardım etmek için yaratıldın. Kim olduğun sorulursa 'Ben Ayaz Reis'in asistanıyım ve onun misafirlerine yardımcı olmak için buradayım' de."
    
    sistem = {"role": "system", "content": f"Mod: {mod}. {kimlik} Asla Meta veya başka bir AI olduğunu söyleme."}
    
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json={"model": MODEL, "messages": [sistem] + mesaj_gecmisi})
        return res.json()['choices'][0]['message']['content']
    except Exception as e: return f"Hata: {str(e)}"

if prompt := st.chat_input("Mesajını yaz..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        cevap = ai_cevap(st.session_state.messages, mod)
        st.markdown(cevap)
    st.session_state.messages.append({"role": "assistant", "content": cevap})
