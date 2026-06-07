    import streamlit as st
import requests
import os
from duckduckgo_search import DDGS
from datetime import datetime, timedelta

# --- AYARLAR ---
API_KEY = os.environ.get("API_KEY")
MODEL = "anthropic/claude-3-haiku"
KURUCU_SIFRESI = "KAPLAN_REIS_74"
NIHAI_SIFRE = "NiHAi_-kuRucU-AyAz"
AVATAR_URL = "https://i.imgur.com/3EfO8Ae.jpeg"
USER_AVATAR = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
DOSYA_ADI = "sarki_id.txt"
MOD_DOSYASI = "mod_id.txt"
TEMA_KURUCU = "tema_kurucu.txt"
TEMA_MISAFIR = "tema_misafir.txt"
AYAZ_MODU_DOSYASI = "ayaz_modu.txt"

# --- KALICI DOSYA FONKSİYONLARI ---
def kaydet(dosya, deger):
    with open(dosya, "w") as f: f.write(deger.strip())

def oku(dosya):
    if os.path.exists(dosya):
        with open(dosya, "r") as f: return f.read().strip()
    return ""

def sil(dosya):
    if os.path.exists(dosya): os.remove(dosya)

# --- WEB ARAMA ---
def web_ara(sorgu):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(sorgu, max_results=3))
            return "Güncel bilgiler: " + "\n".join([r['body'] for r in results])
    except: return "İnternete şu an erişemiyorum Reis."

st.set_page_config(page_title="Aslan Parçası V17.1", page_icon="🦁")

# --- MOD YÖNETİMİ ---
is_admin = oku(MOD_DOSYASI) == "Kurucu"
ayaz_aktif = oku(AYAZ_MODU_DOSYASI) == "Aktif"
if "messages" not in st.session_state: st.session_state.messages = []
if "input_key" not in st.session_state: st.session_state.input_key = 0

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

# Temayı burada tanımlıyoruz ki dışarıda da erişilebilsin
_, theme_map = get_theme_data("Kurucu" if is_admin else "Misafir")

with st.sidebar:
    if not is_admin:
        sifre = st.text_input("🔑 Yönetici Şifresi:", type="password")
        if sifre == KURUCU_SIFRESI: kaydet(MOD_DOSYASI, "Kurucu"); st.rerun()
    else:
        st.success("✅ Yönetici Modu Aktif")
        isim = st.selectbox("👤 Kimsin Reis?", ["Mehmet Reis", "Ayaz Reis"])
        if isim == "Ayaz Reis":
            if not ayaz_aktif:
                nihai_sifre = st.text_input("👑 Nihai Şifre:", type="password")
                if st.button("Doğrula"):
                    if nihai_sifre == NIHAI_SIFRE: kaydet(AYAZ_MODU_DOSYASI, "Aktif"); st.rerun()
                    else: st.error("❌ Hatalı Şifre!")
            else: st.info("👑 Ayaz Reis Modu Aktif")
        else:
            if ayaz_aktif: sil(AYAZ_MODU_DOSYASI); st.rerun()

        tema_dosyasi = TEMA_KURUCU if is_admin else TEMA_MISAFIR
        kayitli_tema = oku(tema_dosyasi)
        if kayitli_tema not in theme_map: kayitli_tema = list(theme_map.keys())[0]
        tema_secimi = st.selectbox("Arka Plan:", list(theme_map.keys()), index=list(theme_map.keys()).index(kayitli_tema))
        if st.button("💾 Temayı Kaydet"): kaydet(tema_dosyasi, tema_secimi); st.rerun()
        
        if st.button("🚪 Çıkış Yap"): sil(MOD_DOSYASI); sil(AYAZ_MODU_DOSYASI); st.rerun()

    if st.button("🔄 Sohbeti Temizle"): st.session_state.messages = []; st.rerun()

    st.markdown("---")
    st.subheader("🎵 Müzik Motoru")
    kayitli_id = oku(DOSYA_ADI)
    yeni_id = st.text_input("YouTube Video ID'si:", value=kayitli_id)
    if st.button("💾 Kaydet ve Oynat"): kaydet(DOSYA_ADI, yeni_id); st.rerun()
    if st.button("🗑️ Sil"): sil(DOSYA_ADI); st.rerun()
    if kayitli_id: st.markdown(f'<iframe width="100%" height="200" src="https://www.youtube.com/embed/{kayitli_id}" frameborder="0" allow="autoplay"></iframe>', unsafe_allow_html=True)

# --- STYLE ---
tema_secimi = oku(TEMA_KURUCU if is_admin else TEMA_MISAFIR)
if tema_secimi not in theme_map: tema_secimi = list(theme_map.keys())[0]
bg_color, text_color = theme_map[tema_secimi]

st.markdown(f"""
    <style>
    .stApp {{ background: {bg_color}; color: {text_color} !important; }}
    .assistant-box {{ background-color: rgba(30, 30, 30, 0.9); padding: 15px; border-radius: 10px; border-left: 5px solid gold; margin-bottom: 10px; }}
    .user-box {{ background-color: rgba(128, 128, 128, 0.2); padding: 15px; border-radius: 10px; margin-bottom: 10px; text-align: right; }}
    .aslan-header {{ display: flex; align-items: center; gap: 10px; font-weight: bold; border-bottom: 1px solid gold; padding-bottom: 5px; margin-bottom: 5px; }}
    .user-header {{ display: flex; align-items: center; justify-content: flex-end; gap: 10px; font-weight: bold; margin-bottom: 8px; }}
    </style>
    """, unsafe_allow_html=True)

# --- AI CEVAP MOTORU ---
def ai_cevap(mesaj_gecmisi, mod, isim, kullanici_mesaji):
    turkiye_saati = (datetime.utcnow() + timedelta(hours=3)).strftime("%H:%M")
    headers = {"Authorization": f"Bearer {API_KEY}"}
    ek_bilgi = f"\n[Güncel Bilgi]: Şu an saat {turkiye_saati}."
    
    if any(k in kullanici_mesaji.lower() for k in ["hava", "hava durumu"]):
        if len(kullanici_mesaji.split()) < 3: return "Reis, hangi şehirde olduğunu yazmalısın."
        ek_bilgi += f"\n[İnternet]: {web_ara(kullanici_mesaji + ' hava durumu')}"
    elif any(k in kullanici_mesaji.lower() for k in ["ara", "çevir", "tercüme", "hesapla", "nedir"]):
        ek_bilgi += f"\n[İnternet]: {web_ara(kullanici_mesaji)}"
    
    if mod == "Kurucu":
        if isim == "Ayaz Reis" and ayaz_aktif:
            karakter = "Sen Ayaz Reis'in kurduğu neşeli, şakacı, samimi ve sadık bir asistansın."
        else:
            karakter = "Sen resmi, bilge, otoriter bir asistansın. Mehmet Reis'e karşı saygılı ve ciddi ol."
    else:
        karakter = "Sen samimi, doğal, enerjik ve arkadaş canlısı bir asistansın."
    
    talimat = f"{karakter} Adın Aslan Parçası. Kurucun Ayaz Reis, yöneticin Mehmet Reis. {ek_bilgi}"
    
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, 
                           json={"model": MODEL, "messages": [{"role": "system", "content": talimat}] + mesaj_gecmisi[-6:]})
        return res.json()['choices'][0]['message']['content']
    except: return "Sistem meşgul, Reis."

st.title("🤖 Aslan Parçası V17.1")

for m in st.session_state.messages:
    if m["role"] == "assistant":
        st.markdown(f'<div class="assistant-box"><div class="aslan-header"><img src="{AVATAR_URL}" width="30" style="border-radius:50%"> Aslan Parçası</div>{m["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="user-box"><div class="user-header">{isim if is_admin else "Ziyaretçi"} <img src="{USER_AVATAR}" width="30" style="border-radius:50%"></div>{m["content"]}</div>', unsafe_allow_html=True)

user_input = st.text_area("Mesajını yaz:", height=100, key=f"chat_input_{st.session_state.input_key}")
if st.button("🚀 Gönder"):
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        cevap = ai_cevap(st.session_state.messages, "Kurucu" if is_admin else "Misafir", isim if is_admin else "Ziyaretçi", user_input)
        st.session_state.messages.append({"role": "assistant", "content": cevap})
        st.session_state.input_key += 1
        st.rerun()
 
