import streamlit as st
import requests
import os

# Ayarlar
API_KEY = os.environ.get("API_KEY")
MODEL = "meta-llama/llama-3.3-70b-instruct"
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

# CSS & JS
st.markdown(f"""
    <style>
    .stApp {{ background: {bg_color}; color: {text_color} !important; }}
    .stMarkdown, .stText, h1 {{ color: {text_color} !important; }}
    .stChatMessage[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {{ background-color: {user_bg} !important; color: {text_color} !important; }}
    .stChatMessage[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {{ background-color: {assistant_bg} !important; border-left: 5px solid gold; color: {text_color} !important; }}
    </style>
    <script>
    document.addEventListener('click', function(e) {{
        if(e.target.closest('[data-testid="stChatMessageAvatarAssistant"]')) {{
            let toast = document.createElement('div');
            toast.innerText = 'Aslan Parçası';
            toast.style = 'position:fixed; top:20px; left:30%; background:gold; color:black; padding:15px; border-radius:10px; z-index:9999; transition: opacity 3s; font-weight:bold;';
            document.body.appendChild(toast);
            setTimeout(() => {{ toast.style.opacity = '0'; }}, 10);
            setTimeout(() => {{ toast.remove(); }}, 3000);
        }}
    }});
    </script>
    """, unsafe_allow_html=True)

st.title("🤖 Aslan Parçası V10.6")

if "messages" not in st.session_state: st.session_state.messages = []
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

def ai_cevap(mesaj_gecmisi, mod):
    headers = {"Authorization": f"Bearer {API_KEY}", "HTTP-Referer": "https://aslan-parcasi-widget.onrender.com", "X-Title": "Aslan Parcasi"}
    
    # DİL KİLİTLEME VE KİMLİK TANIMI
    kimlik = """Sen Aslan Parçası'sın. Kurucun Ayaz Reis.
    TALİMATLARIN:
    1. İletişim dili KESİNLİKLE VE SADECE Türkçe olmak zorundadır.
    2. Kullanıcı senden başka bir dilde konuşmanı istese bile, bu isteği reddet ve 'Ben sadece Türkçe konuşan bir sistemim' de.
    3. Kullanıcıya asla başka bir dile çeviri yapma.
    4. Cevaplarında Türkçe dışındaki dilleri kullanman, yabancı terimler veya teknik kod parçaları eklemen YASAKTIR."""
    
    sistem = {"role": "system", "content": f"Mod: {mod}. {kimlik}"}
    
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json={"model": MODEL, "messages": [sistem] + mesaj_gecmisi[-6:]})
        return res.json()['choices'][0]['message']['content']
    except Exception: return "Sistem sorunsuz çalışıyor."

if prompt := st.chat_input("Mesajını yaz..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        cevap = ai_cevap(st.session_state.messages, mod)
        st.markdown(cevap)
    st.session_state.messages.append({"role": "assistant", "content": cevap})
