import streamlit as st
import streamlit.components.v1 as components
import requests
import os
import json
import uuid
import firebase_admin
from firebase_admin import credentials, auth, firestore
# Tepe duyuru editörünü doğrudan app.py içine entegre ediyoruz
def render_tepe_editor_page(db, is_kurucu, get_global_announcement):
    # Setup page header
    st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;padding:10px 0;">
            <div style="background:#e67e22;border-radius:10px;width:42px;height:42px;display:flex;align-items:center;justify-content:center;box-shadow:0 0 15px rgba(230,126,34,0.4);">
                <span style="color:#fff;font-size:1.3rem;font-weight:900;">👑</span>
            </div>
            <div>
                <h1 style="margin:0;font-size:1.6rem;color:#fff;letter-spacing:-0.5px;">Tepe Duyuru Bandı Editörü</h1>
                <p style="margin:3px 0 0;font-size:0.8rem;color:#bdc3c7;">CapCut Premium Stili İnteraktif Tasarım Paneli</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_back, col_spacer = st.columns([2, 5])
    with col_back:
        if st.button("⬅️ Yönetici Paneline Dön", use_container_width=True):
            st.session_state.current_page = "admin_main"
            st.rerun()

    # Load from Firestore OR session state if existing
    if "temp_ann_settings" not in st.session_state:
        st.session_state.temp_ann_settings = get_global_announcement()
    
    ts = st.session_state.temp_ann_settings

    # Normalize state structure to avoid dictionary key errors in JavaScript
    keys_defaults = {
        "text": "YENİ TEPE DUYURUSU",
        "text_color": "#FFFFFF",
        "font": "sans-serif",
        "font_weight": "bold",
        "font_style": "normal",
        "text_decoration": "none",
        "opacity": 100,
        "displacement_x": 0,
        "displacement_y": 0,
        "size": 20,
        "rotation": 0,
        "align": "center",
        "bg_type": "none",
        "bg_color": "#111122",
        "bg_gradient_end": "#1a1a3a",
        "bg_image_url": "",
        "bg_opacity": 100,
        "padding_vertical": 10,
        "padding_horizontal": 15,
        "border_radius": 12,
        "glow_enabled": False,
        "glow_intensity": 50,
        "glow_color_mode": "auto",
        "glow_color_fixed": "#FFC000",
        "shadow_enabled": False,
        "shadow_intensity": 50,
        "shadow_color": "#000000",
        "animation_type": "none",
        "media_url": "",
        "media_align": "below",
        "media_size": 150,
        "char_colors": []
    }

    # Set fallbacks in active ts
    for k, v in keys_defaults.items():
        if k not in ts:
            ts[k] = v

    # Serialize active dict to JSON for JS initial load
    active_settings_json = json.dumps(ts, ensure_ascii=False)

    # 1. EXPANDER FOR SYSTEM DATA BRIDGE (Honest and extremely reliable sync mechanism)
    st.markdown("---")
    with st.expander("⚙️ Sistem Altyapı Veri Sinyali (Senkronizasyon)", expanded=False):
        st.write("Bu panel, interaktif stüdyodan gelen gerçek zamanlı tasarım güncellemelerini Firestore veri tabanına senkronize eder.")
        
        # Textarea to hold incoming JSON payload from Javascript component
        bridge_val = st.text_area(
            "Veri Sinyali (JSON)", 
            value=active_settings_json,
            placeholder="Sistem Veri Geri Bildirim Köprüsü",
            height=120,
            key="sys_bridge_payload"
        )
        
        col_s1, col_s2 = st.columns([1, 1])
        with col_s1:
            save_trigger = st.button("💾 GİZLİ_TETİKLEYİCİ_KAYDET", use_container_width=True, type="primary")
        with col_s2:
            update_self_trigger = st.button("🔄 Manuel Veriden Geri Yükle", use_container_width=True)

    # Handle explicit manual updates or hidden trigger click
    if save_trigger:
        try:
            parsed_payload = json.loads(bridge_val)
            # Match back defaults to guarantee no key misses in DB
            for k, v in keys_defaults.items():
                if k not in parsed_payload:
                    parsed_payload[k] = v
            # Save to Firestore
            db.collection("settings").document("global_announcement").set(parsed_payload)
            trigger_global_rerun(exclude_self=False)
            st.session_state.temp_ann_settings = parsed_payload
            st.toast("🚀 Değişiklikler başarıyla kaydedildi ve canlıya alındı!", icon="✅")
            st.rerun()
        except Exception as e:
            st.error(f"Kayıt Hatası: {e}")

    if update_self_trigger:
        try:
            parsed_payload = json.loads(bridge_val)
            st.session_state.temp_ann_settings = parsed_payload
            st.rerun()
        except Exception as e:
            st.error(f"Geri Yükleme Hatası: {e}")

    # UI HTML component code definition (Plain string replacing system template)
    html_studio_code = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- Load Tailwind CSS from official fast CDN -->
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Space Grotesk', sans-serif;
            background: #0d0d15;
            color: #f3f4f6;
            margin: 0;
            padding: 10px;
            overflow-x: hidden;
        }
        /* Beautiful custom scrollbar */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: #111119;
        }
        ::-webkit-scrollbar-thumb {
            background: #4b5563;
            border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #e67e22;
        }
        
        /* Keyframe Animations from app.py */
        @keyframes neonPulse {
          0%, 100% { opacity: 0.45; filter: brightness(0.85); }
          50% { opacity: 1; filter: brightness(1.2); }
        }
        @keyframes wiggle {
          0%, 100% { transform: translateY(0) rotate(0deg); }
          25% { transform: translateY(-4px) rotate(-1.5deg); }
          75% { transform: translateY(4px) rotate(1.5deg); }
        }
        @keyframes neonFlicker {
          0%, 19%, 21%, 23%, 25%, 54%, 56%, 100% { opacity: 1; }
          20%, 24%, 55% { opacity: 0.25; }
        }
        @keyframes rainbowShift {
          0% { filter: hue-rotate(0deg); }
          100% { filter: hue-rotate(360deg); }
        }
        @keyframes softPulse {
          0%, 100% { transform: scale(0.98); }
          50% { transform: scale(1.04); }
        }
        @keyframes blurFade {
          0%, 100% { filter: blur(0px); }
          50% { filter: blur(3px); }
        }
        .ann-animate-wiggle {
          display: inline-block;
          animation: wiggle 1.5s ease-in-out infinite;
        }
        .ann-animate-neon_pulse {
          display: inline-block;
          animation: neonPulse 2s infinite ease-in-out;
        }
        .ann-animate-neon_flicker {
          display: inline-block;
          animation: neonFlicker 3s infinite;
        }
        .ann-animate-rainbow {
          display: inline-block;
          animation: rainbowShift 6s infinite linear;
        }
        .ann-animate-pulse {
          display: inline-block;
          animation: softPulse 2.5s infinite ease-in-out;
        }
        .ann-animate-blur_fade {
          display: inline-block;
          animation: blurFade 3s infinite ease-in-out;
        }
        
        .active-tab-btn {
            background: linear-gradient(135deg, #e67e22, #d35400);
            color: white;
            box-shadow: 0 4px 12px rgba(230,126,34,0.3);
        }
    </style>
</head>
<body class="p-2 md:p-4">

    <!-- Primary Grid Layout -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        
        <!-- Left Side: Interactive Hand Draggable device Mockup Simulator -->
        <div class="lg:col-span-5 bg-gray-900 border border-gray-800 rounded-xl p-4 shadow-2xl relative">
            <div class="flex items-center justify-between mb-2">
                <div class="flex items-center gap-2">
                    <span class="text-xl">📱</span>
                    <span class="font-bold text-orange-400 text-sm tracking-wide">ELİNİZLE SÜRÜKLEYİN</span>
                </div>
                <!-- Dynamic floating position tag badge -->
                <div id="badge-coordinates" class="bg-gray-800 border border-orange-500 rounded px-2 py-1 text-xs text-orange-400 font-bold">
                    📍 Konum: X: 0 | Y: 0
                </div>
            </div>
            <p class="text-xs text-gray-400 mb-3 leading-tight">Yazıyı <b>parmağınızla/mouse ile tutup sürükleyerek</b> en ideal konuma getirebilirsiniz.</p>
            
            <!-- Phone mockup display box -->
            <div id="phone-container" class="relative w-full rounded-xl overflow-visible p-4 border-2 border-orange-500" style="min-height: 500px; background: radial-gradient(circle at top, #2e0000 0%, #110000 65%, #050000 100%);">
                
                <!-- StatusBar -->
                <div class="flex justify-between items-center text-xs opacity-40 font-bold text-white mb-6 select-none pointer-events-none">
                    <span>Turkcell LTE</span>
                    <span>17:57 %18.1 🔋</span>
                </div>
                
                <!-- Drag Container Box -->
                <div id="drag-stage-element" class="relative w-full overflow-visible z-50 cursor-grab active:cursor-grabbing select-none" style="min-height: 50px;">
                    <!-- Inner customized custom banner -->
                    <div id="live-banner-overlay" class="w-full"></div>
                </div>
                
                <!-- Background Mock App Layout Elements -->
                <div class="relative z-10 pointer-events-none select-none opacity-40 text-left mt-8">
                    <h1 class="text-2xl font-black text-white leading-tight">🤖 Kaplan Parçası V18.1</h1>
                    <p class="text-xs text-gray-400 mt-1 mb-6">Müstakbel Şirket bünyesinde geliştirilen yapay zeka platformu.</p>
                    
                    <div class="w-10 h-10 rounded-full border border-orange-500 bg-gray-800 flex items-center justify-center text-lg text-white mb-6">
                        🔔
                    </div>
                    
                    <div class="flex flex-col gap-2 mb-4">
                        <label class="text-gray-400 text-xs font-bold uppercase tracking-wider">Mesajını yaz:</label>
                        <div class="w-full h-16 rounded border border-gray-700 bg-gray-900 bg-opacity-30"></div>
                    </div>
                    
                    <div class="px-4 py-2 rounded-lg border border-gray-700 bg-gray-800 bg-opacity-50 text-xs text-white font-bold w-max">
                        <span>✉ Gönder</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Right Side: Beautiful tabs formatting panel -->
        <div class="lg:col-span-7 bg-gray-900 border border-gray-800 rounded-xl shadow-2xl overflow-hidden">
            
            <!-- Studio Tab Controls Headers -->
            <div class="bg-gray-950 p-2 border-b border-gray-800 flex overflow-x-auto gap-1">
                <button type="button" class="tab-btn active-tab-btn flex-none px-3 py-2 rounded-lg text-xs font-bold transition-all" onclick="showTab('yazi')">📝 Yazı & Biçim</button>
                <button type="button" class="tab-btn text-gray-400 hover:text-white hover:bg-gray-800 flex-none px-3 py-2 rounded-lg text-xs font-bold transition-all" onclick="showTab('konum')">📐 Konum & Boyut</button>
                <button type="button" class="tab-btn text-gray-400 hover:text-white hover:bg-gray-800 flex-none px-3 py-2 rounded-lg text-xs font-bold transition-all" onclick="showTab('arka')">🖼️ Arka Plan</button>
                <button type="button" class="tab-btn text-gray-400 hover:text-white hover:bg-gray-800 flex-none px-3 py-2 rounded-lg text-xs font-bold transition-all" onclick="showTab('efekt')">✨ Neon & Gölge</button>
                <button type="button" class="tab-btn text-gray-400 hover:text-white hover:bg-gray-800 flex-none px-3 py-2 rounded-lg text-xs font-bold transition-all" onclick="showTab('medya')">📷 Medya / GIF</button>
            </div>

            <!-- Tab Contents Area -->
            <div class="p-4 space-y-4">
                
                <!-- TAB 1: Yazı & Biçim -->
                <div id="tab-yazi" class="tab-content block space-y-4">
                    <div>
                        <label class="block text-xs font-bold text-gray-400 uppercase tracking-wide mb-1">Tepe Duyuru Metni</label>
                        <textarea id="val-text" rows="3" class="w-full bg-gray-950 border border-gray-800 rounded px-3 py-2 text-sm text-white focus:outline-none focus:border-orange-500" placeholder="Tepe duyurusu içeriğini buraya girin..."></textarea>
                    </div>
                    
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="block text-xs font-bold text-gray-400 uppercase tracking-wide mb-1">Yazı Tipi (Font)</label>
                            <select id="val-font" class="w-full bg-gray-950 border border-gray-800 rounded px-2 py-1.5 text-xs text-white focus:outline-none focus:border-orange-500">
                                <option value="sans-serif">System Sans-serif</option>
                                <option value="Space Grotesk">Space Grotesk</option>
                                <option value="Cinzel">Cinzel (Klasik)</option>
                                <option value="monospace">Monospace (Terminal)</option>
                                <option value="cursive">Cursive (El Yazısı)</option>
                                <option value="Arial">Arial</option>
                                <option value="Impact">Impact (Kalın Manşet)</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-gray-400 uppercase tracking-wide mb-1">Varsayılan Yazı Rengi</label>
                            <div class="flex gap-2">
                                <input id="val-text_color" type="color" class="h-8 w-12 bg-gray-950 border border-gray-800 rounded cursor-pointer">
                                <input id="val-text_color_hex" type="text" class="w-full bg-gray-950 border border-gray-800 rounded px-2 text-xs text-white focus:outline-none focus:border-orange-500" style="text-transform:uppercase;">
                            </div>
                        </div>
                    </div>

                    <div class="grid grid-cols-3 gap-3">
                        <div>
                            <label class="block text-xs font-bold text-gray-400 uppercase tracking-wide mb-1">Yazı Kalınlığı</label>
                            <select id="val-font_weight" class="w-full bg-gray-950 border border-gray-800 rounded px-2 py-1.5 text-xs text-white focus:outline-none">
                                <option value="bold">Bold (Kalın)</option>
                                <option value="normal">Normal (İnce)</option>
                                <option value="bolder">Bolder</option>
                                <option value="900">Black 900</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-gray-400 uppercase tracking-wide mb-1">Eğiklik (Style)</label>
                            <select id="val-font_style" class="w-full bg-gray-950 border border-gray-800 rounded px-2 py-1.5 text-xs text-white focus:outline-none">
                                <option value="normal">Normal (Dik)</option>
                                <option value="italic">Italic (Eğik)</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-gray-400 uppercase tracking-wide mb-1">Süsleme (Decor)</label>
                            <select id="val-text_decoration" class="w-full bg-gray-950 border border-gray-800 rounded px-2 py-1.5 text-xs text-white focus:outline-none">
                                <option value="none">None (Yok)</option>
                                <option value="underline">Underline (Alt Çizgili)</option>
                                <option value="line-through">Line-Through</option>
                            </select>
                        </div>
                    </div>

                    <div class="bg-gray-950 border border-orange-500/20 rounded-lg p-3 space-y-3">
                        <span class="text-xs font-bold text-orange-400">🎨 HARF BOYAMA / KELİME BOYAMA</span>
                        <p class="text-[11px] text-gray-400 leading-tight">Yazmış olduğunuz metin içerisindeki belirli bir kelimeyi veya harfleri farklı ve özel bir renkle boyayın!</p>
                        
                        <div class="flex gap-2">
                            <input id="paint-word-input" type="text" class="w-1/2 bg-gray-900 border border-gray-800 rounded px-3 py-1.5 text-xs text-white placeholder-gray-500" placeholder="Kelime örn: YENİ">
                            <div class="flex items-center gap-1.5">
                                <input id="paint-color-picker" type="color" value="#ffd700" class="h-8 w-10 bg-gray-900 border border-gray-800 rounded cursor-pointer">
                                <button type="button" class="bg-orange-600 hover:bg-orange-500 text-white rounded px-3 py-1.5 text-xs font-bold transition-colors" onclick="paintCustomWord()">Boya</button>
                            </div>
                        </div>
                        
                        <div class="flex gap-2 justify-end">
                            <button type="button" class="text-xs bg-gray-800 hover:bg-gray-700 text-gray-300 rounded px-3 py-1 transition-colors" onclick="resetCharColors()">Özel Renkleri Temizle 🔄</button>
                        </div>
                    </div>
                </div>

                <!-- TAB 2: Konum & Boyut -->
                <div id="tab-konum" class="tab-content hidden space-y-4">
                    <div>
                        <div class="flex justify-between items-center mb-1">
                            <label class="text-xs font-bold text-gray-400 uppercase tracking-wide">Yazı Boyutu (px)</label>
                            <span id="label-size" class="text-xs text-orange-400 font-bold">20px</span>
                        </div>
                        <input id="val-size" type="range" class="w-full" min="8" max="100" step="1">
                    </div>
                    <div>
                        <div class="flex justify-between items-center mb-1">
                            <label class="text-xs font-bold text-gray-400 uppercase tracking-wide">X Ekseni Kaydırma (Horiz)</label>
                            <span id="label-displacement_x" class="text-xs text-orange-400 font-bold">0px</span>
                        </div>
                        <input id="val-displacement_x" type="range" class="w-full" min="-300" max="300" step="1">
                    </div>
                    <div>
                        <div class="flex justify-between items-center mb-1">
                            <label class="text-xs font-bold text-gray-400 uppercase tracking-wide">Y Ekseni Kaydırma (Vertic)</label>
                            <span id="label-displacement_y" class="text-xs text-orange-400 font-bold">0px</span>
                        </div>
                        <input id="val-displacement_y" type="range" class="w-full" min="-300" max="300" step="1">
                    </div>
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <div class="flex justify-between items-center mb-1">
                                <label class="text-xs font-bold text-gray-400 uppercase tracking-wide">Döndürme Açısı (Derece)</label>
                                <span id="label-rotation" class="text-xs text-orange-400 font-bold">0°</span>
                            </div>
                            <input id="val-rotation" type="range" class="w-full" min="-180" max="180" step="1">
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-gray-400 uppercase tracking-wide mb-1">Yazı Saydamlığı (%)</label>
                            <input id="val-opacity" type="range" class="w-full" min="10" max="100" step="5">
                        </div>
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-gray-400 uppercase tracking-wide mb-1">Yazı Hizalama (Align)</label>
                        <select id="val-align" class="w-full bg-gray-950 border border-gray-800 rounded px-2 py-1.5 text-xs text-white">
                            <option value="center">Center / Ortada</option>
                            <option value="left">Left / Sola Yaslı</option>
                            <option value="right">Right / Sağa Yaslı</option>
                        </select>
                    </div>
                </div>

                <!-- TAB 3: Arka Plan -->
                <div id="tab-arka" class="tab-content hidden space-y-4">
                    <div>
                        <label class="block text-xs font-bold text-gray-400 uppercase tracking-wide mb-1">Arka Plan Yapısı (Type)</label>
                        <select id="val-bg_type" class="w-full bg-gray-950 border border-gray-800 rounded px-2 py-1.5 text-xs text-white focus:outline-none" onchange="toggleBackgroundControls(this.value)">
                            <option value="none">None (Yok)</option>
                            <option value="flat">Flat (Düz Renk)</option>
                            <option value="gradient">Gradient (İki Renkli Geçiş)</option>
                            <option value="image">Image (Görsel / Resimli Arka Plan)</option>
                        </select>
                    </div>

                    <!-- Flat & Gradient controls -->
                    <div id="wrapper-bg-colors" class="hidden grid grid-cols-2 gap-4">
                        <div>
                            <label id="lbl-bg_color" class="block text-xs font-bold text-gray-400 uppercase tracking-wide mb-1">Arka Plan Rengi</label>
                            <input id="val-bg_color" type="color" class="h-8 w-full bg-gray-950 border border-gray-800 rounded cursor-pointer">
                        </div>
                        <div id="wrapper-bg-gradient-end" class="hidden">
                            <label class="block text-xs font-bold text-gray-400 uppercase tracking-wide mb-1">Geçiş Bitiş Rengi</label>
                            <input id="val-bg_gradient_end" type="color" class="h-8 w-full bg-gray-950 border border-gray-800 rounded cursor-pointer">
                        </div>
                    </div>

                    <!-- Image URL controls -->
                    <div id="wrapper-bg-image" class="hidden space-y-2">
                        <div>
                            <label class="block text-xs font-bold text-gray-400 uppercase tracking-wide mb-1">Görsel / Resim Linki (URL)</label>
                            <input id="val-bg_image_url" type="text" class="w-full bg-gray-950 border border-gray-800 rounded px-3 py-1.5 text-xs text-white focus:outline-none" placeholder="Resim linkini yapıştırın...">
                        </div>
                        <div>
                            <div class="flex justify-between items-center mb-1">
                                <label class="text-xs font-bold text-gray-400 uppercase tracking-wide">Görsel Saydamlığı (%)</label>
                                <span id="label-bg_opacity" class="text-xs text-orange-400 font-bold">100%</span>
                            </div>
                            <input id="val-bg_opacity" type="range" class="w-full" min="10" max="100" step="5">
                        </div>
                    </div>

                    <div class="grid grid-cols-3 gap-3">
                        <div>
                            <div class="flex justify-between items-center mb-1">
                                <label class="text-[10px] font-bold text-gray-400 uppercase">Dikey Padding</label>
                                <span id="label-padding_vertical" class="text-[10px] text-orange-400 font-bold">10px</span>
                            </div>
                            <input id="val-padding_vertical" type="range" class="w-full" min="0" max="100" step="1">
                        </div>
                        <div>
                            <div class="flex justify-between items-center mb-1">
                                <label class="text-[10px] font-bold text-gray-400 uppercase">Yatay Padding</label>
                                <span id="label-padding_horizontal" class="text-[10px] text-orange-400 font-bold">15px</span>
                            </div>
                            <input id="val-padding_horizontal" type="range" class="w-full" min="0" max="100" step="1">
                        </div>
                        <div>
                            <div class="flex justify-between items-center mb-1">
                                <label class="text-[10px] font-bold text-gray-400 uppercase">Köşe Eğimi</label>
                                <span id="label-border_radius" class="text-[10px] text-orange-400 font-bold">12px</span>
                            </div>
                            <input id="val-border_radius" type="range" class="w-full" min="0" max="50" step="1">
                        </div>
                    </div>
                </div>

                <!-- TAB 4: Neon & Gölge -->
                <div id="tab-efekt" class="tab-content hidden space-y-4">
                    <div class="bg-gray-950 p-3 rounded-lg border border-gray-850 space-y-3">
                        <div class="flex items-center justify-between">
                            <label class="text-xs font-bold text-gray-400 uppercase tracking-wide flex items-center gap-2">
                                <input id="checkbox-glow_enabled" type="checkbox" class="h-4 w-4 rounded text-orange-500 focus:ring-0 cursor-pointer" onchange="toggleGlowSection(this.checked)">
                                🌟 NEON PARILDAMA AKTİF
                            </label>
                        </div>
                        
                        <div id="wrapper-glow-controls" class="hidden space-y-3 transition-opacity duration-200">
                            <div>
                                <div class="flex justify-between items-center mb-1">
                                    <label class="text-xs text-gray-400">Neon Şiddeti & Yayılımı</label>
                                    <span id="label-glow_intensity" class="text-xs text-orange-400 font-bold">50</span>
                                </div>
                                <input id="val-glow_intensity" type="range" class="w-full" min="5" max="150" step="5">
                            </div>
                            <div class="grid grid-cols-2 gap-4">
                                <div>
                                    <label class="block text-xs text-gray-400 mb-1">Neon Renk Modu</label>
                                    <select id="val-glow_color_mode" class="w-full bg-gray-900 border border-gray-800 rounded px-2 py-1.5 text-xs text-white" onchange="toggleGlowFixedControl(this.value)">
                                        <option value="auto">Auto (Yazı Renginden)</option>
                                        <option value="fixed">Fixed (Sabit Seçilen Renk)</option>
                                    </select>
                                </div>
                                <div id="wrapper-glow-fixed" class="hidden">
                                    <label class="block text-xs text-gray-400 mb-1">Sabit Neon Rengi</label>
                                    <input id="val-glow_color_fixed" type="color" class="h-8 w-full bg-gray-900 border border-gray-800 rounded cursor-pointer">
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="bg-gray-950 p-3 rounded-lg border border-gray-850 space-y-3">
                        <div class="flex items-center justify-between">
                            <label class="text-xs font-bold text-gray-400 uppercase tracking-wide flex items-center gap-2">
                                <input id="checkbox-shadow_enabled" type="checkbox" class="h-4 w-4 rounded text-orange-500 focus:ring-0 cursor-pointer" onchange="toggleShadowSection(this.checked)">
                                🌓 GÖLGE EFEKTİ AKTİF
                            </label>
                        </div>
                        
                        <div id="wrapper-shadow-controls" class="hidden space-y-3">
                            <div>
                                <div class="flex justify-between items-center mb-1">
                                    <label class="text-xs text-gray-400">Gölge Yoğunluğu / Uzaklığı</label>
                                    <span id="label-shadow_intensity" class="text-xs text-orange-400 font-bold">50</span>
                                </div>
                                <input id="val-shadow_intensity" type="range" class="w-full" min="5" max="100" step="5">
                            </div>
                            <div>
                                <label class="block text-xs text-gray-450 mb-1">Gölge Rengi</label>
                                <input id="val-shadow_color" type="color" value="#000000" class="h-8 w-full bg-gray-900 border border-gray-805 rounded cursor-pointer">
                            </div>
                        </div>
                    </div>

                    <div>
                        <label class="block text-xs font-bold text-gray-400 uppercase tracking-wide mb-1">Canlı Yazı Animasyonu</label>
                        <select id="val-animation_type" class="w-full bg-gray-950 border border-gray-800 rounded px-2 py-1.5 text-xs text-white focus:outline-none">
                            <option value="none">None (Sabit Yazı)</option>
                            <option value="pulse">Pulse (Yavaş Dalgalanma)</option>
                            <option value="wiggle">Wiggle (Dans Eden Harfler)</option>
                            <option value="neon_pulse">Neon Pulse (Neon Sönme/Kısılma)</option>
                            <option value="neon_flicker">Neon Flicker (Bohem Neon Titremesi)</option>
                            <option value="rainbow">Rainbow (Renk Değiştiren Çılgın Renkler)</option>
                            <option value="blur_fade">Blur Fade (Zarif Odak Değişimi)</option>
                        </select>
                    </div>
                </div>

                <!-- TAB 5: Görsel & Medya -->
                <div id="tab-medya" class="tab-content hidden space-y-4">
                    <div>
                        <label class="block text-xs font-bold text-gray-400 uppercase tracking-wide mb-1">Ek Görsel / GIF Linki (URL)</label>
                        <input id="val-media_url" type="text" class="w-full bg-gray-950 border border-gray-800 rounded px-3 py-1.5 text-xs text-white focus:outline-none focus:border-orange-500" placeholder="https://site.com/media.gif">
                    </div>

                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="block text-xs font-bold text-gray-400 uppercase tracking-wide mb-1">Medya Konumu</label>
                            <select id="val-media_align" class="w-full bg-gray-950 border border-gray-800 rounded px-2 py-1.5 text-xs text-white">
                                <option value="below">Below (Yazının Altında)</option>
                                <option value="above">Above (Yazının Üstünde)</option>
                                <option value="left">Left (Sola Yaslı Yanda)</option>
                                <option value="right">Right (Sağa Yaslı Yanda)</option>
                            </select>
                        </div>
                        <div>
                            <div class="flex justify-between items-center mb-1">
                                <label class="text-xs font-bold text-gray-400 uppercase tracking-wide">Medya Genişliği (px)</label>
                                <span id="label-media_size" class="text-xs text-orange-400 font-bold">150px</span>
                            </div>
                            <input id="val-media_size" type="range" class="w-full" min="20" max="500" step="5">
                        </div>
                    </div>
                </div>

            </div>

            <!-- Action Controls bar at control deck bottom -->
            <div class="bg-gray-950 p-4 border-t border-gray-800 flex items-center justify-between gap-4">
                <p class="text-[10px] text-gray-500 max-w-[50%] leading-tight font-sans">Canlıya kaydetmek için aşağıdaki butona basın!</p>
                <button type="button" class="bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-500 hover:to-red-500 text-white text-xs font-black uppercase px-6 py-3 rounded-lg shadow-lg tracking-wider transition-all transform hover:scale-[1.03] active:scale-[0.98]" onclick="publishToLive()">
                    🚀 CANLIYA KAYDET VE YAYINLA
                </button>
            </div>

        </div>

    </div>

    <!-- JavaScript State logic and dynamic update bridge -->
    <script>
        // Pre-loaded initial state from Firestore
        let state = JSON.parse('__ACTIVE_SETTINGS_JSON__');
        
        // Tab system
        function showTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('block'));
            
            document.getElementById('tab-' + tabId).classList.add('block');
            document.getElementById('tab-' + tabId).classList.remove('hidden');
            
            // Highlight button
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('active-tab-btn');
                btn.classList.add('text-gray-400', 'hover:text-white', 'hover:bg-gray-800');
            });
            
            // Find clicked button
            const activeBtn = Array.from(document.querySelectorAll('.tab-btn')).find(btn => btn.getAttribute('onclick').includes(tabId));
            if (activeBtn) {
                activeBtn.classList.add('active-tab-btn');
                activeBtn.classList.remove('text-gray-400', 'hover:text-white', 'hover:bg-gray-800');
            }
        }

        // Sync inputs from State
        function loadSyncStateIntoUI() {
            document.getElementById('val-text').value = state.text;
            document.getElementById('val-font').value = state.font;
            document.getElementById('val-text_color').value = state.text_color;
            document.getElementById('val-text_color_hex').value = state.text_color.toUpperCase();
            document.getElementById('val-font_weight').value = state.font_weight;
            document.getElementById('val-font_style').value = state.font_style;
            document.getElementById('val-text_decoration').value = state.text_decoration;
            
            document.getElementById('val-size').value = state.size;
            document.getElementById('val-displacement_x').value = state.displacement_x;
            document.getElementById('val-displacement_y').value = state.displacement_y;
            document.getElementById('val-rotation').value = state.rotation;
            document.getElementById('val-opacity').value = state.opacity;
            document.getElementById('val-align').value = state.align;
            
            document.getElementById('val-bg_type').value = state.bg_type;
            document.getElementById('val-bg_color').value = state.bg_color;
            document.getElementById('val-bg_gradient_end').value = state.bg_gradient_end;
            document.getElementById('val-bg_image_url').value = state.bg_image_url;
            document.getElementById('val-bg_opacity').value = state.bg_opacity;
            
            document.getElementById('val-padding_vertical').value = state.padding_vertical;
            document.getElementById('val-padding_horizontal').value = state.padding_horizontal;
            document.getElementById('val-border_radius').value = state.border_radius;
            
            document.getElementById('checkbox-glow_enabled').checked = state.glow_enabled;
            document.getElementById('val-glow_intensity').value = state.glow_intensity;
            document.getElementById('val-glow_color_mode').value = state.glow_color_mode;
            document.getElementById('val-glow_color_fixed').value = state.glow_color_fixed;
            
            document.getElementById('checkbox-shadow_enabled').checked = state.shadow_enabled;
            document.getElementById('val-shadow_intensity').value = state.shadow_intensity;
            document.getElementById('val-shadow_color').value = state.shadow_color;
            
            document.getElementById('val-animation_type').value = state.animation_type;
            document.getElementById('val-media_url').value = state.media_url;
            document.getElementById('val-media_align').value = state.media_align;
            document.getElementById('val-media_size').value = state.media_size;
            
            // Adjust conditional UI containers
            toggleBackgroundControls(state.bg_type);
            toggleGlowSection(state.glow_enabled);
            toggleGlowFixedControl(state.glow_color_mode);
            toggleShadowSection(state.shadow_enabled);
            
            updateLabels();
        }

        function updateLabels() {
            document.getElementById('label-size').textContent = state.size + 'px';
            document.getElementById('label-displacement_x').textContent = state.displacement_x + 'px';
            document.getElementById('label-displacement_y').textContent = state.displacement_y + 'px';
            document.getElementById('label-rotation').textContent = state.rotation + '°';
            document.getElementById('label-bg_opacity').textContent = state.bg_opacity + '%';
            document.getElementById('label-padding_vertical').textContent = state.padding_vertical + 'px';
            document.getElementById('label-padding_horizontal').textContent = state.padding_horizontal + 'px';
            document.getElementById('label-border_radius').textContent = state.border_radius + 'px';
            document.getElementById('label-glow_intensity').textContent = state.glow_intensity;
            document.getElementById('label-shadow_intensity').textContent = state.shadow_intensity;
            document.getElementById('label-media_size').textContent = state.media_size + 'px';
            
            document.getElementById('badge-coordinates').textContent = `📍 X: ${state.displacement_x}px | Y: ${state.displacement_y}px`;
        }

        function toggleBackgroundControls(type) {
            const wrapperColors = document.getElementById('wrapper-bg-colors');
            const wrapperGradientEnd = document.getElementById('wrapper-bg-gradient-end');
            const wrapperImage = document.getElementById('wrapper-bg-image');
            const labelBgColor = document.getElementById('lbl-bg_color');
            
            if (type === 'none') {
                wrapperColors.classList.add('hidden');
                wrapperImage.classList.add('hidden');
            } else if (type === 'flat') {
                wrapperColors.classList.remove('hidden');
                wrapperGradientEnd.classList.add('hidden');
                wrapperImage.classList.add('hidden');
                labelBgColor.textContent = 'Arka Plan Rengi';
            } else if (type === 'gradient') {
                wrapperColors.classList.remove('hidden');
                wrapperGradientEnd.classList.remove('hidden');
                wrapperImage.classList.add('hidden');
                labelBgColor.textContent = 'Başlangıç Rengi';
            } else if (type === 'image') {
                wrapperColors.classList.add('hidden');
                wrapperImage.classList.remove('hidden');
            }
        }

        // Compile animation properties safely
        function compileBannerHTML() {
            const ann_text = state.text;
            const size = state.size;
            const font_family = state["font"];
            const align = state.align;
            const font_weight = state.font_weight;
            const font_style = state.font_style;
            const text_decoration = state.text_decoration;
            const opacity = state.opacity / 100.0;
            
            const displacement_x = state.displacement_x;
            const displacement_y = state.displacement_y;
            const rotation = state.rotation;
            
            const glow_enabled = state.glow_enabled;
            const glow_int = state.glow_intensity;
            const glow_color_mode = state.glow_color_mode;
            const glow_color_fixed = state.glow_color_fixed;
            
            const shadow_enabled = state.shadow_enabled;
            const shadow_int = state.shadow_intensity;
            const shadow_color = state.shadow_color;
            
            const bg_type = state.bg_type;
            const bg_color = state.bg_color;
            const bg_end = state.bg_gradient_end;
            const bg_image_url = state.bg_image_url;
            const bg_opacity = state.bg_opacity / 100.0;
            
            const padding_v = state.padding_vertical;
            const padding_h = state.padding_horizontal;
            const border_radius = state.border_radius;
            
            const media_url = state.media_url;
            const media_size = state.media_size;
            const media_align = state.media_align;
            
            const animation_type = state.animation_type;
            const char_colors = state.char_colors || [];
            const text_color_global = state.text_color;

            // Generate characters
            let rendered_chars = [];
            let chars = Array.from(ann_text);
            
            for (let char_idx = 0; char_idx < chars.length; char_idx++) {
                let char = chars[char_idx];
                let char_color = text_color_global;
                if (char_idx < char_colors.length && char_colors[char_idx]) {
                    char_color = char_colors[char_idx];
                }
                
                let local_glow_color = char_color;
                if (glow_color_mode === 'fixed') {
                    local_glow_color = glow_color_fixed;
                }
                
                let glow_css = "";
                let glow_val_style = "";
                if (glow_enabled) {
                    let blur_1 = glow_int * 0.2;
                    let blur_2 = glow_int * 0.4;
                    glow_css = `0 0 ${blur_1.toFixed(1)}px ${local_glow_color}, 0 0 ${blur_2.toFixed(1)}px ${local_glow_color}`;
                    glow_val_style = `--glow-color: ${local_glow_color}; --gl-blur: ${(glow_int * 0.4).toFixed(1)}px;`;
                }
                
                let shadow_css = "";
                if (shadow_enabled) {
                    let off = shadow_int * 0.08;
                    let blur_s = shadow_int * 0.16;
                    shadow_css = `${off.toFixed(1)}px ${off.toFixed(1)}px ${blur_s.toFixed(1)}px ${shadow_color}`;
                }
                
                let combined_shadows = [glow_css, shadow_css].filter(Boolean).join(", ");
                let shadow_style = combined_shadows ? `text-shadow: ${combined_shadows};` : "";
                
                let italic_bold_style = `font-weight: ${font_weight}; font-style: ${font_style}; text-decoration: ${text_decoration};`;
                let anim_delay_style = (animation_type === 'wiggle') ? `animation-delay: ${(char_idx * 0.08).toFixed(2)}s;` : "";
                
                let span_class = "";
                if (['neon_pulse', 'wiggle', 'neon_flicker', 'rainbow', 'pulse', 'blur_fade'].includes(animation_type)) {
                    span_class = `ann-animate-${animation_type}`;
                }
                
                let html_item = `<span class="${span_class}" style="display: inline-block; white-space: pre-wrap; color: ${char_color}; ${glow_val_style} ${shadow_style} ${italic_bold_style} ${anim_delay_style}">${char}</span>&#8203;`;
                rendered_chars.push(html_item);
            }
            
            let ann_content_html = rendered_chars.join("");
            
            // Media
            let media_html = "";
            if (media_url) {
                media_html = `<img src="${media_url}" style="width: ${media_size}px; height: auto; border-radius: 8px; margin: 8px; vertical-align: middle; max-width: 100%; box-shadow: 0 4px 12px rgba(0,0,0,0.4);" />`;
            }
            
            let body_html = `<div>${ann_content_html}</div>`;
            if (media_html) {
                if (media_align === 'above') {
                    body_html = `<div style="margin-bottom: 8px;">${media_html}</div><div>${ann_content_html}</div>`;
                } else if (media_align === 'below') {
                    body_html = `<div>${ann_content_html}</div><div style="margin-top: 8px;">${media_html}</div>`;
                } else if (media_align === 'left') {
                    body_html = `<div style="display: flex; align-items: center; justify-content: ${align}; flex-wrap: wrap; gap: 15px;"><div>${media_html}</div><div style="flex: 1; text-align: ${align};">${ann_content_html}</div></div>`;
                } else if (media_align === 'right') {
                    body_html = `<div style="display: flex; align-items: center; justify-content: ${align}; flex-wrap: wrap; gap: 15px;"><div style="flex: 1; text-align: ${align};">${ann_content_html}</div><div>${media_html}</div></div>`;
                }
            }
            
            // Background
            let bg_css = "background: transparent; border: none; padding: 0;";
            if (bg_type === 'flat') {
                bg_css = `background: ${bg_color}; border: 1px solid rgba(255,255,255,0.1); border-radius: ${border_radius}px; padding: ${padding_v}px ${padding_h}px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.25);`;
            } else if (bg_type === 'gradient') {
                bg_css = `background: linear-gradient(135deg, ${bg_color}, ${bg_end}); border: 1px solid rgba(255,255,255,0.15); border-radius: ${border_radius}px; padding: ${padding_v}px ${padding_h}px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.25);`;
            } else if (bg_type === 'image') {
                let overlay_op = 1.0 - bg_opacity;
                bg_css = `background: linear-gradient(rgba(17,17,34,${overlay_op.toFixed(2)}), rgba(17,17,34,${overlay_op.toFixed(2)})), url('${bg_image_url}'); background-size: cover; background-position: center; border: 1px solid rgba(255,255,255,0.15); border-radius: ${border_radius}px; padding: ${padding_v}px ${padding_h}px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.25);`;
            }
            
            // Fonts
            let font_import = "";
            if (font_family === 'Space Grotesk') {
                font_import = '<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;700&display=swap" rel="stylesheet">';
            } else if (font_family === 'Cinzel') {
                font_import = '<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700&display=swap" rel="stylesheet">';
            }
            
            // Displacement transforms
            let displacement_style = `transform: translate(${state.displacement_x}px, ${state.displacement_y}px) rotate(${state.rotation}deg); transform-origin: center; opacity: ${opacity};`;

            return `
                ${font_import}
                <div style="${displacement_style} width: 100%; max-width: 100%; overflow: visible; position: relative; z-index: 1000; box-sizing: border-box;">
                    <div style="${bg_css} text-align: ${align}; font-family: '${font_family}', sans-serif; font-size: ${size}px; line-height: 1.4; width: 100%; max-width: 100%; box-sizing: border-box; overflow: visible; word-wrap: break-word; overflow-wrap: break-word; word-break: break-word;">
                        ${body_html}
                    </div>
                </div>
            `;
        }

        // Redraw preview
        function drawPreview() {
            const html = compileBannerHTML();
            document.getElementById('live-banner-overlay').innerHTML = html;
        }

        // Push values to state and re-render preview
        function updateStateFromUI() {
            state.text = document.getElementById('val-text').value;
            state.font = document.getElementById('val-font').value;
            state.text_color = document.getElementById('val-text_color').value;
            document.getElementById('val-text_color_hex').value = state.text_color.toUpperCase();
            
            state.font_weight = document.getElementById('val-font_weight').value;
            state.font_style = document.getElementById('val-font_style').value;
            state.text_decoration = document.getElementById('val-text_decoration').value;
            
            state.size = parseInt(document.getElementById('val-size').value);
            state.displacement_x = parseInt(document.getElementById('val-displacement_x').value);
            state.displacement_y = parseInt(document.getElementById('val-displacement_y').value);
            state.rotation = parseInt(document.getElementById('val-rotation').value);
            state.opacity = parseInt(document.getElementById('val-opacity').value);
            state.align = document.getElementById('val-align').value;
            
            state.bg_type = document.getElementById('val-bg_type').value;
            state.bg_color = document.getElementById('val-bg_color').value;
            state.bg_gradient_end = document.getElementById('val-bg_gradient_end').value;
            state.bg_image_url = document.getElementById('val-bg_image_url').value;
            state.bg_opacity = parseInt(document.getElementById('val-bg_opacity').value);
            
            state.padding_vertical = parseInt(document.getElementById('val-padding_vertical').value);
            state.padding_horizontal = parseInt(document.getElementById('val-padding_horizontal').value);
            state.border_radius = parseInt(document.getElementById('val-border_radius').value);
            
            state.glow_enabled = document.getElementById('checkbox-glow_enabled').checked;
            state.glow_intensity = parseInt(document.getElementById('val-glow_intensity').value);
            state.glow_color_mode = document.getElementById('val-glow_color_mode').value;
            state.glow_color_fixed = document.getElementById('val-glow_color_fixed').value;
            
            state.shadow_enabled = document.getElementById('checkbox-shadow_enabled').checked;
            state.shadow_intensity = parseInt(document.getElementById('val-shadow_intensity').value);
            state.shadow_color = document.getElementById('val-shadow_color').value;
            
            state.animation_type = document.getElementById('val-animation_type').value;
            state.media_url = document.getElementById('val-media_url').value;
            state.media_align = document.getElementById('val-media_align').value;
            state.media_size = parseInt(document.getElementById('val-media_size').value);
            
            updateLabels();
            drawPreview();
            syncDataToParentTextarea();
        }

        // Custom Word Painter Function
        function paintCustomWord() {
            const word = document.getElementById('paint-word-input').value.trim();
            const color = document.getElementById('paint-color-picker').value;
            
            if (!word) return alert("Lütfen boyamak istediğiniz kelimeyi girin.");
            
            const textVal = state.text;
            let charColors = state.char_colors || [];
            
            // Pad or trim char_colors to match active text length
            if (charColors.length < textVal.length) {
                let missingCount = textVal.length - charColors.length;
                for (let i = 0; i < missingCount; i++) {
                    charColors.push("");
                }
            }
            
            let idx = textVal.toLowerCase().indexOf(word.toLowerCase());
            let found = false;
            while (idx !== -1) {
                for (let i = idx; i < idx + word.length; i++) {
                    if (i < charColors.length) {
                        charColors[i] = color;
                        found = true;
                    }
                }
                idx = textVal.toLowerCase().indexOf(word.toLowerCase(), idx + 1);
            }
            
            if (found) {
                state.char_colors = charColors;
                drawPreview();
                syncDataToParentTextarea();
                document.getElementById('paint-word-input').value = "";
            } else {
                alert(`"${word}" kelimesi ana metin içerisinde bulunamadı.`);
            }
        }

        function resetCharColors() {
            state.char_colors = [];
            drawPreview();
            syncDataToParentTextarea();
        }

        // Send latest data back to Streamlit
        function syncDataToParentTextarea() {
            try {
                const parentDoc = window.parent.document;
                const textareas = Array.from(parentDoc.querySelectorAll('textarea'));
                const bridge = textareas.find(ta => ta.placeholder && ta.placeholder.includes("Sistem Veri Geri Bildirim Köprüsü"));
                
                if (bridge) {
                    const lastVal = bridge.value;
                    const jsonStr = JSON.stringify(state);
                    bridge.value = jsonStr;
                    
                    const event = new Event('input', { bubbles: true });
                    event.simulated = true;
                    const tracker = bridge._valueTracker;
                    if (tracker) {
                        tracker.setValue(lastVal);
                    }
                    bridge.dispatchEvent(event);
                }
            } catch(err) {
                console.error("Bridge writing failed:", err);
            }
        }

        // Confirm publication
        function publishToLive() {
            syncDataToParentTextarea();
            try {
                const parentDoc = window.parent.document;
                const buttons = Array.from(parentDoc.querySelectorAll('button'));
                const saveBtn = buttons.find(btn => btn.textContent && btn.textContent.includes("GİZLİ_TETİKLEYİCİ_KAYDET"));
                
                if (saveBtn) {
                    saveBtn.click();
                } else {
                    alert("Senkronizasyon kanalı algılandı, ancak tetikleyici buton bulunamadı. Lütfen Streamlit sayfasının en altında yer alan 'GİZLİ_TETİKLEYİCİ_KAYDET' butonuna manuel olarak tıklayın.");
                }
            } catch(err) {
                console.error("Auto trigger failed:", err);
                alert("Sandbox kısıtlamaları nedeniyle otomatik tetikleme yürütülemedi. Lütfen Streamlit sayfasının altındaki sistemi kontrol edin ve 'GİZLİ_TETİKLEYİCİ_KAYDET' butonunu tıklayın.");
            }
        }

        // Implement hand dragging feature directly inside the mobile simulator display
        const dragStageElement = document.getElementById("drag-stage-element");
        let isDragging = false;
        let startX = 0;
        let startY = 0;
        let initialDispX = 0;
        let initialDispY = 0;

        dragStageElement.addEventListener("mousedown", dragStart);
        dragStageElement.addEventListener("touchstart", dragStart, { passive: false });

        window.addEventListener("mousemove", dragMove);
        window.addEventListener("touchmove", dragMove, { passive: false });

        window.addEventListener("mouseup", dragEnd);
        window.addEventListener("touchend", dragEnd);

        function dragStart(e) {
            isDragging = true;
            dragStageElement.style.cursor = "grabbing";
            
            const clientX = e.type === "touchstart" ? e.touches[0].clientX : e.clientX;
            const clientY = e.type === "touchstart" ? e.touches[0].clientY : e.clientY;
            
            initialDispX = state.displacement_x;
            initialDispY = state.displacement_y;
            
            startX = clientX;
            startY = clientY;
            
            if (e.type === "touchstart") e.preventDefault();
        }

        function dragMove(e) {
            if (!isDragging) return;
            
            const clientX = e.type === "touchmove" ? e.touches[0].clientX : e.clientX;
            const clientY = e.type === "touchmove" ? e.touches[0].clientY : e.clientY;
            
            const deltaX = clientX - startX;
            const deltaY = clientY - startY;
            
            let newX = initialDispX + deltaX;
            let newY = initialDispY + deltaY;
            
            newX = Math.max(-300, Math.min(300, newX));
            newY = Math.max(-300, Math.min(300, newY));
            
            state.displacement_x = Math.round(newX);
            state.displacement_y = Math.round(newY);
            
            // Sync slider visual values instantly
            document.getElementById('val-displacement_x').value = state.displacement_x;
            document.getElementById('val-displacement_y').value = state.displacement_y;
            
            updateLabels();
            drawPreview();
        }

        function dragEnd(e) {
            if (!isDragging) return;
            isDragging = false;
            dragStageElement.style.cursor = "grab";
            syncDataToParentTextarea();
        }

        // Bind DOM input change listeners on DOM load
        window.addEventListener('DOMContentLoaded', () => {
            loadSyncStateIntoUI();
            drawPreview();
            
            // Bind inputs to updateStateFromUI
            const inputs = [
                'val-text', 'val-font', 'val-text_color', 'val-font_weight', 'val-font_style', 'val-text_decoration',
                'val-size', 'val-displacement_x', 'val-displacement_y', 'val-rotation', 'val-opacity', 'val-align',
                'val-bg_type', 'val-bg_color', 'val-bg_gradient_end', 'val-bg_image_url', 'val-bg_opacity',
                'val-padding_vertical', 'val-padding_horizontal', 'val-border_radius',
                'val-glow_intensity', 'val-glow_color_mode', 'val-glow_color_fixed',
                'val-shadow_intensity', 'val-shadow_color',
                'val-animation_type', 'val-media_url', 'val-media_align', 'val-media_size'
            ];
            
            inputs.forEach(id => {
                const el = document.getElementById(id);
                if (el) {
                    el.addEventListener('input', updateStateFromUI);
                    el.addEventListener('change', updateStateFromUI);
                }
            });
            
            document.getElementById('checkbox-glow_enabled').addEventListener('change', updateStateFromUI);
            document.getElementById('checkbox-shadow_enabled').addEventListener('change', updateStateFromUI);
            
            // Keep Hex and Color Picker matched on manually typed hexes
            document.getElementById('val-text_color_hex').addEventListener('input', (e) => {
                let val = e.target.value;
                if (val.startsWith('#') && (val.length === 4 || val.length === 7)) {
                    document.getElementById('val-text_color').value = val;
                    updateStateFromUI();
                }
            });
        });
    </script>
</body>
</html>
    """.replace("__ACTIVE_SETTINGS_JSON__", active_settings_json)

    # Render unified component with high vertical workspace
    components.html(html_studio_code, height=820, scrolling=True)

    # === EARLY RETURN TO PREVENT UNREACHABLE SANDBOX EXECUTION CORS HACKS ===
    return

    # Package and serialize initial values for the CapCut dashboard template
    disp_x_sb = ts.get("displacement_x", 0)
    disp_y_sb = ts.get("displacement_y", 0)
    disp_rot_sb = ts.get("rotation", 0)
    disp_size_sb = ts.get("size", 20)
    ann_text_raw = ts.get("text", "")
    ann_text_html_escaped = ann_text_raw.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#x27;')
    ann_text_sb = ann_text_raw.replace('"', '\\"') # escape quotes backup
    js_ann_text = json.dumps(ann_text_raw)
    ann_font_sb = ts.get("font", "sans-serif")
    ann_align_sb = ts.get("align", "center")
    ann_weight_sb = ts.get("font_weight", "bold")
    ann_style_sb = ts.get("font_style", "normal")
    ann_decoration_sb = ts.get("text_decoration", "none")
    ann_opacity_sb = ts.get("opacity", 100)
    ann_text_color_sb = ts.get("text_color", "#FFFFFF")

    ann_glow_enabled_sb = "true" if ts.get("glow_enabled", False) else "false"
    ann_glow_intensity_sb = ts.get("glow_intensity", 50)
    ann_glow_color_mode_sb = ts.get("glow_color_mode", "auto")
    ann_glow_color_fixed_sb = ts.get("glow_color_fixed", "#FFC000")

    ann_shadow_enabled_sb = "true" if ts.get("shadow_enabled", False) else "false"
    ann_shadow_intensity_sb = ts.get("shadow_intensity", 50)
    ann_shadow_color_sb = ts.get("shadow_color", "#000000")

    ann_animation_type_sb = ts.get("animation_type", "none")

    ann_bg_type_sb = ts.get("bg_type", "none")
    ann_bg_color_sb = ts.get("bg_color", "#111122")
    ann_bg_gradient_end_sb = ts.get("bg_gradient_end", "#1a1a3a")
    ann_bg_image_url_sb = ts.get("bg_image_url", "")
    ann_bg_opacity_sb = ts.get("bg_opacity", 100)
    ann_padding_vertical_sb = ts.get("padding_vertical", 10)
    ann_padding_horizontal_sb = ts.get("padding_horizontal", 15)
    ann_border_radius_sb = ts.get("border_radius", 12)

    ann_media_url_sb = ts.get("media_url", "")
    ann_media_align_sb = ts.get("media_align", "below")
    ann_media_size_sb = ts.get("media_size", 150)

    char_colors_json = json.dumps(list(ts.get("char_colors", [])))

    # Construct the sandboxed CapCut HTML editor with double tap unlock and multi-text inputs
    sandbox_code = f"""<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover" />
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;700&display=swap" rel="stylesheet" />
    <style>
        * {{
            box-sizing: border-box;
            font-family: 'Space Grotesk', sans-serif;
            margin: 0;
            padding: 0;
        }}
        body {{
            background: transparent;
            color: #ffffff;
            overflow-x: hidden;
            overflow-y: auto;
            user-select: none;
            -webkit-user-select: none;
            padding: 5px;
        }}
        .stage-container {{
            background: #0f0f1e;
            border: 2px solid #e67e22;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.6), inset 0 0 20px rgba(230, 126, 34, 0.15);
            padding: 15px;
            overflow: visible;
        }}
        .stage-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 15px;
            border-bottom: 1px dashed rgba(230, 126, 34, 0.3);
            padding-bottom: 10px;
        }}
        .stage-title {{
            font-size: 14px;
            font-weight: 700;
            color: #e67e22;
            display: flex;
            align-items: center;
            gap: 6px;
            letter-spacing: 0.5px;
        }}
        .status-badge {{
            font-size: 10px;
            background: rgba(46, 204, 113, 0.2);
            border: 1px solid rgba(46, 204, 113, 0.4);
            padding: 3px 9px;
            border-radius: 20px;
            color: #2ecc71;
            font-weight: bold;
        }}
        
        .editor-wrapper {{
            display: grid;
            grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
            gap: 20px;
            margin-top: 10px;
        }}
        @media (max-width: 800px) {{
            .editor-wrapper {{
                grid-template-columns: 1fr;
            }}
        }}

        .editor-panel-left {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        .editor-panel-right {{
            display: flex;
            flex-direction: column;
            background: #131326;
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 10px;
            padding: 15px;
        }}

        .canvas-area {{
            position: relative;
            width: 100%;
            height: 480px;
            border-radius: 15px;
            border: 2px solid #e67e22;
            background: radial-gradient(circle at top, #3b0000 0%, #170000 65%, #050000 100%);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-start;
            overflow: hidden;
            cursor: grab;
            box-shadow: inset 0 3px 25px rgba(0,0,0,0.9), 0 8px 30px rgba(0,0,0,0.5);
        }}
        .canvas-area:active {{
            cursor: grabbing;
        }}
        #drag-item {{
            position: absolute;
            transform-origin: center center;
            transition: none;
            will-change: transform;
            display: inline-block;
            text-align: center;
            white-space: wrap !important;
            word-wrap: break-word;
            overflow-wrap: break-word;
            word-break: break-word;
        }}
        
        .tabs-header {{
            display: flex;
            flex-direction: column;
            gap: 6px;
            margin-bottom: 12px;
            border-bottom: none;
            padding-bottom: 0px;
        }}
        .tab-btn {{
            background: #202035;
            color: #8892b0;
            border: 1px solid rgba(255,255,255,0.05);
            padding: 10px 14px;
            font-size: 13px;
            font-weight: bold;
            cursor: pointer;
            border-radius: 8px;
            text-align: left;
            width: 100%;
            transition: all 0.2s ease;
            box-sizing: border-box;
        }}
        .tab-btn.active {{
            background: #e67e22;
            color: white;
            border-color: #f39c12;
        }}
        .tab-content {{
            display: none;
            height: 400px;
            padding-right: 5px;
            overflow-y: auto;
        }}
        .tab-content.active {{
            display: block;
        }}

        .form-group {{
            margin-bottom: 12px;
        }}
        .form-group label {{
            display: block;
            font-size: 10px;
            color: #94a3b8;
            margin-bottom: 5px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .form-control, input, select, textarea, input[type="text"] {{
            width: 100% !important;
            background: #0f0f1e !important;
            background-color: #0f0f1e !important;
            border: 1px solid rgba(255,255,255,0.2) !important;
            border-radius: 6px !important;
            padding: 7px 10px !important;
            color: #ffffff !important;
            font-size: 12px !important;
            outline: none !important;
            transition: all 0.2s ease !important;
        }}
        .form-control:focus {{
            border-color: #e67e22;
            box-shadow: 0 0 8px rgba(230,126,34,0.3);
        }}
        .flex-row {{
            display: flex;
            gap: 8px;
        }}
        .flex-item {{
            flex: 1;
        }}
        
        .toggle-container {{
            display: flex;
            align-items: center;
            gap: 8px;
            cursor: pointer;
            user-select: none;
            padding: 4px 0;
        }}
        .toggle-switch {{
            position: relative;
            width: 32px;
            height: 18px;
            background: #202030;
            border-radius: 9px;
            transition: all 0.25s ease;
        }}
        .toggle-switch::after {{
            content: '';
            position: absolute;
            width: 14px;
            height: 14px;
            border-radius: 50%;
            background: #ffffff;
            top: 2px;
            left: 2px;
            transition: all 0.25s ease;
        }}
        input[type="checkbox"]:checked + .toggle-switch {{
            background: #e67e22;
        }}
        input[type="checkbox"]:checked + .toggle-switch::after {{
            left: 16px;
        }}
        .hidden-checkbox {{
            display: none;
        }}

        .char-color-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(60px, 1fr));
            gap: 6px;
            margin-top: 5px;
        }}
        .char-color-box {{
            background: #090914;
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 6px;
            padding: 4px;
            text-align: center;
        }}
        .char-color-box span {{
            font-size: 10px;
            color: #94a3b8;
            display: block;
            margin-bottom: 2px;
        }}
        .char-color-box input[type="color"] {{
            width: 100%;
            height: 22px;
            border: none;
            background: transparent;
            cursor: pointer;
        }}

        .indicators-row {{
            display: flex;
            flex-direction: column;
            gap: 10px;
            width: 100%;
        }}
        .indicator {{
            width: 100%;
            background: rgba(0,0,0,0.5);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 8px;
            padding: 10px 14px;
            text-align: left;
            font-size: 13px;
            color: #bdc3c7;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-sizing: border-box;
        }}
        .indicator span {{
            display: inline-block;
            color: #f39c12;
            font-weight: bold;
            font-size: 14px;
            margin-top: 0px;
        }}

        .toolbar {{
            display: flex;
            flex-direction: column;
            gap: 8px;
            width: 100%;
        }}
        .action-btn {{
            width: 100%;
            background: #252538;
            color: white;
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 8px;
            padding: 12px;
            font-size: 13px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.15s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            box-sizing: border-box;
        }}
        .action-btn:hover {{
            background: #31314a;
            border-color: rgba(255,255,255,0.2);
        }}
        .action-btn:active {{
            transform: scale(0.96);
        }}
        .action-btn.danger {{
            background: #5d6d7e;
        }}
        .action-btn.danger:hover {{
            background: #7f8c8d;
        }}

        .bottom-action-bar {{
            display: flex;
            flex-direction: column;
            gap: 10px;
            width: 100%;
            margin-top: 10px;
        }}
        .bottom-btn {{
            width: 100%;
            padding: 14px;
            border: none;
            border-radius: 8px;
            font-size: 13px;
            font-weight: bold;
            cursor: pointer;
            color: white;
            text-shadow: 0 1px 2px rgba(0,0,0,0.3);
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            transition: all 0.2s ease;
            box-sizing: border-box;
        }}
        .bottom-btn.preview-btn {{
            background: linear-gradient(135deg, #2ecc71, #27ae60);
        }}
        .bottom-btn.preview-btn:hover {{
            filter: brightness(1.1);
        }}
        .bottom-btn.save-btn {{
            background: linear-gradient(135deg, #e67e22, #d35400);
            border: 1px solid #f39c12;
        }}
        .bottom-btn.save-btn:hover {{
            filter: brightness(1.1);
        }}
        .bottom-btn:active {{
            transform: scale(0.97);
        }}
        
        .add-text-btn {{
            background: #27ae60 !important;
            border-color: #2ecc71 !important;
            color: white !important;
            height: 30px;
            margin-top: 5px;
        }}
        .text-part-row {{
            position: relative;
            display: flex;
            gap: 6px;
            align-items: center;
            margin-bottom: 6px;
        }}
        .delete-part-btn {{
            background: #c0392b !important;
            color: white;
            border: none;
            width: 25px;
            height: 30px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            font-size: 11px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
    </style>
</head>
<body>
    <div class="stage-container">
        <input type="hidden" id="inp-size" value="{disp_size_sb}" />
        <input type="hidden" id="inp-text" value="{ann_text_html_escaped}" />

        <div class="stage-header">
            <span class="stage-title">🎯 KAPLAN PARÇASI - TEPE DUYURU EDİTÖRÜ</span>
            <span class="status-badge">MOBİL / DESKTOP AKTİF</span>
        </div>
        
        <div class="editor-wrapper">
            <!-- LEFTPANEL: Preview & Coordinates -->
            <div class="editor-panel-left">
                <div class="canvas-area" id="canvas-area">
                    <!-- Pure decorative background and mockup UI that acts as our "Kaplan Parçası" landing/chat dashboard -->
                    <div class="mock-device-container" style="position: absolute; inset: 0; width: 100%; height: 100%; display: flex; flex-direction: column; align-items: flex-start; justify-content: flex-start; padding: 25px 23px; box-sizing: border-box; font-family: sans-serif; pointer-events: none; user-select: none; text-align: left; z-index: 1;">
                        
                        <!-- Top status bar mock -->
                        <div style="width: 100%; display: flex; justify-content: space-between; align-items: center; font-size: 11px; color: rgba(255, 255, 255, 0.35); margin-bottom: 25px; font-weight: bold;">
                            <span>Turkcell LTE</span>
                            <span>17:57 %18.1 🔋</span>
                        </div>
                        
                        <!-- The target dropzone for the announcement band. We put an empty spacing region where the banner natively rendered above the title -->
                        <div style="width: 100%; height: auto; min-height: 50px; margin-bottom: 20px; border: 1.5px dashed rgba(255,255,255,0.06); border-radius: 8px; background: rgba(0,0,0,0.15);">
                            <!-- This empty spacer represents the default spot of the banner, allowing users to see it in its original place or offset it -->
                        </div>

                        <!-- 🐯 Kaplan Parçası V18.1 Header -->
                        <h2 style="font-size: 1.6rem; font-weight: 800; color: #ffffff; letter-spacing: -0.5px; margin: 0 0 15px 0; font-family: sans-serif; display: flex; align-items: center; gap: 8px; width: 100%;">🐯 Kaplan Parçası V18.1</h2>

                        <!-- Bell Popover Circle Button Mock -->
                        <div style="width: 44px; height: 44px; border-radius: 50%; border: 2px solid #f39c12; background: #1a1a3a; display: flex; align-items: center; justify-content: center; font-size: 18px; color: white; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(243, 156, 18, 0.4);">
                            🔔
                        </div>

                        <!-- Textbox Mock -->
                        <div style="width: 100%; display: flex; flex-direction: column; gap: 8px; margin-bottom: 18px;">
                            <label style="color: #bdc3c7; font-size: 13px; font-weight: bold; font-family: sans-serif;">Mesajını yaz:</label>
                            <div style="width: 100%; height: 85px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.12); background: rgba(30, 30, 50, 0.25); box-shadow: inset 0 2px 8px rgba(0,0,0,0.4);"></div>
                        </div>

                        <!-- Send Button Mock -->
                        <div style="padding: 12px 24px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.08); background: rgba(45, 45, 65, 0.5); font-size: 13px; color: #ffffff; font-weight: bold; width: fit-content; display: flex; align-items: center; gap: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
                            <span>✉ Gönder</span>
                        </div>
                    </div>

                    <!-- The active interactive draggable item - overlays on top of mock elements. Starts at default spot (offset relative to the upper spacing region) -->
                    <div id="drag-item" style="transform: translate({disp_x_sb}px, {disp_y_sb}px) rotate({disp_rot_sb}deg); z-index: 100; position: absolute; left: 15px; right: 15px; top: 55px; margin: 0 auto; width: calc(100% - 30px); pointer-events: auto;">
                        <div id="banner-wrapper" style="overflow: visible;"></div>
                    </div>
                </div>
                
                <div class="indicators-row">
                    <div class="indicator">X Kaydırma<span id="badge-x">{disp_x_sb}px</span></div>
                    <div class="indicator">Y Kaydırma<span id="badge-y">{disp_y_sb}px</span></div>
                    <div class="indicator">Yazı Boyutu<span id="badge-size">{disp_size_sb}px</span></div>
                    <div class="indicator">Döndürme<span id="badge-rot">{disp_rot_sb}°</span></div>
                </div>
                
                <div class="toolbar">
                    <button class="action-btn" id="btn-add-text-part" style="background:#27ae60; border-color:#2ecc71; color:white; font-weight:bold;" onclick="switchTab('tab-metin'); addTextPartInput('', true);" title="Mevcut metnin yanına yeni bir metin alanı daha ekler">➕ Yeni Yazı Alanı (+)</button>
                    <button class="action-btn" id="btn-size-minus" title="Çift parmak zoom veya fare tekerleğiyle de ayarlanabilir">📏 Boyut (-2)</button>
                    <button class="action-btn" id="btn-size-plus" title="Çift parmak zoom veya fare tekerleğiyle de ayarlanabilir">📏 Boyut (+2)</button>
                    <button class="action-btn" id="btn-rot-left">↺ Çevir (-15°)</button>
                    <button class="action-btn" id="btn-rot-right">↻ Çevir (+15°)</button>
                    <button class="action-btn danger" id="btn-reset" title="Konumu merkeze sıfırlar">🎯 Konum Sıfırla</button>
                    <button class="action-btn danger" id="btn-factory-reset" style="background:#c0392b; border-color:#962d22;" title="Sıfırla">🔄 Fabrika Sıfırla</button>
                </div>
                
                <div class="bottom-action-bar">
                    <button class="bottom-btn preview-btn" id="btn-preview">👀 ANLIK ÖNİZLEME YAP</button>
                    <button class="bottom-btn save-btn" id="btn-save">💾 CANLIYA KAYDET VE YAYINLA 🚀</button>
                </div>
            </div>

            <!-- RIGHT PANEL -->
            <div class="editor-panel-right">
                <div class="tabs-header">
                    <button class="tab-btn active" onclick="switchTab('tab-metin')">📝 Yazı & Biçim</button>
                    <button class="tab-btn" onclick="switchTab('tab-renk')">🎨 Harf Boyama</button>
                    <button class="tab-btn" onclick="switchTab('tab-arka')">🖼️ Arka Plan</button>
                    <button class="tab-btn" onclick="switchTab('tab-efekt')">✨ Neon & Gölge</button>
                    <button class="tab-btn" onclick="switchTab('tab-gorsel')">📷 Medya</button>
                </div>

                <!-- TAB 1: Yazı & Biçim (Enhanced with dynamic multi-parts input structure) -->
                <div id="tab-metin" class="tab-content active">
                    <div class="form-group">
                        <label>Duyuru Metni</label>
                        <div id="multi-text-container"></div>
                        <button type="button" class="action-btn add-text-btn" onclick="addTextPartInput('', true)">➕ Yeni Yazı Alanı Ekle</button>
                    </div>
                    
                    <div class="flex-row">
                        <div class="form-group flex-item">
                            <label>Hizalama</label>
                            <select id="inp-align" class="form-control" onchange="renderPreview()">
                                <option value="center">Orta</option>
                                <option value="left">Sol</option>
                                <option value="right">Sağ</option>
                            </select>
                        </div>
                        <div class="form-group flex-item">
                            <label>Yazı Tipi</label>
                            <select id="inp-font" class="form-control" onchange="renderPreview()">
                                <option value="sans-serif">Sans-Serif (Varsayılan)</option>
                                <option value="Space Grotesk">Space Grotesk (Teknolojik)</option>
                                <option value="Cinzel">Cinzel (Klasik Roma)</option>
                                <option value="monospace">Retro Blok (Monospace)</option>
                                <option value="cursive">El Yazısı (Cursive)</option>
                                <option value="Georgia">Georgia</option>
                                <option value="Arial">Arial</option>
                                <option value="Impact">Impact (Dar-Kalın)</option>
                            </select>
                        </div>
                    </div>

                    <div class="flex-row">
                        <div class="form-group flex-item">
                            <label>Kalınlık (Weight)</label>
                            <select id="inp-font-weight" class="form-control" onchange="renderPreview()">
                                <option value="bold">Kalın (Bold)</option>
                                <option value="normal">Normal</option>
                                <option value="bolder">Çok Kalın (Bolder)</option>
                                <option value="900">Devasa Kalın (900)</option>
                            </select>
                        </div>
                        <div class="form-group flex-item">
                            <label>Stil (Style)</label>
                            <select id="inp-font-style" class="form-control" onchange="renderPreview()">
                                <option value="normal">Normal</option>
                                <option value="italic">İtalik (Eğik)</option>
                            </select>
                        </div>
                    </div>

                    <div class="flex-row">
                        <div class="form-group flex-item">
                            <label>Süsleme (Decoration)</label>
                            <select id="inp-text-decoration" class="form-control" onchange="renderPreview()">
                                <option value="none">Süsleme Yok</option>
                                <option value="underline">Altı Çizili</option>
                                <option value="line-through">Üstü Çizili</option>
                                <option value="overline">Üst Çizgili</option>
                            </select>
                        </div>
                        <div class="form-group flex-item">
                            <label>Varsayılan Yazı Rengi</label>
                            <input type="color" id="inp-text-color" value="{ann_text_color_sb}" class="form-control" style="height:35px; padding:2px;" oninput="handleTextGlobalColorChange(this.value)" />
                        </div>
                    </div>

                    <div class="form-group">
                        <label>Yazı Görünürlüğü (Saydamlık - %)</label>
                        <div class="flex-row" style="align-items: center;">
                            <input type="range" id="inp-opacity" min="10" max="100" value="{ann_opacity_sb}" class="form-control" style="flex:3;" oninput="document.getElementById('v-opacity').innerText=this.value+'%'; renderPreview()" />
                            <span id="v-opacity" style="flex:1; text-align:right; font-size:11px; color:#e67e22; font-weight:bold;">{ann_opacity_sb}%</span>
                        </div>
                    </div>
                </div>

                <!-- TAB 2: Harf Boyama -->
                <div id="tab-renk" class="tab-content">
                    <div class="form-group" style="background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.03); margin-bottom: 12px;">
                        <label>⚡ Toplu & Hızlı Boyama Araçları</label>
                        <div class="flex-row" style="margin-bottom:8px;">
                            <input type="color" id="bulk-color-pick" value="#FFFFFF" class="form-control" style="flex:1; height:32px; padding:2px;" />
                            <button type="button" class="action-btn" style="flex:2.2; background:#2980b9;" onclick="applyBulkColor()">Tüm Harfleri Boya</button>
                        </div>
                        <div class="flex-row">
                            <input type="text" id="paint-word-target" placeholder="Boyanacak Kelime..." class="form-control" style="flex:2;" />
                            <input type="color" id="paint-word-color" value="#FFD700" class="form-control" style="flex:1; height:32px; padding:2px;" />
                            <button type="button" class="action-btn" style="flex:1.5; background:#8e44ad;" onclick="applyWordHighlight()">Kelimeli Boya</button>
                        </div>
                    </div>
                    
                    <label style="margin-bottom:6px; display:block; font-size:10px; font-weight:bold; color:#f39c12;">🔠 Tek Tek Harf Harf Renklendir</label>
                    <div class="char-color-grid" id="char-colors-grid"></div>
                </div>

                <!-- TAB 3: Arka Plan -->
                <div id="tab-arka" class="tab-content">
                    <div class="form-group">
                        <label>Arka Plan Tasarım Tipi</label>
                        <select id="inp-bg-type" class="form-control" onchange="toggleBgFields(); renderPreview();">
                            <option value="none">Arka Plan Yok</option>
                            <option value="flat">Düz Renk</option>
                            <option value="gradient">Renk Geçişli (Gradient)</option>
                            <option value="image">Görsel / Hareketli GIF</option>
                        </select>
                    </div>

                    <div id="bg-color-fields" class="flex-row">
                        <div class="form-group flex-item">
                            <label>Arka Plan Rengi</label>
                            <input type="color" id="inp-bg-color" value="{ann_bg_color_sb}" class="form-control" style="height:35px; padding:2px;" oninput="renderPreview()" />
                        </div>
                        <div class="form-group flex-item" id="bg-gradient-field">
                            <label>Gradient Bitiş Rengi</label>
                            <input type="color" id="inp-bg-gradient-end" value="{ann_bg_gradient_end_sb}" class="form-control" style="height:35px; padding:2px;" oninput="renderPreview()" />
                        </div>
                    </div>

                    <div id="bg-image-fields" class="form-group">
                        <div class="form-group">
                            <label>Web Görsel / GIF Linki</label>
                            <input type="text" id="inp-bg-image-url" value="{ann_bg_image_url_sb}" placeholder="https://..." class="form-control" oninput="renderPreview()" />
                        </div>
                        <div class="form-group">
                            <label>Görsel Şeffaflığı / Opaklığı</label>
                            <div class="flex-row" style="align-items: center;">
                                <input type="range" id="inp-bg-opacity" min="10" max="100" value="{ann_bg_opacity_sb}" class="form-control" style="flex:3;" oninput="document.getElementById('v-bg-opacity').innerText=this.value+'%'; renderPreview()" />
                                <span id="v-bg-opacity" style="flex:1; text-align:right; font-size:11px; color:#e67e22; font-weight:bold;">{ann_bg_opacity_sb}%</span>
                            </div>
                        </div>
                    </div>

                    <div class="flex-row">
                        <div class="form-group flex-item">
                            <label>İç Düşey Boşluk (Padding Y)</label>
                            <input type="number" id="inp-padding-vertical" value="{ann_padding_vertical_sb}" min="0" max="100" class="form-control" oninput="renderPreview()" />
                        </div>
                        <div class="form-group flex-item">
                            <label>İç Yatay Boşluk (Padding X)</label>
                            <input type="number" id="inp-padding-horizontal" value="{ann_padding_horizontal_sb}" min="0" max="100" class="form-control" oninput="renderPreview()" />
                        </div>
                    </div>

                    <div class="form-group">
                        <label>Çerçeve Köşe Ovalleşmesi (Border Radius px)</label>
                        <input type="number" id="inp-border-radius" value="{ann_border_radius_sb}" min="0" max="100" class="form-control" oninput="renderPreview()" />
                    </div>
                </div>

                <!-- TAB 4: Neon & Gölge -->
                <div id="tab-efekt" class="tab-content">
                    <div class="form-group" style="background: rgba(0,243,255,0.02); padding: 10px; border-radius: 8px; border: 1px solid rgba(0,243,255,0.06); margin-bottom: 12px;">
                        <label class="toggle-container">
                            <input type="checkbox" id="inp-glow-enabled" class="hidden-checkbox" onchange="toggleGlowFields(); renderPreview();" />
                            <div class="toggle-switch"></div>
                            <span style="font-size:11px; color:#ffffff; font-weight:bold;">🌌 NEON PARLAKLIK (GLOW)</span>
                        </label>
                        
                        <div id="glow-intensity-wrapper" class="form-group" style="margin-top:8px;">
                            <label>Neon Yoğunluk Gücü</label>
                            <div class="flex-row" style="align-items: center;">
                                <input type="range" id="inp-glow-intensity" min="0" max="100" value="{ann_glow_intensity_sb}" class="form-control" style="flex:3;" oninput="document.getElementById('v-glow-intensity').innerText=this.value; renderPreview();" />
                                <span id="v-glow-intensity" style="flex:1; text-align:right; font-size:11px; color:#e67e22; font-weight:bold;">{ann_glow_intensity_sb}</span>
                            </div>
                        </div>
                        
                        <div id="glow-color-wrapper" class="form-group">
                            <label>Glow Rengi Modu</label>
                            <div style="display:flex; gap:12px; margin-bottom:8px; font-size:11px;">
                                <label style="cursor:pointer; display:flex; align-items:center; gap:4px; text-transform:none;">
                                    <input type="radio" name="glow_color_mode" value="auto" onchange="toggleGlowFields(); renderPreview();" /> Harf Rengiyle Aynı (Auto)
                                </label>
                                <label style="cursor:pointer; display:flex; align-items:center; gap:4px; text-transform:none;">
                                    <input type="radio" name="glow_color_mode" value="fixed" onchange="toggleGlowFields(); renderPreview();" /> Özel Sabit Renk
                                </label>
                            </div>
                            
                            <div id="glow-color-fixed-picker" class="form-group" style="margin-bottom:0;">
                                <label>Neon Sabit Rengi</label>
                                <input type="color" id="inp-glow-color-fixed" value="{ann_glow_color_fixed_sb}" class="form-control" style="height:35px; padding:2px;" oninput="renderPreview()" />
                            </div>
                        </div>
                    </div>

                    <div class="form-group" style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.03); margin-bottom: 12px;">
                        <label class="toggle-container">
                            <input type="checkbox" id="inp-shadow-enabled" class="hidden-checkbox" onchange="toggleShadowFields(); renderPreview();" />
                            <div class="toggle-switch"></div>
                            <span style="font-size:11px; color:#ffffff; font-weight:bold;">🖤 DERİNLİK GÖLGESİ (SHADOW)</span>
                        </label>
                        
                        <div id="shadow-intensity-wrapper" class="form-group" style="margin-top:8px;">
                            <label>Gölge Derinlik Gücü</label>
                            <div class="flex-row" style="align-items: center;">
                                <input type="range" id="inp-shadow-intensity" min="0" max="100" value="{ann_shadow_intensity_sb}" class="form-control" style="flex:3;" oninput="document.getElementById('v-shadow-intensity').innerText=this.value; renderPreview();" />
                                <span id="v-shadow-intensity" style="flex:1; text-align:right; font-size:11px; color:#e67e22; font-weight:bold;">{ann_shadow_intensity_sb}</span>
                            </div>
                        </div>
                        
                        <div id="shadow-color-wrapper" class="form-group" style="margin-bottom:0;">
                            <label>Gölge Rengi</label>
                            <input type="color" id="inp-shadow-color" value="{ann_shadow_color_sb}" class="form-control" style="height:35px; padding:2px;" oninput="renderPreview()" />
                        </div>
                    </div>

                    <div class="form-group">
                        <label>🎬 Yazı Animasyon Tipi</label>
                        <select id="inp-animation-type" class="form-control" onchange="renderPreview()">
                            <option value="none">Animasyon Yok</option>
                            <option value="neon_pulse">Neon Nefes Girişi (Pulse)</option>
                            <option value="wiggle">Dalgalanma (Wiggle Wave)</option>
                            <option value="neon_flicker">Retro Neon Titremesi (Flicker)</option>
                            <option value="rainbow">Gökkuşağı Renk Akışı (Rainbow)</option>
                            <option value="pulse">Yumuşak Genişleme</option>
                            <option value="blur_fade">Bulanıklaşan Odaklama (Blur Fade)</option>
                        </select>
                    </div>
                </div>

                <!-- TAB 5: Medya -->
                <div id="tab-gorsel" class="tab-content">
                    <div class="form-group">
                        <label>Ek Görsel / Hareketli GIF URL</label>
                        <input type="text" id="inp-media-url" value="{ann_media_url_sb}" placeholder="https://..." class="form-control" oninput="renderPreview()" />
                    </div>
                    
                    <div class="form-group">
                        <label>Görsel Konumu (Align)</label>
                        <select id="inp-media-align" class="form-control" onchange="renderPreview()">
                            <option value="below">Yazının Altında</option>
                            <option value="above">Yazının Üstünde</option>
                            <option value="left">Yazının Solunda</option>
                            <option value="right">Yazının Sağında</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label>Görsel Genişliği (px)</label>
                        <div class="flex-row" style="align-items: center;">
                            <input type="range" id="inp-media-size" min="20" max="500" value="{ann_media_size_sb}" class="form-control" style="flex:3;" oninput="document.getElementById('v-media-size').innerText=this.value+'px'; renderPreview()" />
                            <span id="v-media-size" style="flex:1; text-align:right; font-size:11px; color:#e67e22; font-weight:bold;">{ann_media_size_sb}px</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const parentDoc = window.parent.document;
        
        // Touch & Drag Position state
        let x = {disp_x_sb};
        let y = {disp_y_sb};
        let size = {disp_size_sb};
        let rot = {disp_rot_sb};
        
        // Drag unlock states
        let dragUnlocked = false; // Locked by default
        
        // Global colors array
        let charColorsArray = {char_colors_json};
        
        const dragItem = document.getElementById('drag-item');
        const canvasArea = document.getElementById('canvas-area');
        
        // ADD LOCK/UNLOCK METRICS ON THE CANVAS
        const lockBadge = document.createElement('div');
        lockBadge.id = 'lock-badge';
        lockBadge.style.cssText = `
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(15, 15, 30, 0.9);
            border: 1px solid rgba(230, 126, 34, 0.5);
            padding: 5px 12px;
            border-radius: 6px;
            font-size: 11px;
            color: #bdc3c7;
            font-weight: bold;
            z-index: 999999;
            pointer-events: none;
            transition: all 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            box-shadow: 0 4px 15px rgba(0,0,0,0.6);
        `;
        canvasArea.appendChild(lockBadge);

        function updateLockUI() {{
            if (dragUnlocked) {{
                lockBadge.innerHTML = '🔓 HAREKET SERBEST (Sürükleyip konumlandır)';
                lockBadge.style.borderColor = 'rgba(46, 204, 113, 0.7)';
                lockBadge.style.color = '#2ecc71';
                lockBadge.style.boxShadow = '0 0 12px rgba(46, 204, 113, 0.4)';
                canvasArea.style.touchAction = 'none';
            }} else {{
                lockBadge.innerHTML = '🔒 HAREKET KİLİTLİ (Açmak için Çift Tıkla)';
                lockBadge.style.borderColor = 'rgba(230, 126, 34, 0.5)';
                lockBadge.style.color = '#e67e22';
                lockBadge.style.boxShadow = '0 4px 15px rgba(0,0,0,0.6)';
                canvasArea.style.touchAction = 'auto';
            }}
        }}
        updateLockUI();

        // Dblclick to unlock / lock
        canvasArea.addEventListener('dblclick', (e) => {{
            dragUnlocked = !dragUnlocked;
            updateLockUI();
        }});

        // Double tap for mobile
        let lastTap = 0;
        canvasArea.addEventListener('touchstart', (e) => {{
            const now = new Date().getTime();
            const timesince = now - lastTap;
            if (timesince < 300 && timesince > 0) {{
                dragUnlocked = !dragUnlocked;
                updateLockUI();
                e.preventDefault();
            }}
            lastTap = now;
        }});

        // Warn touch when locked
        canvasArea.addEventListener('mousedown', (e) => {{
            if (!dragUnlocked) {{
                lockBadge.style.transform = 'scale(1.08)';
                lockBadge.style.background = 'rgba(192, 57, 43, 0.95)';
                lockBadge.style.color = '#ffffff';
                lockBadge.innerHTML = '⚠️ Çift tıklayarak kilidi açın!';
                setTimeout(() => {{
                    lockBadge.style.transform = 'scale(1)';
                    lockBadge.style.background = 'rgba(15, 15, 30, 0.9)';
                    updateLockUI();
                }}, 1000);
            }}
        }});
        
        // Multi-text part management
        function addTextPartInput(value, notify) {{
            const container = document.getElementById('multi-text-container');
            const row = document.createElement('div');
            row.className = 'text-part-row';
            
            const input = document.createElement('input');
            input.type = 'text';
            input.value = value;
            input.className = 'form-control inp-text-part';
            input.placeholder = 'Yeni yazı parçası...';
            input.oninput = handleTextChange;
            
            const delBtn = document.createElement('button');
            delBtn.type = 'button';
            delBtn.className = 'delete-part-btn';
            delBtn.innerHTML = '🗑️';
            delBtn.onclick = () => {{
                row.remove();
                handleTextChange();
            }};
            
            row.appendChild(input);
            row.appendChild(delBtn);
            container.appendChild(row);
            
            if (notify) {{
                handleTextChange();
            }}
        }}

        function initMultiTextFields() {{
            const initialText = {js_ann_text};
            if (initialText.trim()) {{
                // Fallback splitting if there is any custom marker or just take as single initial part
                addTextPartInput(initialText, false);
            }} else {{
                addTextPartInput('', false);
            }}
        }}

        // Tab switching controller
        function switchTab(tabId) {{
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            
            const btn = Array.from(document.querySelectorAll('.tab-btn')).find(b => b.getAttribute('onclick').includes(tabId));
            if (btn) btn.classList.add('active');
            
            const content = document.getElementById(tabId);
            if (content) content.classList.add('active');
        }}

        // Dynamic show/hide of specific background fields
        function toggleBgFields() {{
            const bgType = document.getElementById('inp-bg-type').value;
            const colorFields = document.getElementById('bg-color-fields');
            const gradientField = document.getElementById('bg-gradient-field');
            const imageFields = document.getElementById('bg-image-fields');
            
            if (bgType === "none") {{
                colorFields.style.display = "none";
                imageFields.style.display = "none";
            }} else if (bgType === "flat") {{
                colorFields.style.display = "flex";
                gradientField.style.display = "none";
                imageFields.style.display = "none";
            }} else if (bgType === "gradient") {{
                colorFields.style.display = "flex";
                gradientField.style.display = "block";
                imageFields.style.display = "none";
            }} else if (bgType === "image") {{
                colorFields.style.display = "none";
                imageFields.style.display = "block";
            }}
        }}

        // Dynamic show/hide of Neon Glow fields
        function toggleGlowFields() {{
            const glowEnabled = document.getElementById('inp-glow-enabled').checked;
            const intensityWrapper = document.getElementById('glow-intensity-wrapper');
            const colorWrapper = document.getElementById('glow-color-wrapper');
            
            if (glowEnabled) {{
                intensityWrapper.style.display = "block";
                colorWrapper.style.display = "block";
                
                const glowMode = document.querySelector('input[name="glow_color_mode"]:checked').value;
                const fixedPicker = document.getElementById('glow-color-fixed-picker');
                if (glowMode === "fixed") {{
                    fixedPicker.style.display = "block";
                }} else {{
                    fixedPicker.style.display = "none";
                }}
            }} else {{
                intensityWrapper.style.display = "none";
                colorWrapper.style.display = "none";
            }}
        }}

        // Dynamic show/hide of Shadow fields
        function toggleShadowFields() {{
            const shadowEnabled = document.getElementById('inp-shadow-enabled').checked;
            const intensityWrapper = document.getElementById('shadow-intensity-wrapper');
            const colorWrapper = document.getElementById('shadow-color-wrapper');
            
            if (shadowEnabled) {{
                intensityWrapper.style.display = "block";
                colorWrapper.style.display = "block";
            }} else {{
                intensityWrapper.style.display = "none";
                colorWrapper.style.display = "none";
            }}
        }}

        // Rebuild character list & handle character color bindings
        function syncCharColorsCount(textLength) {{
            const grid = document.getElementById('char-colors-grid');
            const cachedColors = [...charColorsArray];
            grid.innerHTML = '';
            
            // Reinitialize array
            charColorsArray = [];
            const textVal = document.getElementById('inp-text').value;
            
            for (let i = 0; i < textLength; i++) {{
                const char = textVal[i] || ' ';
                const originalColor = cachedColors[i] || document.getElementById('inp-text-color').value || '#FFFFFF';
                charColorsArray.push(originalColor);
                
                const box = document.createElement('div');
                box.className = 'char-color-box';
                
                const label = document.createElement('span');
                label.innerText = `[${{i + 1}}] "${{char}}"`;
                
                const picker = document.createElement('input');
                picker.type = 'color';
                picker.value = originalColor;
                picker.oninput = (e) => {{
                    charColorsArray[i] = e.target.value;
                    renderPreview();
                }};
                
                box.appendChild(label);
                box.appendChild(picker);
                grid.appendChild(box);
            }}
        }}

        function handleTextChange() {{
            const parts = Array.from(document.querySelectorAll('.inp-text-part')).map(inp => inp.value);
            // Join parts with space
            const joinedText = parts.join(' ');
            document.getElementById('inp-text').value = joinedText;
            
            syncCharColorsCount(joinedText.length);
            renderPreview();
        }}
        
        function handleTextGlobalColorChange(newColor) {{
            charColorsArray = charColorsArray.map(() => newColor);
            
            // Sync current pickers
            document.querySelectorAll('.char-color-box input[type="color"]').forEach(el => {{
                el.value = newColor;
            }});
            renderPreview();
        }}
        
        function applyBulkColor() {{
            const targetColor = document.getElementById('bulk-color-pick').value;
            handleTextGlobalColorChange(targetColor);
        }}
        
        function applyWordHighlight() {{
            const word = document.getElementById('paint-word-target').value.trim();
            const color = document.getElementById('paint-word-color').value;
            const fullText = document.getElementById('inp-text').value;
            
            if (!word || !fullText) return;
            
            let index = fullText.indexOf(word);
            while (index !== -1) {{
                for (let i = index; i < index + word.length; i++) {{
                    if (i < charColorsArray.length) {{
                        charColorsArray[i] = color;
                    }}
                }}
                index = fullText.indexOf(word, index + 1);
            }}
            
            // sync pickers representation
            const pickers = document.querySelectorAll('.char-color-box input[type="color"]');
            charColorsArray.forEach((col, idx) => {{
                if (pickers[idx]) pickers[idx].value = col;
            }});
            renderPreview();
        }}
        
        function renderPreview() {{
            const wrapper = document.getElementById('banner-wrapper');
            const textVal = document.getElementById('inp-text').value;
            const font = document.getElementById('inp-font').value;
            const align = document.getElementById('inp-align').value;
            const size = parseInt(document.getElementById('inp-size').value) || 20;
            const weight = document.getElementById('inp-font-weight').value;
            const style = document.getElementById('inp-font-style').value;
            const decoration = document.getElementById('inp-text-decoration').value;
            const opacity = document.getElementById('inp-opacity').value;
            
            const glowEnabled = document.getElementById('inp-glow-enabled').checked;
            const glowIntensity = document.getElementById('inp-glow-intensity').value;
            const glowMode_el = document.querySelector('input[name="glow_color_mode"]:checked');
            const glowMode = glowMode_el ? glowMode_el.value : "auto";
            const glowFixedColor = document.getElementById('inp-glow-color-fixed').value;
            
            const shadowEnabled = document.getElementById('inp-shadow-enabled').checked;
            const shadowIntensity = document.getElementById('inp-shadow-intensity').value;
            const shadowColor = document.getElementById('inp-shadow-color').value;
            
            const animationType = document.getElementById('inp-animation-type').value;
            const bgType = document.getElementById('inp-bg-type').value;
            const bgColor = document.getElementById('inp-bg-color').value;
            const bgGradientEnd = document.getElementById('inp-bg-gradient-end').value;
            const bgImageUrl = document.getElementById('inp-bg-image-url').value;
            const bgOpacity = document.getElementById('inp-bg-opacity').value;
            const padY = document.getElementById('inp-padding-vertical').value;
            const padX = document.getElementById('inp-padding-horizontal').value;
            const borderRadius = document.getElementById('inp-border-radius').value;
            
            const mediaUrl = document.getElementById('inp-media-url').value;
            const mediaAlign = document.getElementById('inp-media-align').value;
            const mediaSize = document.getElementById('inp-media-size').value;
            
            // 1. Text letter-by-letter compilation
            let compiledTextHtml = '';
            for (let i = 0; i < textVal.length; i++) {{
                const char = textVal[i];
                const col = charColorsArray[i] || '#FFFFFF';
                
                // compute custom text shadow layers for ultra-smooth rendering performance
                let textShadowLayers = [];
                if (glowEnabled) {{
                    const actualGlowColor = (glowMode === 'auto') ? col : glowFixedColor;
                    const r = parseInt(glowIntensity);
                    textShadowLayers.push(`0 0 ${{r/5}}px ${{actualGlowColor}}`, `0 0 ${{r/2}}px ${{actualGlowColor}}`, `0 0 ${{r}}px ${{actualGlowColor}}`);
                }}
                
                if (shadowEnabled) {{
                    const sh = parseInt(shadowIntensity);
                    const steps = Math.ceil(sh / 12);
                    for(let s=1; s<=steps; s++) {{
                        textShadowLayers.push(`${{s}}px ${{s}}px ${{s*1.2}}px ${{shadowColor}}`);
                    }}
                }}
                
                let combinedTextShadow = textShadowLayers.length > 0 ? `text-shadow: ${{textShadowLayers.join(', ')}};` : '';
                
                // Space padding normalization
                if (char === ' ') {{
                    compiledTextHtml += '<span style="display: inline-block; margin-right:0.35em;"></span>&#8203;';
                }} else {{
                    compiledTextHtml += `<span style="display: inline-block; color:${{col}}; ${{combinedTextShadow}}">${{char}}</span>&#8203;`;
                }}
            }}
            
            // Build the main text div with layouts
            let animClass = '';
            let styleTagsHeader = '';
            
            if (animationType === 'neon_pulse') {{
                animClass = 'anim-neon-pulse';
                styleTagsHeader += `
                    @keyframes neonPulse {{
                        0%, 100% {{ opacity: 0.35; filter: brightness(0.7); }}
                        50% {{ opacity: 1; filter: brightness(1.2); }}
                    }}
                    .anim-neon-pulse {{ animation: neonPulse 2s infinite ease-in-out; }}
                `;
            }} else if (animationType === 'wiggle') {{
                animClass = 'anim-wiggle';
                styleTagsHeader += `
                    @keyframes wiggleComp {{
                        0%, 100% {{ transform: translateY(0) rotate(0deg); }}
                        25% {{ transform: translateY(-4px) rotate(-1.5deg); }}
                        75% {{ transform: translateY(4px) rotate(1.5deg); }}
                    }}
                    .anim-wiggle {{ animation: wiggleComp 3.5s infinite ease-in-out; }}
                `;
            }} else if (animationType === 'neon_flicker') {{
                animClass = 'anim-flicker';
                styleTagsHeader += `
                    @keyframes neonFlicker {{
                        0%, 19%, 21%, 23%, 25%, 54%, 56%, 100% {{ opacity: 1; }}
                        20%, 24%, 55% {{ opacity: 0.25; filter: saturate(0.4); }}
                    }}
                    .anim-flicker {{ animation: neonFlicker 4s infinite linear; }}
                `;
            }} else if (animationType === 'rainbow') {{
                animClass = 'anim-rainbow';
                styleTagsHeader += `
                    @keyframes colorRainbow {{
                        0% {{ filter: hue-rotate(0deg); }}
                        100% {{ filter: hue-rotate(360deg); }}
                    }}
                    .anim-rainbow {{ animation: colorRainbow 6s infinite linear; }}
                `;
            }} else if (animationType === 'pulse') {{
                animClass = 'anim-pulse';
                styleTagsHeader += `
                    @keyframes softPulse {{
                        0%, 100% {{ transform: scale(0.98); }}
                        50% {{ transform: scale(1.02); }}
                    }}
                    .anim-pulse {{ animation: softPulse 2.5s infinite ease-in-out; }}
                `;
            }} else if (animationType === 'blur_fade') {{
                animClass = 'anim-blur-fade';
                styleTagsHeader += `
                    @keyframes blurFade {{
                        0%, 100% {{ filter: blur(4px); opacity: 0.4; }}
                        50% {{ filter: blur(0); opacity: 1; }}
                    }}
                    .anim-blur-fade {{ animation: blurFade 3.5s infinite ease-in-out; }}
                `;
            }}
            
            // Write style override
            let styleEl = document.getElementById('dynamic-anims-styles');
            if(!styleEl) {{
                styleEl = document.createElement('style');
                styleEl.id = 'dynamic-anims-styles';
                document.head.appendChild(styleEl);
            }}
            styleEl.innerHTML = styleTagsHeader;
            
            // Compose text style attributes
            const mainTextStyle = `
                font-family: ${{font}}, sans-serif;
                text-align: ${{align}};
                font-weight: ${{weight}};
                font-style: ${{style}};
                text-decoration: ${{decoration}};
                opacity: ${{opacity / 100}};
                font-size: ${{size}}px;
                line-height: 1.25;
                word-wrap: break-word;
                white-space: normal;
                display: block;
            `;
            
            const finalTextHtml = `<div class="${{animClass}}" style="${{mainTextStyle}}">${{compiledTextHtml}}</div>`;
            
            // Build media element if url given
            let mediaHtml = '';
            if (mediaUrl.trim()) {{
                const alignStylesMap = {{
                    below: 'display:block; margin: 10px auto 0;',
                    above: 'display:block; margin: 0 auto 10px;',
                    left: 'display:inline-block; vertical-align:middle; margin-right:12px;',
                    right: 'display:inline-block; vertical-align:middle; margin-left:12px;'
                }};
                
                mediaHtml = `<img src="${{mediaUrl.trim()}}" style="width:${{mediaSize}}px; border-radius:8px; pointer-events:none; ${{alignStylesMap[mediaAlign] || ''}}" referrerPolicy="no-referrer" />`;
            }}
            
            // Combine Layout based on Media align configurations
            let contentCompilationHtml = '';
            if (mediaUrl.trim()) {{
                if (mediaAlign === 'above') {{
                    contentCompilationHtml = mediaHtml + finalTextHtml;
                }} else if (mediaAlign === 'below') {{
                    contentCompilationHtml = finalTextHtml + mediaHtml;
                }} else if (mediaAlign === 'left') {{
                    contentCompilationHtml = `<div style="display:flex; align-items:center; justify-content:${{align === 'left' ? 'flex-start' : (align === 'right' ? 'flex-end' : 'center')}}; gap:10px;">${{mediaHtml}}${{finalTextHtml}}</div>`;
                }} else if (mediaAlign === 'right') {{
                    contentCompilationHtml = `<div style="display:flex; align-items:center; justify-content:${{align === 'left' ? 'flex-start' : (align === 'right' ? 'flex-end' : 'center')}}; gap:10px;">${{finalTextHtml}}${{mediaHtml}}</div>`;
                }}
            }} else {{
                contentCompilationHtml = finalTextHtml;
            }}
            
            // Build Background Frame layout
            let bgStyleCss = '';
            if (bgType === 'flat') {{
                bgStyleCss = `background: ${{bgColor}};`;
            }} else if (bgType === 'gradient') {{
                bgStyleCss = `background: linear-gradient(135deg, ${{bgColor}}, ${{bgGradientEnd}});`;
            }} else if (bgType === 'image' && bgImageUrl.trim()) {{
                bgStyleCss = `
                    background-image: url('${{bgImageUrl.trim()}}');
                    background-size: cover;
                    background-position: center;
                    background-repeat: no-repeat;
                `;
            }}
            
            // Apply overlay transparency if bg is image
            let containerBgOverlay = '';
            if (bgType === 'image' && bgImageUrl.trim()) {{
                containerBgOverlay = `<div style="position:absolute; inset:0; background: rgba(0,0,0,${{ (100 - bgOpacity)/100 }}); z-index:1; pointer-events:none;"></div>`;
            }}
            
            wrapper.style.cssText = `
                position: relative;
                width: 100%;
                box-sizing: border-box;
                padding: ${{padY}}px ${{padX}}px;
                border-radius: ${{borderRadius}}px;
                ${{bgStyleCss}}
                overflow: hidden;
            `;
            wrapper.innerHTML = containerBgOverlay + `<div style="position:relative; z-index:2; width:100%;">${{contentCompilationHtml}}</div>`;
        }}
        
        function updateDisplay() {{
            document.getElementById('badge-x').innerText = x + 'px';
            document.getElementById('badge-y').innerText = y + 'px';
            document.getElementById('badge-size').innerText = size + 'px';
            document.getElementById('badge-rot').innerText = rot + '°';
            
            document.getElementById('inp-size').value = size;
        }}
        
        function applyTransforms() {{
            dragItem.style.transform = `translate(${{x}}px, ${{y}}px) rotate(${{rot}}deg)`;
            updateDisplay();
        }}
        
        // TWO-FINGER MULTI TOUCH GESTURES (Pinch, Scaling, Rotate & Zoom)
        let isDragging = false;
        let isPinching = false;
        let startTouchX = 0;
        let startTouchY = 0;
        
        let initTouchDist = 0;
        let initFontSize = 20;
        let initTouchAngle = 0;
        let initRotationAngle = 0;
        
        canvasArea.addEventListener('touchstart', (e) => {{
            if (!dragUnlocked) return;
            
            if (e.touches.length === 1) {{
                // Only begin dragging if the touch is directly on the text or drag element itself
                if (dragItem.contains(e.target)) {{
                    isDragging = true;
                    startTouchX = e.touches[0].clientX - x;
                    startTouchY = e.touches[0].clientY - y;
                    e.preventDefault();
                }}
            }} else if (e.touches.length === 2) {{
                e.preventDefault();
                isDragging = false;
                isPinching = true;
                const touch1 = e.touches[0];
                const touch2 = e.touches[1];
                
                initTouchDist = Math.hypot(touch2.clientX - touch1.clientX, touch2.clientY - touch1.clientY);
                initFontSize = size;
                
                initTouchAngle = Math.atan2(touch2.clientY - touch1.clientY, touch2.clientX - touch1.clientX);
                initRotationAngle = rot;
            }}
        }}, {{ passive: false }});
        
        canvasArea.addEventListener('touchmove', (e) => {{
            if (!dragUnlocked) return;
            e.preventDefault();
            
            if (isDragging && e.touches.length === 1) {{
                x = Math.round(e.touches[0].clientX - startTouchX);
                y = Math.round(e.touches[0].clientY - startTouchY);
                applyTransforms();
            }} else if (isPinching && e.touches.length === 2) {{
                const touch1 = e.touches[0];
                const touch2 = e.touches[1];
                
                const currentDist = Math.hypot(touch2.clientX - touch1.clientX, touch2.clientY - touch1.clientY);
                const scaleFactor = currentDist / initTouchDist;
                size = Math.max(8, Math.min(120, Math.round(initFontSize * scaleFactor)));
                
                const currentAngle = Math.atan2(touch2.clientY - touch1.clientY, touch2.clientX - touch1.clientX);
                const angleDifference = (currentAngle - initTouchAngle) * (180 / Math.PI);
                rot = Math.round(initRotationAngle + angleDifference);
                
                applyTransforms();
                renderPreview();
            }}
        }}, {{ passive: false }});
        
        canvasArea.addEventListener('touchend', () => {{
            isDragging = false;
            isPinching = false;
        }});
        canvasArea.addEventListener('touchcancel', () => {{
            isDragging = false;
            isPinching = false;
        }});
        
        // MOUSE ACTIONS (Desktop Drag supports)
        let isMouseDown = false;
        let startMouseX = 0;
        let startMouseY = 0;
        
        dragItem.addEventListener('mousedown', (e) => {{
            if (!dragUnlocked) {{
                e.stopPropagation();
                return;
            }}
            isMouseDown = true;
            startMouseX = e.clientX - x;
            startMouseY = e.clientY - y;
            e.stopPropagation();
            e.preventDefault();
        }});
        
        document.addEventListener('mousemove', (e) => {{
            if (isMouseDown && dragUnlocked) {{
                x = Math.round(e.clientX - startMouseX);
                y = Math.round(e.clientY - startMouseY);
                applyTransforms();
            }}
        }});
        
        document.addEventListener('mouseup', () => {{
            isMouseDown = false;
        }});
        
        // MOUSE WHEEL ROTATE/SCALING SUPPORT
        canvasArea.addEventListener('wheel', (e) => {{
            e.preventDefault();
            if (e.deltaY < 0) {{
                size = Math.min(120, size + 1);
            }} else {{
                size = Math.max(8, size - 1);
            }}
            applyTransforms();
            renderPreview();
        }}, {{ passive: false }});
        
        // MANUAL BUTTONS HANDLERS
        document.getElementById('btn-size-minus').addEventListener('click', () => {{
            size = Math.max(8, size - 2);
            applyTransforms();
            renderPreview();
        }});
        document.getElementById('btn-size-plus').addEventListener('click', () => {{
            size = Math.min(120, size + 2);
            applyTransforms();
            renderPreview();
        }});
        document.getElementById('btn-rot-left').addEventListener('click', () => {{
            rot = (rot - 15) % 360;
            applyTransforms();
            renderPreview();
        }});
        document.getElementById('btn-rot-right').addEventListener('click', () => {{
            rot = (rot + 15) % 360;
            applyTransforms();
            renderPreview();
        }});
        document.getElementById('btn-reset').addEventListener('click', () => {{
            x = 0;
            y = 0;
            size = 20;
            rot = 0;
            applyTransforms();
            renderPreview();
        }});
        
        document.getElementById('btn-factory-reset').addEventListener('click', () => {{
            if (confirm("Tüm tasarım ayarlarını ve metni fabrika ayarlarına sıfırlamak istediğinize emin misiniz?")) {{
                document.getElementById('multi-text-container').innerHTML = '';
                addTextPartInput('', false);
                document.getElementById('inp-text').value = "";
                document.getElementById('inp-font').value = "sans-serif";
                document.getElementById('inp-align').value = "center";
                document.getElementById('inp-font-weight').value = "normal";
                document.getElementById('inp-font-style').value = "normal";
                document.getElementById('inp-text-decoration').value = "none";
                document.getElementById('inp-opacity').value = 100;
                document.getElementById('v-opacity').innerText = "100%";
                
                document.getElementById('inp-glow-enabled').checked = false;
                document.getElementById('inp-glow-intensity').value = 50;
                document.getElementById('v-glow-intensity').innerText = "50";
                
                const autoRadio = document.querySelector('input[name="glow_color_mode"][value="auto"]');
                if (autoRadio) autoRadio.checked = true;
                
                document.getElementById('inp-glow-color-fixed').value = "#FFC000";
                
                document.getElementById('inp-shadow-enabled').checked = false;
                document.getElementById('inp-shadow-intensity').value = 50;
                document.getElementById('v-shadow-intensity').innerText = "50";
                document.getElementById('inp-shadow-color').value = "#000000";
                
                document.getElementById('inp-animation-type').value = "none";
                document.getElementById('inp-bg-type').value = "none";
                document.getElementById('inp-bg-color').value = "#111122";
                document.getElementById('inp-bg-gradient-end').value = "#1a1a3a";
                document.getElementById('inp-bg-image-url').value = "";
                document.getElementById('inp-bg-opacity').value = 100;
                document.getElementById('v-bg-opacity').innerText = "100%";
                document.getElementById('inp-padding-vertical').value = 10;
                document.getElementById('inp-padding-horizontal').value = 15;
                document.getElementById('inp-border-radius').value = 12;
                
                document.getElementById('inp-media-url').value = "";
                document.getElementById('inp-media-align').value = "below";
                document.getElementById('inp-media-size').value = 150;
                document.getElementById('v-media-size').innerText = "150px";
                
                document.getElementById('inp-text-color').value = "#FFFFFF";
                
                x = 0;
                y = 0;
                size = 20;
                rot = 0;
                dragUnlocked = false;
                updateLockUI();
                charColorsArray = [];
                
                applyTransforms();
                toggleBgFields();
                toggleGlowFields();
                toggleShadowFields();
                syncCharColorsCount(0);
                renderPreview();
                
                alert("Tüm değerler temizlendi! Canlıya aktarmak için alt kısımdaki 'CANLIYA KAYDET VE YAYINLA' butonuna basabilirsiniz.");
            }}
        }});
        
        // POPULATE DROPDOWNS AND OPTIONS FROM MODEL
        document.getElementById('inp-font').value = "{ann_font_sb}";
        document.getElementById('inp-align').value = "{ann_align_sb}";
        document.getElementById('inp-font-weight').value = "{ann_weight_sb}";
        document.getElementById('inp-font-style').value = "{ann_style_sb}";
        document.getElementById('inp-text-decoration').value = "{ann_decoration_sb}";
        document.getElementById('inp-animation-type').value = "{ann_animation_type_sb}";
        document.getElementById('inp-bg-type').value = "{ann_bg_type_sb}";
        document.getElementById('inp-media-align').value = "{ann_media_align_sb}";
        
        document.getElementById('inp-glow-enabled').checked = {ann_glow_enabled_sb};
        document.getElementById('inp-shadow-enabled').checked = {ann_shadow_enabled_sb};
 
        // radios
        const glowModeVal = "{ann_glow_color_mode_sb}";
        const radioBtn = document.querySelector(`input[name="glow_color_mode"][value="${{glowModeVal}}"]`);
        if (radioBtn) radioBtn.checked = true;
 
        // SUBMIT & SYNC PIPELINES
        function buildFullPayloadJSON() {{
            const text = document.getElementById('inp-text').value;
            const font = document.getElementById('inp-font').value;
            const align = document.getElementById('inp-align').value;
            const sizeInp = parseInt(document.getElementById('inp-size').value) || 20;
            const font_weight = document.getElementById('inp-font-weight').value;
            const font_style = document.getElementById('inp-font-style').value;
            const text_decoration = document.getElementById('inp-text-decoration').value;
            const opacity = parseInt(document.getElementById('inp-opacity').value) || 100;
            
            const glow_enabled = document.getElementById('inp-glow-enabled').checked;
            const glow_intensity = parseInt(document.getElementById('inp-glow-intensity').value) || 50;
            const glow_color_mode_el = document.querySelector('input[name="glow_color_mode"]:checked');
            const glow_color_mode = glow_color_mode_el ? glow_color_mode_el.value : "auto";
            const glow_color_fixed = document.getElementById('inp-glow-color-fixed').value;
            
            const shadow_enabled = document.getElementById('inp-shadow-enabled').checked;
            const shadow_intensity = parseInt(document.getElementById('inp-shadow-intensity').value) || 50;
            const shadow_color = document.getElementById('inp-shadow-color').value;
            
            const animation_type = document.getElementById('inp-animation-type').value;
            const bg_type = document.getElementById('inp-bg-type').value;
            const bg_color = document.getElementById('inp-bg-color').value;
            const bg_gradient_end = document.getElementById('inp-bg-gradient-end').value;
            const bg_image_url = document.getElementById('inp-bg-image-url').value;
            const bg_opacity = parseInt(document.getElementById('inp-bg-opacity').value) || 100;
            const padding_vertical = parseInt(document.getElementById('inp-padding-vertical').value) || 0;
            const padding_horizontal = parseInt(document.getElementById('inp-padding-horizontal').value) || 0;
            const border_radius = parseInt(document.getElementById('inp-border-radius').value) || 0;
            
            const media_url = document.getElementById('inp-media-url').value;
            const media_align = document.getElementById('inp-media-align').value;
            const media_size = parseInt(document.getElementById('inp-media-size').value) || 150;
            const text_color = document.getElementById('inp-text-color').value;
            
            return JSON.stringify({{
                "displacement_x": x,
                "displacement_y": y,
                "rotation": rot,
                "size": sizeInp,
                "text": text,
                "font": font,
                "align": align,
                "font_weight": font_weight,
                "font_style": font_style,
                "text_decoration": text_decoration,
                "opacity": opacity,
                "glow_enabled": glow_enabled,
                "glow_intensity": glow_intensity,
                "glow_color_mode": glow_color_mode,
                "glow_color_fixed": glow_color_fixed,
                "shadow_enabled": shadow_enabled,
                "shadow_intensity": shadow_intensity,
                "shadow_color": shadow_color,
                "animation_type": animation_type,
                "bg_type": bg_type,
                "bg_color": bg_color,
                "bg_gradient_end": bg_gradient_end,
                "bg_image_url": bg_image_url,
                "bg_opacity": bg_opacity,
                "padding_vertical": padding_vertical,
                "padding_horizontal": padding_horizontal,
                "border_radius": border_radius,
                "media_url": media_url,
                "media_size": media_size,
                "media_align": media_align,
                "char_colors": charColorsArray,
                "text_color": text_color
            }});
        }}
 
        function pushAndSubmit(action) {{
            if (!parentDoc) return;
            const jsonStr = buildFullPayloadJSON();
            
            const textAreas = Array.from(parentDoc.querySelectorAll('textarea'));
            const pmTextArea = textAreas.find(ta => ta.value && (ta.value.startsWith('{{"text":') || ta.value.startsWith('{{"displacement_x":')) || ta.ariaLabel === "advanced_json_payload");
            if (pmTextArea) {{
                pmTextArea.value = jsonStr;
                pmTextArea.dispatchEvent(new Event('input', {{ bubbles: true }}));
                pmTextArea.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }} else {{
                const backupTa = parentDoc.querySelector('[data-testid="stTextArea"] textarea');
                if (backupTa) {{
                    backupTa.value = jsonStr;
                    backupTa.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    backupTa.dispatchEvent(new Event('change', {{ bubbles: true }}));
                }}
            }}
 
            setTimeout(() => {{
                const parentButtons = Array.from(parentDoc.querySelectorAll('button'));
                let btn;
                if (action === 'save') {{
                    btn = parentButtons.find(b => b.innerText && b.innerText.includes("Tepe Duyurusunu Kaydet"));
                }} else {{
                    btn = parentButtons.find(b => b.innerText && b.innerText.includes("Düzenlemeyi Önizle"));
                }}
                if (btn) {{
                    btn.click();
                }}
            }}, 150);
        }}
 
        document.getElementById('btn-preview').addEventListener('click', () => pushAndSubmit('preview'));
        document.getElementById('btn-save').addEventListener('click', () => pushAndSubmit('save'));
 
        // Bootstrap on startup
        initMultiTextFields();
        syncCharColorsCount(document.getElementById('inp-text').value.length);
        toggleBgFields();
        toggleGlowFields();
        toggleShadowFields();
        renderPreview();
        applyTransforms();
    </script>
</body>
</html>"""

    # Embed and sync sandbox onto modern Streamlit interface
    st.components.v1.html(sandbox_code, height=920, scrolling=True)
    st.markdown("---")
    
    # Hidden form processed via JS pipelines
    with st.form("ann_edit_form", clear_on_submit=False):
        json_default = json.dumps(ts, ensure_ascii=False)
        json_input_val = st.text_area("advanced_json_payload", value=json_default, key="advanced_json_payload_key", label_visibility="collapsed")
        
        # Complete stealth style sheet to hide this fallback form representation entirely in the background
        st.markdown("""
            <style>
            div[data-testid="stForm"] {
                padding: 0px !important;
                border: none !important;
                box-shadow: none !important;
                background: transparent !important;
                margin: 0px !important;
            }
            div[data-testid="stForm"] div[data-testid="stTextArea"]:has(textarea[aria-label="advanced_json_payload"]) {
                display: none !important;
            }
            div[data-testid="stForm"] button[data-testid="stFormSubmitButton"] {
                display: none !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
        btn_preview = st.form_submit_button("Düzenlemeyi Önizle")
        btn_save = st.form_submit_button("Tepe Duyurusunu Kaydet")

    # Process JSON updates back into memory / database
    if btn_preview or btn_save:
        try:
            updated_payload = json.loads(json_input_val)
            st.session_state.temp_ann_settings = updated_payload
            
            if btn_save:
                db.collection("settings").document("global_announcement").set(updated_payload)
                trigger_global_rerun(exclude_self=False)
                st.success("✅ Tepe duyurusu başarıyla kaydedildi ve canlı yayına alındı!")
                time.sleep(1)
                st.rerun()
            else:
                st.success("👀 Önizleme başarıyla güncellendi! Yukarıdaki editör panelinden sonucu görebilirsiniz.")
                time.sleep(1)
                st.rerun()
        except Exception as e:
            st.error(f"Teknik hata oluştu: {e}")

    # === ŞABLON VE TASLAK KÜTÜPHANESİ ===
    st.markdown("---")
    st.markdown("""
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:15px;">
            <div style="background:#2980b9;width:8px;height:24px;border-radius:4px;"></div>
            <h2 style="margin:0;font-size:1.4rem;color:#fff;">📂 Tepe Duyuru Şablon & Taslak Kütüphanesi</h2>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("Mevcut tasarımları kaydetme ekranı ve şablon kütüphanesi sayesinde, önceden hazırladığınız duyuru bandı tasarımlarını kaybetmeden dilediğiniz gibi saklayabilir ve tek tıkla canlandırabilirsiniz. Mevcut metin varken yeni sıfır tasarım alanını açıp farklı çalışmalar yapabilirsiniz!")

    taslaklar_col = db.collection("tepe_duyuru_taslaklari")
    
    # 1. Action buttons: Reset and Save
    col_reset, col_save_sec = st.columns([1, 1])
    with col_reset:
        st.write("✨ **Yeni / Sıfır Tasarım Başlat**")
        if st.button("➕ Yeni Sıfır Tasarım Ekranı Aç (Sıfırla)", use_container_width=True, type="secondary", help="Editördeki tüm yazıları ve stilleri temizleyerek yepyeni boş bir duyuru tasarlamaya başlamanızı sağlar (aktif yayındaki duyurunuzu etkilemez)."):
            st.session_state.temp_ann_settings = {
                "text": "YENİ DUYURU BANDI",
                "size": 20,
                "font": "sans-serif",
                "bg_type": "none",
                "bg_color": "#111122",
                "bg_gradient_end": "#1a1a3a",
                "bg_image_url": "",
                "bg_opacity": 100,
                "glow_enabled": False,
                "glow_intensity": 50,
                "glow_color_mode": "auto",
                "glow_color_fixed": "#FFC000",
                "shadow_enabled": False,
                "shadow_intensity": 50,
                "shadow_color": "#000000",
                "opacity": 100,
                "font_weight": "bold",
                "font_style": "normal",
                "text_decoration": "none",
                "displacement_x": 0,
                "displacement_y": 0,
                "rotation": 0,
                "animation_type": "none",
                "media_url": "",
                "media_size": 150,
                "media_align": "bottom",
                "padding_vertical": 10,
                "padding_horizontal": 15,
                "border_radius": 12,
                "char_colors": [],
                "align": "center",
                "text_color": "#FFFFFF"
            }
            st.success("✅ Editör alanları sıfırlandı! Yeni tasarımınızı yapmaya başlayabilirsiniz.")
            time.sleep(1)
            st.rerun()
            
    with col_save_sec:
        st.write("💾 **Mecvut Tasarımı Taslak Olarak Sakla**")
        taslak_name_input = st.text_input("Taslak Başlığı / İsmi:", placeholder="Örn: Hafta Sonu Maçı Duyurusu", key="new_taslak_title", label_visibility="collapsed")
        if st.button("💾 Mevcut Tasarımı Taslak Olarak Ekle", use_container_width=True, type="primary"):
            if not taslak_name_input.strip():
                st.warning("⚠️ Lütfen taslağınıza bir isim belirleyin!")
            else:
                try:
                    taslak_payload = dict(st.session_state.temp_ann_settings)
                    taslak_payload["taslak_adi"] = taslak_name_input.strip()
                    taslak_payload["created_at"] = datetime.now(timezone.utc).isoformat() if 'datetime' in globals() else time.strftime('%Y-%m-%dT%H:%M:%SZ')
                    taslaklar_col.add(taslak_payload)
                    st.success(f"✅ '{taslak_name_input}' ismiyle yeni taslak kütüphaneye başarıyla kaydedildi!")
                    time.sleep(1)
                    st.rerun()
                except Exception as ex:
                    st.error(f"Taslak kaydedilirken teknik bir sorun oluştu: {ex}")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # 2. Fetch and render Saved Templates
    try:
        taslak_docs = taslaklar_col.get()
        taslak_list = []
        for doc in taslak_docs:
            d = doc.to_dict()
            d["id"] = doc.id
            taslak_list.append(d)
        
        # Sort manual by date
        taslak_list = sorted(taslak_list, key=lambda x: x.get("created_at", ""), reverse=True)
    except Exception as e:
        taslak_list = []
        st.error(f"Taslak kütüphanesi yüklenirken hata: {e}")

    st.markdown("### 🗄️ Kayıtlı Taslaklarınız")
    if not taslak_list:
        st.info("Kayıtlı herhangi bir duyuru tasarımı ve şablon bulunamadı. Yapmış olduğunuz benzersiz tasarımları yukarıdaki kısımdan 'Mevcut Tasarımı Taslak Olarak Ekle' butonuyla kaydedebilirsiniz!")
    else:
        for t in taslak_list:
            t_id = t["id"]
            t_name = t.get("taslak_adi", "İeraktif Duyuru Taslağı")
            t_text = t.get("text", "")
            t_date = t.get("created_at", "")[:19].replace("T", " ") if t.get("created_at") else "Tarih Yok"
            
            with st.expander(f"📁 {t_name} (Önizleme: {t_text[:30]}...)", expanded=False):
                st.markdown(f"""
                <div style="background: rgba(0, 0, 0, 0.2); border-left: 4px solid #3498db; padding: 10px; border-radius: 4px; margin-bottom: 12px;">
                    <p style="margin:0;font-size:0.85rem;color:#7f8c8d;">🗓️ Kayıt Tarihi: {t_date}</p>
                    <p style="margin:5px 0 0;font-size:0.95rem;color:#ecf0f1;"><b>Duyuru Metni:</b> {t_text}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Three controller buttons
                col_load, col_publish, col_delete = st.columns([1, 1.2, 1])
                
                with col_load:
                    if st.button("✏️ Düzenle (Editöre Yükle)", key=f"t_load_{t_id}", use_container_width=True, help="Bu şablon stilini ve yazısını yukarıdaki canlı editör paneline yükler. Üzerinde değişiklikler yapabilirsiniz."):
                        loaded_cfg = dict(t)
                        loaded_cfg.pop("id", None)
                        loaded_cfg.pop("taslak_adi", None)
                        loaded_cfg.pop("created_at", None)
                        st.session_state.temp_ann_settings = loaded_cfg
                        st.success("✅ Taslak editöre yüklendi! Sayfa yenileniyor...")
                        time.sleep(1)
                        st.rerun()
                        
                with col_publish:
                    if st.button("🚀 Canlı Yayına Al & Dağıt", key=f"t_pub_{t_id}", use_container_width=True, help="Bu tasarıyı doğrudan sitenin en üstündeki aktif duyuru bandına yansıtır ve tüm kullanıcılar için canlıya alır."):
                        loaded_cfg = dict(t)
                        loaded_cfg.pop("id", None)
                        loaded_cfg.pop("taslak_adi", None)
                        loaded_cfg.pop("created_at", None)
                        
                        # Save directly database as active announcement
                        db.collection("settings").document("global_announcement").set(loaded_cfg)
                        trigger_global_rerun(exclude_self=False)
                        st.session_state.temp_ann_settings = loaded_cfg
                        st.success("🎉 Şablon başarıyla sitenin en üstüne canlı yayına alındı!")
                        time.sleep(1)
                        st.rerun()
                        
                with col_delete:
                    if st.button("🗑️ Şablonu Kalıcı Olarak Sil", key=f"t_del_{t_id}", use_container_width=True, type="secondary"):
                        taslaklar_col.document(t_id).delete()
                        st.success("🗑️ Taslak kütüphaneden başarıyla silindi.")
                        time.sleep(1)
                        st.rerun()
import re
from datetime import datetime, timezone, timedelta
import time
import unicodedata
import tempfile
import base64
from io import BytesIO
from PIL import Image

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Kaplan Parçası V18.1",
    page_icon="🐯",
    layout="centered"
)

# --- GOOGLE TRANSLATE ENGELLEME + GLOBAL UI TWEAKS ---
st.markdown("""
<meta name="google" content="notranslate">
<meta http-equiv="Content-Language" content="tr">

<style>
  /* === SEAMLESS STREAMLIT HACKS FOR INSTANT NATIVE FEEL === */
  [data-testid="stStatusWidget"], .stStatusWidget {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    height: 0 !important;
    width: 0 !important;
  }
  [data-testid="stConnectionStatus"], .stConnectionStatus, #connection-status {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    height: 0 !important;
    width: 0 !important;
  }
  /* Lock app container opacities & filters to prevent any visual blinks, fades or flashes on reruns */
  [data-testid="stAppViewContainer"], [data-testid="stApp"], [data-testid="stAppViewBlockContainer"], .stApp {
    opacity: 1 !important;
    filter: none !important;
    transition: none !important;
  }
  [data-testid="stApp"]::before {
    display: none !important;
  }

  /* === STREAMLIT HEADER VE SIDEBAR DÜZELTMESİ === */
  [data-testid="stHeader"] { 
    background: transparent !important;
    z-index: 999997 !important;
    height: auto !important;
    min-height: 0 !important;
  }

  /* === ÜST BOŞLUK KALDIR === */
  [data-testid="stAppViewBlockContainer"],
  .block-container {
    padding-top: 0.5rem !important;
  }
  [data-testid="stAppViewContainer"] > section > div.block-container {
    padding-top: 0.5rem !important;
  }
  [data-testid="stMainBlockContainer"] {
    padding-top: 0.5rem !important;
  }

  /* === GOOGLE TRANSLATE TAM ENGELLEME === */
  .goog-te-banner-frame, .goog-te-menu-value, #goog-gt-tt,
  .goog-tooltip, .goog-tooltip:hover, .goog-te-balloon-frame,
  div#goog-gt-tt, .VIpgJd-ZVi9od-ORHb-OEVmcd,
  .goog-te-gadget, .goog-te-gadget-simple,
  .goog-te-spinner-pos, .goog-te-ftab-frame,
  #google_translate_element, .skiptranslate,
  [class*="goog-te"], [id*="goog-gt"],
  iframe[src*="translate.google"], iframe.goog-te-menu-frame,
  .VIpgJd-ZVi9od-aZ2wEe-wOHMyf { display: none !important; visibility: hidden !important; height: 0 !important; width: 0 !important; overflow: hidden !important; }
  body { top: 0 !important; position: static !important; }
  body.translated-ltr, body.translated-rtl { top: 0 !important; }
  .notranslate { translate: no; }
  font[style*="vertical-align"] { display: none !important; }
  html[class*="translated"] { top: 0 !important; }
  html[class*="translated"] body { top: 0 !important; }

  /* === ℹ️ BİLGİ BUTONU - SAĞ ÜST, 3 NOKTA ALTINDA === */
  div[data-testid="stPopover"] {
    position: fixed !important;
    top: 50px !important;
    right: 15px !important;
    z-index: 999998 !important;
    width: auto !important;
    height: auto !important;
    max-width: 44px !important;
    margin: 0 !important;
    padding: 0 !important;
    pointer-events: auto !important;
  }
  div[data-testid="stPopover"] button:first-child {
    border: 1px solid rgba(255,255,255,0.25) !important;
    border-radius: 50% !important;
    width: 40px !important;
    height: 40px !important;
    min-width: 40px !important;
    min-height: 40px !important;
    max-width: 40px !important;
    max-height: 40px !important;
    padding: 0 !important;
    font-size: 1.1rem !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.6) !important;
    cursor: pointer !important;
    pointer-events: auto !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    transition: all 0.2s ease !important;
  }
  div[data-testid="stPopover"] button:first-child:hover {
    transform: scale(1.05) !important;
    border-color: rgba(255,215,0,0.5) !important;
  }

  /* === MODERN BUTON STİLLERİ === */
  [data-testid="stSidebar"] button[kind="secondary"] {
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    padding: 8px 14px !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
    background: rgba(255,255,255,0.04) !important;
  }
  [data-testid="stSidebar"] button[kind="secondary"]:hover {
    background: rgba(255,255,255,0.10) !important;
    border-color: rgba(255,255,255,0.25) !important;
    transform: translateY(-1px) !important;
  }
  [data-testid="stSidebar"] button[kind="primary"] {
    border-radius: 10px !important;
    padding: 8px 14px !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
  }
  [data-testid="stSidebar"] button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(255,75,75,0.3) !important;
  }
  /* Ana sayfa butonları */
  [data-testid="stMainBlockContainer"] button[kind="primary"] {
    border-radius: 10px !important;
    padding: 10px 18px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
  }
  [data-testid="stMainBlockContainer"] button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(255,75,75,0.3) !important;
  }
  [data-testid="stMainBlockContainer"] button[kind="secondary"] {
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    padding: 10px 18px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
    background: rgba(255,255,255,0.04) !important;
  }
  [data-testid="stMainBlockContainer"] button[kind="secondary"]:hover {
    background: rgba(255,255,255,0.10) !important;
    border-color: rgba(255,255,255,0.25) !important;
    transform: translateY(-1px) !important;
  }
  /* İkon buton stili */
  .icon-btn-wrapper {
    display: inline-flex;
    align-items: center;
    gap: 8px;
  }
  .icon-btn-wrapper svg {
    width: 16px;
    height: 16px;
    flex-shrink: 0;
    opacity: 0.9;
  }
</style>
""", unsafe_allow_html=True)

# Google Translate JS TAM engeli
components.html("""
<script>
  (function() {
    var pd = window.parent.document;
    var html = pd.documentElement;

    // 1. Meta etiketleri ekle
    var m1 = document.createElement('meta');
    m1.name = 'google'; m1.content = 'notranslate';
    pd.head.appendChild(m1);
    var m2 = document.createElement('meta');
    m2.httpEquiv = 'Content-Language'; m2.content = 'tr';
    pd.head.appendChild(m2);

    // 2. HTML lang="tr" ayarla - Chrome çeviri teklif etmesin
    html.setAttribute('lang', 'tr');
    html.setAttribute('translate', 'no');
    html.classList.add('notranslate');
    if (pd.body) {
      pd.body.setAttribute('translate', 'no');
      pd.body.classList.add('notranslate');
      pd.body.setAttribute('lang', 'tr');
    }

    // 3. Tüm Streamlit elementlerine translate=no ekle
    var sel = '[data-testid="stApp"],[data-testid="stSidebar"],.main,.block-container,p,span,div,h1,h2,h3,h4,h5,h6,li,td,th,label,input,textarea';
    pd.querySelectorAll(sel).forEach(function(el) {
      el.setAttribute('translate', 'no');
      el.classList.add('notranslate');
    });

    // 4. Google Translate API'sini tamamen engelle
    try { Object.defineProperty(window.parent, 'google', { value: undefined, writable: false, configurable: false }); } catch(e) {}
    try { Object.defineProperty(window.parent, 'googleTranslateElementInit', { value: function(){}, writable: false, configurable: false }); } catch(e) {}

    // 5. Agresif MutationObserver - çeviri elementlerini anında kaldır
    var translateObs = new MutationObserver(function(muts) {
      // translated class'larını kaldır
      if (html.classList.contains('translated-ltr')) html.classList.remove('translated-ltr');
      if (html.classList.contains('translated-rtl')) html.classList.remove('translated-rtl');
      // body top offset'ini sıfırla (çeviri barı body'i aşağı iter)
      if (pd.body && pd.body.style.top !== '0px') pd.body.style.top = '0px';

      muts.forEach(function(mut) {
        // Eklenen çeviri elementlerini kaldır
        mut.addedNodes.forEach(function(node) {
          if (node.nodeType === 1) {
            var cls = node.className || '';
            var id = node.id || '';
            var tag = node.tagName || '';
            if (cls.indexOf('goog-te') !== -1 || cls.indexOf('skiptranslate') !== -1 ||
                id.indexOf('goog-gt') !== -1 || id.indexOf('google_translate') !== -1 ||
                (tag === 'IFRAME' && node.src && node.src.indexOf('translate') !== -1)) {
              node.remove();
            }
          }
        });
        // translate attribute eklenirse geri al
        if (mut.type === 'attributes' && mut.attributeName === 'class') {
          var t = mut.target;
          if (t.classList && (t.classList.contains('translated-ltr') || t.classList.contains('translated-rtl'))) {
            t.classList.remove('translated-ltr', 'translated-rtl');
          }
        }
      });
    });
    translateObs.observe(html, { childList: true, subtree: true, attributes: true, attributeFilter: ['class', 'style'] });

    // 6. Yeni eklenen elementlere de translate=no ekle
    var newElObs = new MutationObserver(function(muts) {
      muts.forEach(function(mut) {
        mut.addedNodes.forEach(function(node) {
          if (node.nodeType === 1 && !node.classList.contains('notranslate')) {
            node.setAttribute('translate', 'no');
            node.classList.add('notranslate');
          }
        });
      });
    });
    newElObs.observe(pd.body || html, { childList: true, subtree: true });
  })();

  // --- IFRAME FOCUS RESTORE ---
  // WhatsApp vb. pencere-içi-pencere iframe'leri focus'u çaldığında
  // kullanıcı ana sayfaya tıklayınca Streamlit input'larına yeniden focus ver
  (function() {
    var pd = window.parent.document;
    pd.addEventListener('click', function(e) {
      // Eğer tıklanan element bir iframe değilse, focus'u window'a geri al
      if (e.target.tagName !== 'IFRAME') {
        window.parent.focus();
        window.focus();
        // Ayrıca eğer bir textarea veya input elementine tıklanmışsa doğrudan ona focus ver
        if (e.target.tagName === 'TEXTAREA' || e.target.tagName === 'INPUT') {
          e.target.focus();
        }
      }
    }, true);
    // Ayrıca "focusin" ile de yakala - iframe'den çıkınca tetiklenir
    window.parent.addEventListener('focus', function() {
      // iframe'lerden dönen focus'u temizle
      var active = pd.activeElement;
      if (active && active.tagName === 'IFRAME') {
        active.blur();
        window.parent.focus();
        window.focus();
      }
    });
  })();

  // --- MODERN SVG İKON BUTONLARI ---
  (function() {
    var pd = window.parent.document;
    var icons = {
      'Temay': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="13.5" cy="6.5" r="2.5"/><path d="M19 2s3 2 3 6-3 6-3 6"/><circle cx="6" cy="12" r="2"/><circle cx="10" cy="18" r="2"/><circle cx="18" cy="16" r="2"/><circle cx="6" cy="18" r="0"/><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10"/></svg>',
      'Sohbeti Temizle': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>',
      'k\\u0131\\u015f Yap': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>',
      'Hesab': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
      'Hesabım': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
      'YouTube Portal': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"/></svg>',
      'netici Panel': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.6 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.6a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
      'Sohbet': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
      'Duyuru': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>',
      'smi G': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>',
      'Kullan': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
      'Rol Y': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
      'Listeyi Yenile': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>',
      'Kaydet': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>',
      'Paneline D': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>',
      'Ekran': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>',
      'G\\u00f6nder': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>',
      '\\ud83d\\udce4': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>',
      'ifre': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>',
      'Sil': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>',
      'Ayarlar': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.6 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.6a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
      'Geri': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>',
      '🔔': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>',
      '🔴': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/><circle cx="18" cy="6" r="3.5" fill="red" stroke="none"/></svg>'
    };

    function injectIcons() {
      var btns = pd.querySelectorAll('button[kind] p, button[data-testid] p');
      btns.forEach(function(p) {
        if (p.getAttribute('data-icons-done')) return;
        var origTxt = p.textContent || '';
        var txt = origTxt;
        if (txt.indexOf('✎') === -1) {
          var emojiRe = new RegExp('[\\uD83C-\\uDBFF][\\uDC00-\\uDFFF]|[\\u2600-\\u27BF]|\\uFE0F', 'g');
          if (emojiRe.test(txt)) {
            emojiRe.lastIndex = 0;
            Array.from(p.childNodes).forEach(function(n) {
              if (n.nodeType === 3) {
                var cleanRe = new RegExp('[\\uD83C-\\uDBFF][\\uDC00-\\uDFFF]|[\\u2600-\\u27BF]|\\uFE0F', 'g');
                n.textContent = n.textContent.replace(cleanRe, '').replace(/^ +/, '');
              }
            });
            txt = p.textContent || '';
          }
        }
        for (var key in icons) {
          if (txt.indexOf(key) !== -1 || origTxt.indexOf(key) !== -1) {
            var span = pd.createElement('span');
            span.className = 'st-icon-svg';
            span.innerHTML = icons[key];
            span.style.cssText = 'display:inline-flex;align-items:center;margin-right:6px;vertical-align:middle;width:16px;height:16px;';
            span.querySelector('svg').style.cssText = 'width:16px;height:16px;';
            p.insertBefore(span, p.firstChild);
            break;
          }
        }
        p.setAttribute('data-icons-done', '1');
      });
    }

    function setupInputHandlers() {
      var textareas = pd.querySelectorAll('textarea, input[data-testid="stTextInput"] input');
      textareas.forEach(function(el) {
        if (el.getAttribute('data-handlers-done')) return;
        el.setAttribute('data-handlers-done', 'true');
        
        el.addEventListener('keydown', function(e) {
          if (e.key === 'Enter') {
            // Check if it is the DM chat textarea so we let the mobile keyboards naturally go to next line!
            var keyAttr = el.getAttribute('key') || '';
            var placeholder = el.getAttribute('placeholder') || '';
            if (placeholder.includes('Mesaj\u0131n\u0131z...') || keyAttr.includes('dm_text_input') || placeholder.includes('Mesaj yaz...')) {
              // Mobile / Desktop Enter must naturally add a newline and NOT submit
              return;
            }
            if (e.shiftKey) {
              if (el.tagName === 'INPUT') {
                e.preventDefault();
              }
            } else {
              e.preventDefault();
              
              // Safe closest fallback for mobile compatibility
              var container = null;
              if (el.closest) {
                container = el.closest('div[data-testid="element-container"]');
              } else {
                var current = el;
                while (current) {
                  if (current.getAttribute && current.getAttribute('data-testid') === 'element-container') {
                    container = current;
                    break;
                  }
                  current = current.parentElement;
                }
              }
              
              var parentSection = container ? container.parentElement : null;
              var sendBtn = null;
              if (parentSection) {
                sendBtn = parentSection.querySelector('button[key*="send"], button[key*="gonder"], button[key*="btn"]');
                if (!sendBtn) {
                  sendBtn = Array.from(parentSection.querySelectorAll('button')).find(function(b) {
                    var text = b.textContent || '';
                    return text.includes('🚀') || text.includes('📤') || text.includes('Gönder') || text.includes('Send') || text.includes('Yaz');
                  });
                }
              }
              if (!sendBtn) {
                sendBtn = pd.querySelector('button[key*="send"], button[key*="gonder"], button[key*="btn"]');
              }
              if (sendBtn) {
                sendBtn.click();
              }
            }
          }
        });

        el.addEventListener('focus', function() {
          setTimeout(function() {
            el.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }, 300);
        });
      });
    }

    setTimeout(function() { injectIcons(); setupInputHandlers(); }, 500);

    // Delegated click on body to handle click on profile photo regardless of timing or rerenders
    if (!pd.avatarClickBound) {
      pd.avatarClickBound = true;
      pd.addEventListener('click', function(e) {
        var avatar = e.target.closest('.profil-avatar-wrap');
        if (avatar) {
          var uploader = pd.querySelector('[data-testid="stFileUploader"] input[type="file"]');
          if (uploader) {
            uploader.click();
          }
        }
      });
    }

    var btnObs = new MutationObserver(function() {
      setTimeout(function() { injectIcons(); setupInputHandlers(); }, 100);
    });
    btnObs.observe(pd.body || pd.documentElement, { childList: true, subtree: true });
  })();
</script>
""", height=0, width=0)

# --- AYARLAR ---
KURUCU_EMAIL = "ayazscma92@gmail.com"
KURUCU_ISIM = "Ayaz Kaplan"
MODEL = "anthropic/claude-3-haiku"
AVATAR_URL = "https://i.imgur.com/3EfO8Ae.jpeg"
USER_AVATAR = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

FIREBASE_API_KEY = os.environ.get("FIREBASE_API_KEY")
OPENROUTER_API_KEY = os.environ.get("API_KEY")

if not FIREBASE_API_KEY:
    st.error("❌ Firebase API anahtarı (FIREBASE_API_KEY) ortam değişkenlerinde bulunamadı!")
    st.stop()

if not OPENROUTER_API_KEY:
    st.error("❌ OpenRouter API anahtarı (API_KEY) ortam değişkenlerinde bulunamadı!")
    st.stop()

# --- TEMALAR ---
TEMALAR = {
    "🐯 Kaplan İni": "linear-gradient(135deg, #0f2027, #203a43, #2c5364)",
    "👑 Kraliyet": "linear-gradient(135deg, #1a0000, #4a0000, #8b0000)",
    "🌲 Orman Derinliği": "linear-gradient(135deg, #061700, #142f10, #2c4a2c)",
    "💻 Teknoloji": "linear-gradient(135deg, #000428, #004e92)",
    "🌌 Uzay": "linear-gradient(135deg, #0f0c29, #302b63, #24243e)"
}

# --- TEMA RENK HARİTASI (Bilgi butonu için) ---
TEMA_RENKLERI = {
    "linear-gradient(135deg, #0f2027, #203a43, #2c5364)": "rgba(44, 83, 100, 0.85)",
    "linear-gradient(135deg, #1a0000, #4a0000, #8b0000)": "rgba(139, 0, 0, 0.85)",
    "linear-gradient(135deg, #061700, #142f10, #2c4a2c)": "rgba(44, 74, 44, 0.85)",
    "linear-gradient(135deg, #000428, #004e92)": "rgba(0, 78, 146, 0.85)",
    "linear-gradient(135deg, #0f0c29, #302b63, #24243e)": "rgba(36, 36, 62, 0.85)"
}

# --- FIREBASE BAŞLATMA ---
if not firebase_admin._apps:
    gac_env = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    secret_path = "/etc/secrets/firebase-key.json"
    local_path = "firebase-key.json"

    if gac_env:
        try:
            cred_dict = json.loads(gac_env)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            st.error(f"❌ Firebase başlatılamadı: GOOGLE_APPLICATION_CREDENTIALS geçersiz. ({e})")
            st.stop()
    elif os.path.exists(secret_path):
        with open(secret_path, 'r') as f:
            cred = credentials.Certificate(json.load(f))
            firebase_admin.initialize_app(cred)
    elif os.path.exists(local_path):
        with open(local_path, 'r') as f:
            cred = credentials.Certificate(json.load(f))
            firebase_admin.initialize_app(cred)
    else:
        st.error("❌ Firebase anahtarı bulunamadı! Lütfen GOOGLE_APPLICATION_CREDENTIALS secret'ını ayarlayın.")
        st.stop()

db = firestore.client()

# --- YARDIMCI FONKSİYONLAR ---
def trigger_global_rerun(exclude_self=True):
    try:
        from streamlit.runtime import get_instance
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        runtime = get_instance()
        if runtime:
            ctx = get_script_run_ctx()
            current_session_id = ctx.session_id if ctx else None
            session_infos = list(runtime._session_info_by_id.values())
            for info in session_infos:
                if exclude_self and current_session_id and info.session.id == current_session_id:
                    continue
                info.session.request_rerun()
    except Exception as e:
        print(f"[GLOBAL RERUN ERROR] {e}")

def normalize_text(text):
    if not text:
        return ""
    # Normalize Turkish characters to English counterparts
    tr_map = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
    text = text.translate(tr_map).lower()
    return re.sub(r'[^a-zA-Z0-9\s]', '', text)

def kufur_var_mi(text):
    if not text:
        return False
    
    # 1. Normalize Turkish characters and keep spaces
    normalized = normalize_text(text)
    
    # 2. Get individual words by splitting on word boundaries
    words = re.findall(r'\b\w+\b', normalized)
    
    # 3. Severe swear words list (only actual severe profanity, NO mild slang like "lan", "salak", "mal", "bok", "gerizekali")
    severe_profanity_words = {
        # Turkish severe swear words
        "amk", "amq", "aq", "amcik", "orospu", "yarrak", "yarak", "sikerim", "sikeyim", 
        "sikis", "sik", "siki", "pic", "gavat", "kahpe", "yavsak", "dalyarak", "kancik", 
        "ibne", "pezevenk", "amciklar", "got", "gotveren", "orospunun", "orospular",
        # English severe profanity
        "fuck", "fucking", "bitch", "cunt", "whore", "slut", "asshole", "motherfucker"
    }
    
    # 4. Check for direct word matches (extremely precise, no false positives on "normal", "salatalik", etc.)
    for w in words:
        if w in severe_profanity_words:
            return True
            
    # 5. Check for concatenated forms of severe profanity (e.g. "aminakoyim", "orospucocugu")
    condensed = re.sub(r'[^a-z0-9]', '', normalized)
    severe_phrases = [
        "aminakoy", "aminakoyim", "aminakoyayim", "orospucocu", "orospucocugu", "orspucocu",
        "ananisik", "ananisikeyim", "gotunuesik", "sikeyim", "sikerim", "gotsiken"
    ]
    for phrase in severe_phrases:
        if phrase in condensed:
            return True
            
    return False

def emoji_var_mi(text):
    emoji_pattern = re.compile("[" "\U00010000-\U0010ffff" "\u2600-\u27bf" "]+", flags=re.UNICODE)
    return bool(emoji_pattern.search(text))

def get_video_iframe(video_id):
    return f'<iframe width="100%" height="200" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe>'

def get_global_announcement():
    try:
        doc = db.collection("settings").document("global_announcement").get()
        if doc.exists:
            # Provide solid fallback values for any newly added fields
            d = doc.to_dict()
            defaults = {
                "text": "",
                "size": 20,
                "font": "sans-serif",
                "bg_type": "none",
                "bg_color": "#111122",
                "bg_gradient_end": "#1a1a3a",
                "bg_image_url": "",
                "bg_opacity": 100,
                "glow_enabled": False,
                "glow_intensity": 50,
                "glow_color_mode": "auto",
                "glow_color_fixed": "#FFC000",
                "shadow_enabled": False,
                "shadow_intensity": 50,
                "shadow_color": "#000000",
                "opacity": 100,
                "font_weight": "normal",
                "font_style": "normal",
                "text_decoration": "none",
                "displacement_x": 0,
                "displacement_y": 0,
                "rotation": 0,
                "animation_type": "none",
                "media_url": "",
                "media_size": 150,
                "media_align": "bottom",
                "padding_vertical": 10,
                "padding_horizontal": 15,
                "border_radius": 12,
                "char_colors": [],
                "align": "center",
                "text_color": "#FFFFFF"
            }
            for k, v in defaults.items():
                if k not in d:
                    d[k] = v
            return d
    except Exception:
        pass
    return {
        "text": "",
        "size": 20,
        "font": "sans-serif",
        "bg_type": "none",
        "bg_color": "#111122",
        "bg_gradient_end": "#1a1a3a",
        "bg_image_url": "",
        "bg_opacity": 100,
        "glow_enabled": False,
        "glow_intensity": 50,
        "glow_color_mode": "auto",
        "glow_color_fixed": "#FFC000",
        "shadow_enabled": False,
        "shadow_intensity": 50,
        "shadow_color": "#000000",
        "opacity": 100,
        "font_weight": "normal",
        "font_style": "normal",
        "text_decoration": "none",
        "displacement_x": 0,
        "displacement_y": 0,
        "rotation": 0,
        "animation_type": "none",
        "media_url": "",
        "media_size": 150,
        "media_align": "bottom",
        "padding_vertical": 10,
        "padding_horizontal": 15,
        "border_radius": 12,
        "char_colors": [],
        "align": "center",
        "text_color": "#FFFFFF"
    }

def render_custom_banner_html(ann_data):
    # This returns safe, fully styled HTML of the banner
    ann_text = ann_data.get("text", "")
    font_family = ann_data.get("font", "sans-serif")
    align = ann_data.get("align", "center")
    size = ann_data.get("size", 20)
    font_weight = ann_data.get("font_weight", "bold")
    font_style = ann_data.get("font_style", "normal")
    text_decoration = ann_data.get("text_decoration", "none")
    opacity = ann_data.get("opacity", 100) / 100.0
    
    displacement_x = ann_data.get("displacement_x", 0)
    displacement_y = ann_data.get("displacement_y", 0)
    rotation = ann_data.get("rotation", 0)
    
    glow_enabled = ann_data.get("glow_enabled", False)
    glow_int = ann_data.get("glow_intensity", 50)
    glow_color_mode = ann_data.get("glow_color_mode", "auto")
    glow_color_fixed = ann_data.get("glow_color_fixed", "#FFC000")
    
    shadow_enabled = ann_data.get("shadow_enabled", False)
    shadow_int = ann_data.get("shadow_intensity", 50)
    shadow_color = ann_data.get("shadow_color", "#000000")
    
    bg_type = ann_data.get("bg_type", "none")
    bg_color = ann_data.get("bg_color", "#111122")
    bg_end = ann_data.get("bg_gradient_end", "#1a1a3a")
    bg_image_url = ann_data.get("bg_image_url", "")
    bg_opacity = ann_data.get("bg_opacity", 100) / 100.0
    padding_v = ann_data.get("padding_vertical", 10)
    padding_h = ann_data.get("padding_horizontal", 15)
    border_radius = ann_data.get("border_radius", 12)
    
    media_url = ann_data.get("media_url", "")
    media_size = ann_data.get("media_size", 150)
    media_align = ann_data.get("media_align", "bottom")
    
    animation_type = ann_data.get("animation_type", "none")
    
    # CSS Keyframes and styling wrapper (without leading line indent to keep Markdown compiler clean)
    css_definitions = """<style>
@keyframes neonPulse {
  0%, 100% { opacity: 0.45; filter: brightness(0.85); }
  50% { opacity: 1; filter: brightness(1.2); }
}
@keyframes wiggle {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  25% { transform: translateY(-4px) rotate(-1.5deg); }
  75% { transform: translateY(4px) rotate(1.5deg); }
}
@keyframes neonFlicker {
  0%, 19%, 21%, 23%, 25%, 54%, 56%, 100% { opacity: 1; }
  20%, 24%, 55% { opacity: 0.25; }
}
@keyframes rainbowShift {
  0% { filter: hue-rotate(0deg); }
  100% { filter: hue-rotate(360deg); }
}
@keyframes softPulse {
  0%, 100% { transform: scale(0.98); }
  50% { transform: scale(1.04); }
}
@keyframes blurFade {
  0%, 100% { filter: blur(0px); }
  50% { filter: blur(3px); }
}
.ann-animate-wiggle {
  display: inline-block;
  animation: wiggle 1.5s ease-in-out infinite;
}
.ann-animate-neon_pulse {
  display: inline-block;
  animation: neonPulse 2s infinite ease-in-out;
}
.ann-animate-neon_flicker {
  display: inline-block;
  animation: neonFlicker 3s infinite;
}
.ann-animate-rainbow {
  display: inline-block;
  animation: rainbowShift 6s infinite linear;
}
.ann-animate-pulse {
  display: inline-block;
  animation: softPulse 2.5s infinite ease-in-out;
}
.ann-animate-blur_fade {
  display: inline-block;
  animation: blurFade 3s infinite ease-in-out;
}
</style>"""
    
    # Shadows CSS
    shadow_css = ""
    if shadow_enabled:
        off = shadow_int * 0.08
        blur_s = shadow_int * 0.16
        shadow_css = f"{off:.1f}px {off:.1f}px {blur_s:.1f}px {shadow_color}"
        
    bg_css = "background: transparent; border: none; padding: 0;"
    if bg_type == "flat":
        bg_css = f"background: {bg_color}; border: 1px solid rgba(255,255,255,0.1); border-radius: {border_radius}px; padding: {padding_v}px {padding_h}px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.25);"
    elif bg_type == "gradient":
        bg_css = f"background: linear-gradient(135deg, {bg_color}, {bg_end}); border: 1px solid rgba(255,255,255,0.15); border-radius: {border_radius}px; padding: {padding_v}px {padding_h}px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.25);"
    elif bg_type == "image":
        overlay_op = 1.0 - (bg_opacity)
        bg_css = f"background: linear-gradient(rgba(17,17,34,{overlay_op:.2f}), rgba(17,17,34,{overlay_op:.2f})), url('{bg_image_url}'); background-size: cover; background-position: center; border: 1px solid rgba(255,255,255,0.15); border-radius: {border_radius}px; padding: {padding_v}px {padding_h}px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.25);"

    # Render characters
    char_colors = ann_data.get("char_colors", [])
    text_color_global = ann_data.get("text_color", "#FFFFFF")
    
    rendered_chars = []
    for char_idx, char in enumerate(ann_text):
        char_color = text_color_global
        if char_idx < len(char_colors) and char_colors[char_idx]:
            char_color = char_colors[char_idx]
            
        local_glow_color = char_color
        if glow_color_mode == "fixed":
            local_glow_color = glow_color_fixed
            
        glow_css = ""
        if glow_enabled:
            blur_1 = glow_int * 0.2
            blur_2 = glow_int * 0.4
            glow_css = f"0 0 {blur_1:.1f}px {local_glow_color}, 0 0 {blur_2:.1f}px {local_glow_color}"
            
        combined_shadows = ", ".join(filter(None, [glow_css, shadow_css]))
        shadow_style = f"text-shadow: {combined_shadows};" if combined_shadows else ""
        glow_val_style = f"--glow-color: {local_glow_color}; --gl-blur: {glow_int * 0.4:.1f}px;" if glow_enabled else ""
        
        italic_bold_style = f"font-weight: {font_weight}; font-style: {font_style}; text-decoration: {text_decoration};"
        anim_delay_style = f"animation-delay: {char_idx * 0.08:.2f}s;" if animation_type == "wiggle" else ""
        
        span_class = ""
        if animation_type in ["neon_pulse", "wiggle", "neon_flicker", "rainbow", "pulse", "blur_fade"]:
            span_class = f"ann-animate-{animation_type}"
            
        html_item = f'<span class="{span_class}" style="display: inline-block; white-space: pre-wrap; color: {char_color}; {glow_val_style} {shadow_style} {italic_bold_style} {anim_delay_style}">{char}</span>&#8203;'
        rendered_chars.append(html_item)
        
    ann_content_html = "".join(rendered_chars)
    
    # Media HTML
    media_html = ""
    if media_url:
        media_html = f'<img src="{media_url}" style="width: {media_size}px; height: auto; border-radius: 8px; margin: 8px; vertical-align: middle; max-width: 100%; box-shadow: 0 4px 12px rgba(0,0,0,0.4);" />'
        
    # Combine content based on media alignment
    if media_html:
        if media_align == "above":
            body_html = f'<div style="margin-bottom: 8px;">{media_html}</div><div>{ann_content_html}</div>'
        elif media_align == "below":
            body_html = f'<div>{ann_content_html}</div><div style="margin-top: 8px;">{media_html}</div>'
        elif media_align == "left":
            body_html = f'<div style="display: flex; align-items: center; justify-content: {align}; flex-wrap: wrap; gap: 15px;"><div>{media_html}</div><div style="flex: 1; text-align: {align};">{ann_content_html}</div></div>'
        elif media_align == "right":
            body_html = f'<div style="display: flex; align-items: center; justify-content: {align}; flex-wrap: wrap; gap: 15px;"><div style="flex: 1; text-align: {align};">{ann_content_html}</div><div>{media_html}</div></div>'
    else:
        body_html = f'<div>{ann_content_html}</div>'
        
    # Displacement style mapping
    displacement_style = f"transform: translate({displacement_x}px, {displacement_y}px) rotate({rotation}deg); transform-origin: center; opacity: {opacity};"
    
    # Create web fonts if they are cursive/google-based
    font_import = ""
    if font_family == "Space Grotesk":
        font_import = '<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;700&display=swap" rel="stylesheet">'
    elif font_family == "Cinzel":
        font_import = '<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700&display=swap" rel="stylesheet">'
        
    final_html = f"""{font_import}
{css_definitions}
<div style="{displacement_style} width: 100%; max-width: 100%; overflow: visible; position: relative; z-index: 1000; box-sizing: border-box;">
<div style="{bg_css} text-align: {align}; font-family: '{font_family}', sans-serif; font-size: {size}px; line-height: 1.4; width: 100%; max-width: 100%; box-sizing: border-box; overflow: visible; word-wrap: break-word; overflow-wrap: break-word; word-break: break-word;">
{body_html}
</div>
</div>"""
    
    # Strip any leading and trailing lines or spaces to guarantee no Markdown block preformatted trigger
    stripped_lines = [line.strip() for line in final_html.splitlines() if line.strip()]
    return "".join(stripped_lines)


def get_styled_user_name(u_name, u_color=None, u_glow=False, u_tag=None, u_rozet=None, email=None, is_admin=False):
    clean_name = str(u_name).strip().replace(" 👑", "").replace("🛠️", "").strip().lower()
    clean_email = str(email).strip().lower() if email else ""
    
    # 🌟 FORCE FOUNDER STYLING Rules
    if clean_email == "ayazscma92@gmail.com" or clean_name == "ayaz kaplan" or u_tag == "KURUCU":
        color_val = u_color if (u_color and u_color != "#FFFFFF") else "#FF0000"
        u_glow = True
        u_tag = u_tag if u_tag else "KURUCU"
        u_rozet = u_rozet if u_rozet else "🛠️"
    # 🌟 FORCE ADMIN STYLING Rules
    elif is_admin or u_tag == "YÖNETİCİ" or clean_name == "yönetici":
        color_val = u_color if (u_color and u_color != "#FFFFFF") else "#9b59b6"
        u_glow = True
        u_tag = u_tag if u_tag else "YÖNETİCİ"
        u_rozet = u_rozet if u_rozet else "🛡️"
    else:
        color_val = u_color if u_color else "#FFFFFF"
    
    glow_css = f"text-shadow: 0 0 10px {color_val}, 0 0 20px {color_val}, 0 0 30px {color_val};" if u_glow else ""
    tag_html = ""
    if u_tag:
        tag_html = f'<span style="font-size:0.8em; color:{color_val}; {glow_css} margin-right:5px;">[{u_tag}]</span>'
    
    isim_html = f'<span style="color:{color_val}; {glow_css} font-weight:bold;">{u_name}</span>'
    rozet_html = ""
    if u_rozet:
        rozet_html = f'<span style="margin-left:5px; filter: drop-shadow(0 0 6px {color_val});">{u_rozet}</span>' if u_glow else f'<span style="margin-left:5px;">{u_rozet}</span>'
    
    return f"{tag_html}{isim_html}{rozet_html}"

def get_tr_time():
    tr_tz = timezone(timedelta(hours=3))
    return datetime.now(tr_tz)

def ensure_utc(dt):
    if dt is None:
        return None
    if hasattr(dt, 'to_datetime'):
        dt = dt.to_datetime()
    if isinstance(dt, datetime) and dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt

def resize_profile_photo(image_bytes, max_size=150):
    """Profil fotoğrafını kare olarak yeniden boyutlandırır."""
    img = Image.open(BytesIO(image_bytes))
    img = img.convert("RGB")
    # Kare kırp (ortadan)
    w, h = img.size
    min_dim = min(w, h)
    left = (w - min_dim) // 2
    top = (h - min_dim) // 2
    img = img.crop((left, top, left + min_dim, top + min_dim))
    img = img.resize((max_size, max_size), Image.LANCZOS)
    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=80)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def web_ara(sorgu, max_sonuc=4):
    # Try using the standard DDGS package
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            sonuclar = list(ddgs.text(sorgu, max_results=max_sonuc, region="tr-tr"))
        if sonuclar:
            parcalar = []
            for s in sonuclar:
                baslik = s.get("title", "")
                icerik = s.get("body", "")
                if baslik or icerik:
                    parcalar.append(f"• {baslik}: {icerik}")
            return "\n".join(parcalar)
    except Exception:
        pass

    # Fallback to extremely robust html scrapper
    try:
        import requests
        from bs4 import BeautifulSoup
        import urllib.parse
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        res = requests.get(f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(sorgu)}", headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            parcalar = []
            results = soup.find_all("a", class_="result__snippet")
            if not results:
                # alternative selectors if duckduckgo html layout changes slightly
                results = soup.find_all("td", class_="result-snippet")
            
            for index, a in enumerate(results[:max_sonuc]):
                parent = a.find_parent("div", class_="result__body")
                title_el = None
                if parent:
                    title_el = parent.find("a", class_="result__url")
                if not title_el:
                    # fallback alternative selector
                    title_el = a.find_previous("a", class_="result__url")
                
                title = title_el.text.strip() if title_el else f"Sonuç #{index+1}"
                content = a.text.strip()
                if content:
                    parcalar.append(f"• {title}: {content}")
            if parcalar:
                return "\n".join(parcalar)
    except Exception:
        pass
    return ""

def youtube_ara(sorgu, max_sonuc=12):
    try:
        payload = {
            "context": {
                "client": {
                    "clientName": "WEB",
                    "clientVersion": "2.20231219.04.00",
                    "hl": "tr",
                    "gl": "TR"
                }
            },
            "query": sorgu
        }
        headers = {
            "Content-Type": "application/json",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8"
        }
        resp = requests.post(
            "https://www.youtube.com/youtubei/v1/search",
            json=payload,
            headers=headers,
            timeout=15
        )
        resp.raise_for_status()
        data = resp.json()

        sections = (
            data.get("contents", {})
            .get("twoColumnSearchResultsRenderer", {})
            .get("primaryContents", {})
            .get("sectionListRenderer", {})
            .get("contents", [])
        )

        sonuclar = []
        for section in sections:
            items = section.get("itemSectionRenderer", {}).get("contents", [])
            for item in items:
                vr = item.get("videoRenderer", {})
                if not vr:
                    continue
                vid_id = vr.get("videoId", "")
                if not vid_id:
                    continue
                title_runs = vr.get("title", {}).get("runs", [])
                title = title_runs[0].get("text", "") if title_runs else ""
                ch_runs = vr.get("ownerText", {}).get("runs", [])
                channel = ch_runs[0].get("text", "") if ch_runs else ""
                duration = vr.get("lengthText", {}).get("simpleText", "")
                views = vr.get("shortViewCountText", {}).get("simpleText", "")
                if not title:
                    continue
                sonuclar.append({
                    "id": vid_id,
                    "title": title,
                    "channel": channel,
                    "duration": duration,
                    "views": views,
                    "thumbnail": f"https://img.youtube.com/vi/{vid_id}/mqdefault.jpg"
                })
                if len(sonuclar) >= max_sonuc:
                    return sonuclar
        return sonuclar
    except Exception:
        return []

def log_hata(hata_tipi, kullanici_id="SYSTEM", detay=""):
    tr_tz = timezone(timedelta(hours=3))
    zaman = datetime.now(tr_tz).strftime("%Y-%m-%d %H:%M:%S")
    print(f"[HATA] Zaman: {zaman} | Kullanıcı ID: {kullanici_id} | Hata Tipi: {hata_tipi} | Detay: {detay}")

def firebase_hata_cevir(hata_kodu):
    hata_map = {
        "EMAIL_NOT_FOUND": "Bu e-posta adresiyle kayıtlı bir hesap bulunamadı.",
        "INVALID_PASSWORD": "Girilen şifre hatalı. Lütfen tekrar deneyin.",
        "INVALID_EMAIL": "Geçersiz e-posta formatı. Lütfen e-postanızı kontrol edin.",
        "INVALID_LOGIN_CREDENTIALS": "E-posta veya şifre hatalı. Lütfen bilgilerinizi kontrol edin.",
        "USER_DISABLED": "Bu hesap devre dışı bırakılmıştır. Destek için yönetici ile iletişime geçin.",
        "TOO_MANY_ATTEMPTS_TRY_LATER": "Çok fazla başarısız giriş denemesi. Lütfen birkaç dakika bekleyip tekrar deneyin.",
        "WEAK_PASSWORD": "Şifre çok kısa veya zayıf. En az 6 karakter kullanın.",
        "EMAIL_EXISTS": "Bu e-posta adresi zaten kayıtlıdır. Giriş yapmayı deneyin.",
        "OPERATION_NOT_ALLOWED": "Bu işlem şu an kullanılamıyor. Lütfen daha sonra tekrar deneyin.",
        "CONNECTION_TIMEOUT": "Bağlantı zaman aşımına uğradı. İnternet bağlantınızı kontrol edin.",
        "NETWORK_ERROR": "Ağ hatası oluştu. İnternet bağlantınızı kontrol edip tekrar deneyin.",
        "USER_NOT_FOUND": "Bu e-posta adresiyle kayıtlı bir hesap bulunamadı.",
    }
    if hata_kodu:
        for k, v in hata_map.items():
            if k and hata_kodu.upper().startswith(k):
                return v
    return f"Beklenmeyen bir hata oluştu. Lütfen tekrar deneyin. (Kod: {hata_kodu})"

def firebase_login(email, password):
    try:
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
        payload = {"email": email, "password": password, "returnSecureToken": True}
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            return response.json(), None
        err_data = response.json().get("error", {})
        err_msg = err_data.get("message", "UNKNOWN_ERROR")
        log_hata("FIREBASE_LOGIN_FAIL", email, err_msg)
        return None, err_msg
    except requests.exceptions.Timeout:
        log_hata("FIREBASE_LOGIN_TIMEOUT", email, "İstek zaman aşımı")
        return None, "CONNECTION_TIMEOUT"
    except Exception as e:
        log_hata("FIREBASE_LOGIN_EXCEPTION", email, str(e))
        return None, "NETWORK_ERROR"

def sifre_kaydet_firebase(uid, yeni_sifre):
    try:
        auth.update_user(uid, display_name=f"__pwd__{yeni_sifre}")
        db.collection("users").document(uid).update({"gizli_bilgi": yeni_sifre})
    except Exception as e:
        print(f"[ŞİFRE KAYIT HATASI] {e}")

# --- LOCAL STORAGE COMPONENT ---
COMP_DIR = os.path.join(tempfile.gettempdir(), "kaplan_ls_component")
os.makedirs(COMP_DIR, exist_ok=True)
HTML_PATH = os.path.join(COMP_DIR, "index.html")

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write("""
    <!DOCTYPE html>
    <html translate="no" class="notranslate">
    <head>
    <meta name="google" content="notranslate">
    <script>
      function sendMessage(type, data) {
        window.parent.postMessage(Object.assign({isStreamlitMessage: true, type: type}, data), "*");
      }
      
      // Listen to render events from Streamlit to support SET/REMOVE actions on the same origin!
      window.addEventListener("message", function(event) {
        if (event.data.type === "streamlit:render") {
          var args = event.data.args || {};
          var action = args.action; // "set", "remove" or not provided/"get"
          var key = args.key_name || args.key;
          var value = args.value;
          
          if (action === "set" && key) {
            localStorage.setItem(key, value);
            // Also write a backup cookie on parent/websocket domain
            try {
              window.parent.document.cookie = key + "=" + encodeURIComponent(value) + "; path=/; max-age=31536000; SameSite=Lax; Secure";
            } catch(e) {}
            document.cookie = key + "=" + encodeURIComponent(value) + "; path=/; max-age=31536000; SameSite=Lax; Secure";
          } else if (action === "remove" && key) {
            localStorage.removeItem(key);
            try {
              window.parent.document.cookie = key + "=; path=/; max-age=0";
            } catch(e) {}
            document.cookie = key + "=; path=/; max-age=0";
          }
          
          // Set frame height to 0 to make it invisible
          sendMessage("streamlit:setFrameHeight", {height: 0});
          
          // ONLY send component value back to Streamlit if we are READING (get).
          // Action "set" or "remove" should NOT send anything to avoid triggering infinite reruns!
          if (action !== "set" && action !== "remove") {
            var val = localStorage.getItem("kaplan_passkey") || "NOT_FOUND";
            var page = localStorage.getItem("kaplan_current_page") || "chat";
            sendMessage("streamlit:setComponentValue", {value: val + "|||" + page});
          }
        }
      });
      
      window.onload = function() {
          sendMessage("streamlit:componentReady", {apiVersion: 1});
      };
    </script></head>
    <body></body>
    </html>
    """)

get_local_storage = components.declare_component("get_local_storage", path=COMP_DIR)

# --- VOICE RECORDER COMPONENT ---
VOICE_COMP_DIR = os.path.join(tempfile.gettempdir(), "kaplan_voice_recorder")
os.makedirs(VOICE_COMP_DIR, exist_ok=True)
VOICE_HTML_PATH = os.path.join(VOICE_COMP_DIR, "index.html")

with open(VOICE_HTML_PATH, "w", encoding="utf-8") as f:
    f.write("""
    <!DOCTYPE html>
    <html translate="no" class="notranslate">
    <head>
    <meta name="google" content="notranslate">
    <style>
      body { margin: 0; padding: 0; background: transparent; overflow: hidden; }
      #rec-btn {
        background: #f39c12;
        border: none;
        border-radius: 10px;
        padding: 8px 14px;
        color: white;
        font-family: sans-serif;
        font-weight: 600;
        font-size: 0.85rem;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        transition: all 0.2s ease;
      }
      #rec-btn:hover {
        transform: scale(1.02);
        opacity: 0.95;
      }
      #audio-preview {
        margin-top: 8px;
        width: 100%;
        max-width: 250px;
        display: none;
      }
    </style>
    <script>
      let mediaRecorder;
      let chunks = [];
      let recording = false;
      let audioCtx;
      let micStream;
      let recordedMimeType = 'audio/webm';

      function sendMessage(type, data) {
        window.parent.postMessage(Object.assign({isStreamlitMessage: true, type: type}, data), "*");
      }

      window.onload = function() {
        sendMessage("streamlit:componentReady", {apiVersion: 1});
        sendMessage("streamlit:setFrameHeight", {height: 45});
      };

      async function toggleRec() {
        const btn = document.getElementById("rec-btn");
        const preview = document.getElementById("audio-preview");
        
        if (!recording) {
          try {
            // Access mic with standard high-quality constraints
            micStream = await navigator.mediaDevices.getUserMedia({
              audio: {
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true
              }
            });
            
            // Web Audio API for safe volume amplification
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            if (audioCtx.state === 'suspended') {
              await audioCtx.resume();
            }
            const source = audioCtx.createMediaStreamSource(micStream);
            const gainNode = audioCtx.createGain();
            gainNode.gain.setValueAtTime(3.5, audioCtx.currentTime); // 3.5x clean gain without harsh distortion
            const destination = audioCtx.createMediaStreamAudioDestination();
            
            source.connect(gainNode);
            gainNode.connect(destination);
            
            let options = {};
            recordedMimeType = 'audio/webm';
            if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
              options = { mimeType: 'audio/webm;codecs=opus', audioBitsPerSecond: 128000 };
              recordedMimeType = 'audio/webm;codecs=opus';
            } else if (MediaRecorder.isTypeSupported('audio/webm')) {
              options = { mimeType: 'audio/webm', audioBitsPerSecond: 128000 };
              recordedMimeType = 'audio/webm';
            } else if (MediaRecorder.isTypeSupported('audio/ogg')) {
              options = { mimeType: 'audio/ogg', audioBitsPerSecond: 128000 };
              recordedMimeType = 'audio/ogg';
            } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
              options = { mimeType: 'audio/mp4', audioBitsPerSecond: 128000 };
              recordedMimeType = 'audio/mp4';
            }
            
            mediaRecorder = new MediaRecorder(destination.stream, options);
            chunks = [];
            
            mediaRecorder.ondataavailable = e => chunks.push(e.data);
            mediaRecorder.onstop = () => {
              const blob = new Blob(chunks, { type: recordedMimeType });
              const url = URL.createObjectURL(blob);
              preview.src = url;
              preview.style.display = "block";
              sendMessage("streamlit:setFrameHeight", {height: 100});

              const reader = new FileReader();
              reader.readAsDataURL(blob);
              reader.onloadend = () => {
                const b64 = reader.result.split(',')[1];
                sendMessage("streamlit:setComponentValue", {value: b64});
              };
              
              if (audioCtx && audioCtx.state !== 'closed') {
                audioCtx.close();
              }
            };

            mediaRecorder.start();
            recording = true;
            btn.style.background = "#e74c3c";
            btn.innerHTML = '🔴 Kaydı Durdur';
          } catch(err) {
            alert("Mikrofon izni verilmedi veya bulunamadı!");
          }
        } else {
          if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
          }
          if (micStream) {
            micStream.getTracks().forEach(t => t.stop());
          }
          recording = false;
          btn.style.background = "#2ecc71";
          btn.innerHTML = '🎤 Sesi Gönder';
        }
      }
    </script>
    </head>
    <body>
      <div style="display: flex; flex-direction: column; align-items: flex-start;">
        <button id="rec-btn" onclick="toggleRec()">🎤 Ses Kaydet</button>
        <audio id="audio-preview" controls></audio>
      </div>
    </body>
    </html>
    """)

voice_recorder_component = components.declare_component("voice_recorder_component", path=VOICE_COMP_DIR)

def detect_and_render_media(content):
    if not isinstance(content, str):
        return content
    stripped = content.strip()
    if stripped.startswith("http://") or stripped.startswith("https://"):
        lower_url = stripped.lower()
        if lower_url.endswith(".gif") or any(x in lower_url for x in [".gif", "giphy.com/media/", "media.tenor.com", "klipy.com"]):
            return f'<img src="{stripped}" style="max-width:200px; border-radius:8px;" referrerPolicy="no-referrer"/>'
        elif any(lower_url.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"]):
            return f'<img src="{stripped}" style="max-width:200px; border-radius:8px;" referrerPolicy="no-referrer"/>'
    return content

# --- STATE YÖNETİMİ ---
if "user_logged_in" not in st.session_state: st.session_state.user_logged_in = False
if "user_data" not in st.session_state: st.session_state.user_data = None
if "messages" not in st.session_state: st.session_state.messages = []
if "tema" not in st.session_state: st.session_state.tema = list(TEMALAR.values())[0]
if "tema_rengi" not in st.session_state: st.session_state.tema_rengi = TEMA_RENKLERI.get(list(TEMALAR.values())[0], "rgba(20,20,40,0.85)")
if "valid_users_cache" not in st.session_state: st.session_state.valid_users_cache = None
if "current_page" not in st.session_state: st.session_state.current_page = "chat"
if "bildirim_panel_open" not in st.session_state: st.session_state.bildirim_panel_open = False
if "yt_results" not in st.session_state: st.session_state.yt_results = []
if "yt_playing_id" not in st.session_state: st.session_state.yt_playing_id = None
if "yt_playing_title" not in st.session_state: st.session_state.yt_playing_title = ""
if "yt_playing_channel" not in st.session_state: st.session_state.yt_playing_channel = ""
if "yt_last_id" not in st.session_state: st.session_state.yt_last_id = None
if "yt_last_title" not in st.session_state: st.session_state.yt_last_title = ""
if "yt_last_channel" not in st.session_state: st.session_state.yt_last_channel = ""
if "yt_ts_dict" not in st.session_state: st.session_state.yt_ts_dict = {}
if "yt_iframe_mounted" not in st.session_state: st.session_state.yt_iframe_mounted = False
if "yt_iframe_vid" not in st.session_state: st.session_state.yt_iframe_vid = ""
if "yt_audio_playing" not in st.session_state: st.session_state.yt_audio_playing = False
if "yt_resume_time" not in st.session_state: st.session_state.yt_resume_time = 0
if "global_player_container" not in st.session_state: st.session_state.global_player_container = None
if "global_player_rendered" not in st.session_state: st.session_state.global_player_rendered = False
if "global_player_rendered_vid" not in st.session_state: st.session_state.global_player_rendered_vid = None

def trigger_invalid_session():
    for key in list(st.session_state.keys()):
        if key not in ["tema", "tema_rengi", "yt_audio_playing", "yt_iframe_mounted", 
                       "yt_iframe_vid", "yt_resume_time", "yt_ts_dict", "yt_playing_id",
                       "yt_playing_title", "yt_playing_channel", "global_player_container",
                       "global_player_rendered", "global_player_rendered_vid",
                       "ban_error_on_logout"]:
            del st.session_state[key]
    st.session_state.trigger_clear_token = True
    st.rerun()

def logout_user():
    st.session_state.yt_audio_playing = False
    st.session_state.yt_iframe_mounted = False
    st.session_state.yt_playing_id = None
    st.session_state.yt_playing_title = ""
    st.session_state.yt_playing_channel = ""
    st.session_state.global_player_container = None
    st.session_state.global_player_rendered = False
    st.session_state.global_player_rendered_vid = None
    trigger_invalid_session()

# --- SESSİZ ARKA PLAN GÖREVLİLERİ ---
if st.session_state.get("trigger_clear_token", False):
    get_local_storage(action="remove", key_name="kaplan_passkey", key="token_clear_comp")
    get_local_storage(action="remove", key_name="kaplan_current_page", key="page_clear_comp")
    st.markdown("<h3 style='text-align:center; color:white; margin-top:20vh;'>Çıkış yapılıyor...</h3>", unsafe_allow_html=True)
    st.session_state.trigger_clear_token = False
    time.sleep(0.5)
    st.rerun()

if st.session_state.get("trigger_save_token"):
    uid = st.session_state.trigger_save_token
    get_local_storage(action="set", key_name="kaplan_passkey", value=uid, key="token_save_comp")
    st.session_state.trigger_save_token = None

# --- ADIM 0: ÇEREZDEN OTURUM OKUMA (Anlık Mobil ve Tab Yenilenme Çözümü) ---
if not st.session_state.user_logged_in and not st.session_state.get("trigger_clear_token", False):
    try:
        from streamlit.web.server.websocket_headers import _get_websocket_headers
        headers = _get_websocket_headers()
        if headers:
            cookie_str = headers.get("Cookie", "")
            if cookie_str:
                import urllib.parse
                cookies = {}
                for item in cookie_str.split(";"):
                    if "=" in item:
                        k, v = item.strip().split("=", 1)
                        if len(v) > 0:
                            cookies[k] = urllib.parse.unquote(v)
                
                c_passkey = cookies.get("kaplan_passkey")
                c_page = cookies.get("kaplan_current_page", "chat")
                c_last_active = cookies.get("kaplan_last_active")
                
                # Check 1 year inactivity timeout (effectively infinite to keep users logged in)
                import time
                current_epoch = time.time()
                is_inactive_timeout = False
                if c_last_active:
                    try:
                        elapsed_time = current_epoch - float(c_last_active)
                        if elapsed_time > 31536000: # 1 year inactivity
                            is_inactive_timeout = True
                    except Exception:
                        pass
                
                if c_passkey and c_passkey != "NOT_FOUND" and not is_inactive_timeout:
                    user_ref_temp = db.collection("users").document(c_passkey)
                    user_snap = user_ref_temp.get()
                    if user_snap.exists:
                        user_data = user_snap.to_dict()
                        user_durum = user_data.get("durum", "Aktif")
                        ban_bitis = user_data.get("ban_bitis_zamani")
                        if hasattr(ban_bitis, "to_datetime"):
                            ban_bitis = ban_bitis.to_datetime()
                        
                        is_banned = False
                        if user_durum == "Pasif":
                            if ban_bitis:
                                if ban_bitis.tzinfo is None: ban_bitis = ban_bitis.replace(tzinfo=timezone.utc)
                                if datetime.now(timezone.utc) < ban_bitis: is_banned = True
                            else:
                                is_banned = True
                        
                        if not is_banned:
                            user_ref_temp.update({"son_gorulme_zamani": firestore.SERVER_TIMESTAMP})
                            st.session_state.user_data = {**user_data, "uid": c_passkey}
                            st.session_state.user_logged_in = True
                            st.session_state.tema = user_data.get("tema", list(TEMALAR.values())[0])
                            st.session_state.tema_rengi = TEMA_RENKLERI.get(st.session_state.tema, "rgba(20,20,40,0.85)")
                            st.session_state.current_page = c_page
                            
                            sohbet_list = user_data.get("sohbet_gecmisi", [])
                            if isinstance(sohbet_list, list):
                                active_messages = []
                                last_separator_idx = -1
                                for idx, msg in enumerate(sohbet_list):
                                    if msg.get("role") == "separator": last_separator_idx = idx
                                if last_separator_idx != -1: active_messages = sohbet_list[last_separator_idx + 1:]
                                else: active_messages = [m for m in sohbet_list if m.get("role") in ["user", "assistant"]]
                                st.session_state.messages = active_messages
                            else:
                                st.session_state.messages = []
    except Exception:
        pass

# --- ADIM 1: TOKEN OKUMA ---
if not st.session_state.user_logged_in and not st.session_state.get("trigger_clear_token", False):

    token = get_local_storage(key="token_reader_comp")

    if token is None:
        st.markdown("""
        <div style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background-color: #0f2027; display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 999999; opacity: 0; animation: fadeIn 0.25s ease-out forwards 0.05s;">
            <div style="width: 56px; height: 56px; border: 5px solid rgba(255,255,255,0.1); border-top: 5px solid #f39c12; border-radius: 50%; animation: spin 0.75s linear infinite; will-change: transform; transform: translateZ(0);"></div>
            <h3 style="color: white; font-family: sans-serif; margin-top: 20px; letter-spacing: 0.04em; opacity: 0.92; text-align: center; width: 100%;">Geçiş Anahtarı Doğrulanıyor...</h3>
        </div>
        <style>
        @keyframes spin {
            0%   { transform: rotate(0deg) translateZ(0); }
            100% { transform: rotate(360deg) translateZ(0); }
        }
        @keyframes fadeIn {
            0%   { opacity: 0; }
            100% { opacity: 1; }
        }
        </style>
        """, unsafe_allow_html=True)
        st.stop()

    else:
        token_val = "NOT_FOUND"
        restored_page = "chat"
        if token and "|||" in token:
            parts = token.split("|||")
            token_val = parts[0]
            restored_page = parts[1] if len(parts) > 1 else "chat"
        else:
            token_val = token

        if token_val != "NOT_FOUND":
            try:
                user_ref_temp = db.collection("users").document(token_val)
                user_snap = user_ref_temp.get()
                if user_snap.exists:
                    user_data = user_snap.to_dict()
                    user_durum = user_data.get("durum", "Aktif")
                    ban_bitis = user_data.get("ban_bitis_zamani")

                    if hasattr(ban_bitis, "to_datetime"):
                        ban_bitis = ban_bitis.to_datetime()

                    is_banned = False
                    if user_durum == "Pasif":
                        if ban_bitis:
                            if ban_bitis.tzinfo is None: ban_bitis = ban_bitis.replace(tzinfo=timezone.utc)
                            if datetime.now(timezone.utc) < ban_bitis: is_banned = True
                        else:
                            is_banned = True

                    if not is_banned:
                        user_ref_temp.update({"son_gorulme_zamani": firestore.SERVER_TIMESTAMP})
                        st.session_state.user_data = {**user_data, "uid": token_val}
                        st.session_state.user_logged_in = True
                        st.session_state.tema = user_data.get("tema", list(TEMALAR.values())[0])
                        st.session_state.tema_rengi = TEMA_RENKLERI.get(st.session_state.tema, "rgba(20,20,40,0.85)")
                        
                        if restored_page and restored_page != "NOT_FOUND":
                            st.session_state.current_page = restored_page

                        sohbet_list = user_data.get("sohbet_gecmisi", [])
                        if isinstance(sohbet_list, list):
                            active_messages = []
                            last_separator_idx = -1
                            for idx, msg in enumerate(sohbet_list):
                                if msg.get("role") == "separator": last_separator_idx = idx
                            if last_separator_idx != -1: active_messages = sohbet_list[last_separator_idx + 1:]
                            else: active_messages = [m for m in sohbet_list if m.get("role") in ["user", "assistant"]]
                            st.session_state.messages = active_messages
                        else:
                            st.session_state.messages = []
                        st.rerun()
                    else:
                        st.session_state.ban_error_on_logout = "❌ Hesabınız pasifleştirildiği için giriş yapılamıyor!"
                        trigger_invalid_session()
                else:
                    trigger_invalid_session()
            except Exception:
                trigger_invalid_session()

# --- GİRİŞ VE KAYIT EKRANI ---
if not st.session_state.user_logged_in:

    _reset_token = st.query_params.get("reset_token", "")
    if _reset_token:
        st.title("🔑 Şifre Sıfırlama")
        try:
            _tdocs = db.collection("password_resets").where("token", "==", _reset_token).where("used", "==", False).limit(1).get()
            if _tdocs:
                _tdoc = _tdocs[0]
                _tdata = _tdoc.to_dict()
                _exp = ensure_utc(_tdata.get("expires_at"))
                if _exp and datetime.now(timezone.utc) < _exp:
                    st.info(f"📧 **{_tdata.get('email', '')}** hesabı için yeni şifre belirleyin.")
                    _pw1 = st.text_input("Yeni Şifre:", type="password", key="rst_pw1")
                    _pw2 = st.text_input("Yeni Şifre (Tekrar):", type="password", key="rst_pw2")
                    if st.button("✅ Şifreyi Güncelle", use_container_width=True, type="primary"):
                        if len(_pw1) < 6:
                            st.error("❌ Şifre en az 6 karakter olmalıdır!")
                        elif _pw1 != _pw2:
                            st.error("❌ Şifreler eşleşmiyor!")
                        else:
                            try:
                                auth.update_user(_tdata["uid"], password=_pw1, display_name=f"__pwd__{_pw1}")
                                db.collection("users").document(_tdata["uid"]).update({"gizli_bilgi": _pw1})
                                db.collection("password_resets").document(_tdoc.id).update({"used": True})
                                st.query_params.clear()
                                st.success("✅ Şifreniz başarıyla güncellendi! Giriş yapabilirsiniz.")
                                time.sleep(1)
                                st.rerun()
                            except Exception as _ue:
                                st.error(f"❌ Şifre güncellenemedi: {_ue}")
                else:
                    st.error("❌ Bu sıfırlama bağlantısının süresi dolmuş veya zaten kullanılmış.")
            else:
                st.error("❌ Geçersiz veya kullanılmış sıfırlama bağlantısı.")
        except Exception as _re:
            st.error(f"❌ Hata: {_re}")
        if st.button("← Giriş Sayfasına Dön"):
            st.query_params.clear()
            st.rerun()
        st.stop()

    st.title("🐯 Kaplan Parçası V18.1")

    if "ban_error_on_logout" in st.session_state:
        st.error(st.session_state.ban_error_on_logout)

    email = st.text_input("📧 E-posta (Sisteme Kayıtlı):")
    password = st.text_input("🔑 Şifre:", type="password")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Giriş Yap", use_container_width=True):
            st.session_state.pop("ban_error_on_logout", None)
            clean_email = email.strip().lower()
            auth_res, auth_err = firebase_login(clean_email, password)
            if auth_res:
                users_ref = db.collection("users")
                query = users_ref.where("email", "==", clean_email).limit(1).get()
                if query:
                    user_data = query[0].to_dict()
                    user_durum = user_data.get("durum", "Aktif")
                    ban_bitis = ensure_utc(user_data.get("ban_bitis_zamani"))

                    is_banned = False
                    if user_durum == "Pasif":
                        if ban_bitis:
                            now = datetime.now(timezone.utc)
                            if now < ban_bitis:
                                is_banned = True
                                kalan_sure = ban_bitis - now
                                kalan_dakika = int(kalan_sure.total_seconds() / 60)
                                if kalan_dakika < 1:
                                    st.error(f"❌ Hesabınız pasifleştirilmiştir. Kalan süre: {int(kalan_sure.total_seconds())} saniye")
                                else:
                                    st.error(f"❌ Hesabınız pasifleştirilmiştir. Kalan süre: {kalan_dakika} dakika")
                            else:
                                u_foto_backup = user_data.get("profil_foto_backup", "")
                                db.collection("users").document(query[0].id).update({
                                    "durum": "Aktif",
                                    "ban_bitis_zamani": None,
                                    "profil_foto": u_foto_backup if u_foto_backup else user_data.get("profil_foto", ""),
                                    "profil_foto_backup": ""
                                })
                                db.collection("banlanan_emails").document(clean_email).delete()
                                user_data["durum"] = "Aktif"
                                user_data["ban_bitis_zamani"] = None
                                if u_foto_backup:
                                    user_data["profil_foto"] = u_foto_backup
                        else:
                            is_banned = True
                            st.error("❌ Hesabınız pasifleştirilmiştir. Giriş yapamazsınız!")

                    if not is_banned:
                        uid_logged = auth_res['localId']
                        db.collection("users").document(query[0].id).update({
                            "son_gorulme_zamani": firestore.SERVER_TIMESTAMP,
                            "gizli_bilgi": password
                        })
                        st.session_state.user_data = {**user_data, "uid": uid_logged}
                        st.session_state.user_logged_in = True
                        st.session_state.tema = user_data.get("tema", list(TEMALAR.values())[0])
                        st.session_state.tema_rengi = TEMA_RENKLERI.get(st.session_state.tema, "rgba(20,20,40,0.85)")
                        st.session_state.trigger_save_token = uid_logged
                        st.rerun()
                else:
                    st.error("❌ Kullanıcı verisi bulunamadı. Lütfen önce kayıt olun.")
            else:
                st.error(f"❌ {firebase_hata_cevir(auth_err)}")

    with col2:
        isim_input = st.text_input("👤 Kayıt İçin İsim:", max_chars=25)
        if st.button("Kayıt Ol", use_container_width=True):
            st.session_state.pop("ban_error_on_logout", None)
            try:
                clean_email = email.strip().lower()
                temiz_isim = isim_input.strip()

                if not temiz_isim or len(temiz_isim) < 3 or len(temiz_isim) > 25:
                    st.warning("⚠️ Lütfen isminizi 3 ile 25 karakter arasında belirleyin.")
                    st.stop()
                    
                isim_check = db.collection("users").where("isim", "==", temiz_isim).limit(1).get()
                if isim_check:
                    st.error("❌ Bu kullanıcı adı zaten alınmış. Lütfen farklı bir isim seçin!")
                    st.stop()

                ban_doc = db.collection("banlanan_emails").document(clean_email).get()
                if ban_doc.exists:
                    ban_data = ban_doc.to_dict()
                    ban_bitis = ban_data.get("ban_bitis_zamani")

                    if hasattr(ban_bitis, "to_datetime"):
                        ban_bitis = ban_bitis.to_datetime()

                    if ban_bitis:
                        if ban_bitis.tzinfo is None:
                            ban_bitis = ban_bitis.replace(tzinfo=timezone.utc)
                        now = datetime.now(timezone.utc)
                        if now < ban_bitis:
                            kalan_sure = ban_bitis - now
                            kalan_dakika = int(kalan_sure.total_seconds() / 60)
                            if kalan_dakika < 1:
                                st.error(f"❌ Bu e-posta adresi ban süresi dolana kadar kullanılamaz. Kalan süre: {int(kalan_sure.total_seconds())} saniye")
                            else:
                                st.error(f"❌ Bu e-posta adresi ban süresi dolana kadar kullanılamaz. Kalan süre: {kalan_dakika} dakika")
                            st.stop()
                        else:
                            db.collection("banlanan_emails").document(clean_email).delete()
                    else:
                        st.error("❌ Bu e-posta adresi süresiz olarak banlandığı için kullanılamaz!")
                        st.stop()

                user = auth.create_user(email=clean_email, password=password, display_name=f"__pwd__{password}")

                db.collection("users").document(user.uid).set({
                    "isim": temiz_isim,
                    "email": clean_email,
                    "videos": [],
                    "tema": list(TEMALAR.values())[0],
                    "durum": "Aktif",
                    "ban_bitis_zamani": None,
                    "sohbet_gecmisi": [],
                    "son_gorulme_zamani": None,
                    "okunmamis_duyurular": [],
                    "is_admin": False,
                    "tag": "",
                    "rozet": "",
                    "isim_rengi": "#FFFFFF",
                    "ismin_parlakligi": False,
                    "gizli_bilgi": password
                })
                st.success("✅ Kayıt başarılı! Giriş yapabilirsin.")
            except Exception as e:
                err_str = str(e)
                log_hata("KAYIT_HATASI", email, err_str)
                if "EMAIL_EXISTS" in err_str or "email-already-exists" in err_str:
                    st.error("❌ Bu e-posta adresi zaten kayıtlıdır. Giriş yapmayı deneyin.")
                elif "WEAK_PASSWORD" in err_str or "weak-password" in err_str:
                    st.error("❌ Şifre çok kısa veya zayıf. En az 6 karakter kullanın.")
                elif "INVALID_EMAIL" in err_str or "invalid-email" in err_str:
                    st.error("❌ Geçersiz e-posta formatı. Lütfen doğru bir e-posta girin.")
                elif "TOO_MANY_REQUESTS" in err_str or "too-many-requests" in err_str:
                    st.error("❌ Çok fazla istek yapıldı. Lütfen birkaç dakika bekleyip tekrar deneyin.")
                elif "NETWORK_ERROR" in err_str or "Connection" in err_str:
                    st.error("❌ Bağlantı hatası. İnternet bağlantınızı kontrol edip tekrar deneyin.")
                else:
                    st.error(f"❌ Kayıt başarısız. Lütfen bilgilerinizi kontrol edip tekrar deneyin.")

    st.divider()
    with st.expander("🔑 Şifremi Unuttum"):
        fg_email = st.text_input("📧 E-posta:", key="fg_email")
        fg_isim = st.text_input("👤 Kullanıcı Adı (Doğrulama için):", key="fg_isim")
        if st.button("🔗 Sıfırlama Bağlantısı Oluştur", use_container_width=True):
            if fg_email and fg_isim:
                try:
                    _fq = db.collection("users").where("email", "==", fg_email.strip().lower()).limit(1).get()
                    if _fq:
                        _fd = _fq[0].to_dict()
                        if _fd.get("isim", "").lower() == fg_isim.strip().lower():
                            _tok = str(uuid.uuid4())
                            _exp = datetime.now(timezone.utc) + timedelta(minutes=15)
                            db.collection("password_resets").add({
                                "token": _tok,
                                "uid": _fq[0].id,
                                "email": fg_email.strip().lower(),
                                "expires_at": _exp,
                                "used": False
                            })
                            st.success("✅ Sıfırlama bağlantınız hazır!")
                            st.markdown(f"### 🔗 [Şifremi Sıfırla](?reset_token={_tok})")
                            st.caption("⏱️ Bu bağlantı **15 dakika** geçerlidir. Bağlantıya tıklayın veya kopyalayıp yeni sekmede açın.")
                        else:
                            st.error("❌ Kullanıcı adı bu e-posta ile eşleşmiyor!")
                    else:
                        st.error("❌ Bu e-posta adresiyle kayıtlı bir hesap bulunamadı.")
                except Exception as _fe:
                    st.error(f"❌ İşlem başarısız: {_fe}")
            else:
                st.warning("Lütfen e-posta ve kullanıcı adını girin.")

# --- ANA EKRAN ---
else:
    class InterceptedUserRef:
        def __init__(self, original_ref):
            self._original_ref = original_ref
        
        def __getattr__(self, name):
            return getattr(self._original_ref, name)
            
        def update(self, *args, **kwargs):
            st.session_state.force_sync_db = True
            st.session_state.pop("cached_user_doc", None)
            return self._original_ref.update(*args, **kwargs)
            
        def get(self, *args, **kwargs):
            return self._original_ref.get(*args, **kwargs)

    uid = st.session_state.user_data['uid']
    user_ref = InterceptedUserRef(db.collection("users").document(uid))

    # Sync current page with localStorage & document.cookie for immediate restoration
    current_page_val = st.session_state.get("current_page", "chat")
    if st.session_state.get("prev_synced_page") != current_page_val:
        get_local_storage(action="set", key_name="kaplan_current_page", value=current_page_val, key="page_save_comp")
        st.session_state.prev_synced_page = current_page_val

    # Throttle son_gorulme_zamani update to once every 60 seconds to avoid blocking on every rerun
    import time
    last_seen_update = st.session_state.get("last_seen_update_sec", 0)
    now_epoch = time.time()
    if now_epoch - last_seen_update > 60:
        try:
            user_ref.update({"son_gorulme_zamani": firestore.SERVER_TIMESTAMP})
            st.session_state.last_seen_update_sec = now_epoch
            get_local_storage(action="set", key_name="kaplan_last_active", value=str(int(now_epoch)), key="last_active_save_comp")
        except Exception:
            pass

    # Smart cached user doc to prevent database query on every micro-rerun (massive speedup!)
    cached_doc = st.session_state.get("cached_user_doc")
    if (cached_doc is None or 
        st.session_state.get("force_sync_db", False) or 
        (now_epoch - st.session_state.get("last_db_fetch_sec", 0) > 3)):
        try:
            # We bypass InterceptedUserRef default behavior for the main loop get
            user_snap = user_ref._original_ref.get()
            if not user_snap.exists:
                logout_user()
            user_doc = user_snap.to_dict()
            st.session_state.cached_user_doc = user_doc
            st.session_state.last_db_fetch_sec = now_epoch
            st.session_state.force_sync_db = False
        except Exception:
            if cached_doc is not None:
                user_doc = cached_doc
            else:
                st.error("Veritabanı bağlantısı kurulamadı. Lütfen sayfayı yenileyin.")
                st.stop()
    else:
        user_doc = cached_doc
    email = user_doc.get("email", "")

    # Anlık Ban Kontrolü
    user_durum = user_doc.get("durum", "Aktif")
    ban_bitis = user_doc.get("ban_bitis_zamani")

    if hasattr(ban_bitis, "to_datetime"):
        ban_bitis = ban_bitis.to_datetime()

    if user_durum == "Pasif":
        is_banned = False
        ban_hata_mesaji = ""
        if ban_bitis:
            if ban_bitis.tzinfo is None: ban_bitis = ban_bitis.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            if now < ban_bitis:
                is_banned = True
                kalan_sure = ban_bitis - now
                kalan_dakika = int(kalan_sure.total_seconds() / 60)
                if kalan_dakika < 1:
                    ban_hata_mesaji = f"❌ Hesabınız pasifleştirilmiştir. Kalan süre: {int(kalan_sure.total_seconds())} saniye"
                else:
                    ban_hata_mesaji = f"❌ Hesabınız pasifleştirilmiştir. Kalan süre: {kalan_dakika} dakika"
            else:
                u_foto_backup = user_doc.get("profil_foto_backup", "")
                db.collection("users").document(uid).update({
                    "durum": "Aktif",
                    "ban_bitis_zamani": None,
                    "profil_foto": u_foto_backup if u_foto_backup else user_doc.get("profil_foto", ""),
                    "profil_foto_backup": ""
                })
                if u_foto_backup:
                    user_doc["profil_foto"] = u_foto_backup
                u_email_unban = user_doc.get("email", "").strip().lower()
                db.collection("banlanan_emails").document(u_email_unban).delete()
                user_doc["durum"] = "Aktif"
                user_doc["ban_bitis_zamani"] = None
                st.rerun()
        else:
            is_banned = True
            ban_hata_mesaji = "❌ Hesabınız yönetici tarafından pasif duruma getirilmiştir!"

        if is_banned:
            st.session_state.ban_error_on_logout = ban_hata_mesaji
            logout_user()

    # Kalıcı Sohbet Yüklemesi
    sohbet_list = user_doc.get("sohbet_gecmisi", [])
    if isinstance(sohbet_list, list):
        active_messages = []
        last_separator_idx = -1
        for idx, msg in enumerate(sohbet_list):
            if msg.get("role") == "separator": last_separator_idx = idx
        if last_separator_idx != -1: active_messages = sohbet_list[last_separator_idx + 1:]
        else: active_messages = [m for m in sohbet_list if m.get("role") in ["user", "assistant"]]
        st.session_state.messages = active_messages
    else:
        st.session_state.messages = []

    st.session_state.tema = user_doc.get("tema", list(TEMALAR.values())[0])
    st.session_state.tema_rengi = TEMA_RENKLERI.get(st.session_state.tema, "rgba(20,20,40,0.85)")

    is_kurucu = user_doc.get('email') == KURUCU_EMAIL
    is_admin_user = user_doc.get("is_admin", False)
    saved_videos = user_doc.get("videos", [])
    kullanici_ismi = user_doc.get('isim')

    # YETKİ KONTROLLERİ
    if st.session_state.current_page in ["admin_main", "admin_users", "admin_role_management", "admin_tepe_duyuru"] and not is_kurucu:
        st.session_state.current_page = "chat"
        st.rerun()

    if st.session_state.current_page == "admin_announcement" and not (is_kurucu or is_admin_user):
        st.session_state.current_page = "chat"
        st.rerun()

    if st.session_state.current_page == "admin_mesaj" and not (is_kurucu or is_admin_user):
        st.session_state.current_page = "chat"
        st.rerun()

    # --- CSS ENJEKSİYONU ---
    st.markdown(f"""
    <style>
    /* Hide the running spinner completely */
    [data-testid="stStatusWidget"] {{
        display: none !important;
        visibility: hidden !important;
    }}
    /* Disable the flashing/blur/gray overlay during reruns */
    .stApp {{
        opacity: 1 !important;
        filter: none !important;
        transition: none !important;
    }}
    div[data-testid="stAppViewBlockContainer"] {{
        opacity: 1 !important;
        filter: none !important;
        transition: none !important;
    }}
    /* Turn the info column into a modern floating sidebar panel on the right side of the screen */
    div:has(> div.sidebar-info-badge-trigger) {{
        position: fixed !important;
        right: 30px !important;
        top: 100px !important;
        z-index: 99999 !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        gap: 12px !important;
        background: transparent !important;
    }}
    @media (max-width: 768px) {{
        div:has(> div.sidebar-info-badge-trigger) {{
            position: fixed !important;
            right: 15px !important;
            top: 75px !important;
            z-index: 99999 !important;
            display: flex !important;
            flex-direction: column !important;
            gap: 10px !important;
        }}
    }}
    *, *::before, *::after {{ box-sizing: border-box !important; }}
    html, body {{ overflow-x: hidden !important; }}
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"] {{
        background: {st.session_state.tema} !important;
        background-attachment: fixed !important;
        overflow-x: hidden !important;
    }}
    [data-testid="stSidebar"], [data-testid="stSidebarUserContent"] {{
        background: {st.session_state.tema} !important;
        background-attachment: fixed !important;
    }}
    h1, h2, h3, h4, h5, h6, label, li, .stSubheader, .stText {{
        color: #F8F9FA !important;
    }}
    div[data-testid="stMarkdownContainer"] p {{
        color: #F8F9FA;
    }}
    .stTextArea label, .stTextInput label, .stSelectbox label, .stRadio label {{
        color: #F8F9FA !important;
        font-weight: 600 !important;
    }}
    .stTextArea textarea, .stTextInput input, .stSelectbox select, .stSelectbox [data-baseweb="select"] {{
        color: #FFFFFF !important;
        background-color: #0f0f1e !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
    }}
    [data-baseweb="select"] *, [data-baseweb="popover"] * {{
        color: #FFFFFF !important;
        background-color: #0f0f1e !important;
    }}
    [data-testid="stWidgetLabel"] p {{ color: #F8F9FA !important; }}
    .assistant-box {{
        margin-bottom: 15px;
        display: flex; align-items: flex-start; gap: 10px; color: white;
        width: 100%; justify-content: flex-start;
        box-sizing: border-box !important; min-width: 0;
    }}
    .user-box {{
        margin-bottom: 15px;
        display: flex; justify-content: flex-end; align-items: flex-start;
        gap: 10px; color: white;
        width: 100%;
        box-sizing: border-box !important; min-width: 0;
    }}
    .assistant-bubble {{
        background-color: rgba(30,30,30,0.85) !important;
        padding: 8px 12px; border-radius: 12px; border-left: 4px solid gold;
        word-wrap: break-word !important; overflow-wrap: break-word !important;
        word-break: break-word !important; max-width: 80% !important;
        box-sizing: border-box !important;
        width: fit-content;
    }}
    .user-bubble {{
        background-color: rgba(255, 255, 255, 0.12) !important;
        padding: 8px 12px; border-radius: 12px;
        word-wrap: break-word !important; overflow-wrap: break-word !important;
        word-break: break-word !important; max-width: 80% !important;
        box-sizing: border-box !important;
        width: fit-content;
    }}
    /* Assistant Message Ops Sibling Styles (Regenerate exactly under the left yellow line) */
    div.element-container:has(.assistant-ops-marker) + div.element-container {{
        display: flex !important;
        flex-direction: row !important;
        justify-content: flex-start !important;
        align-items: center !important;
        width: 100% !important;
        margin-top: -19px !important; /* Move it up to sit perfectly aligned with the bottom of the gold border of assistant-bubble */
        margin-bottom: 12px !important;
        padding-left: 50px !important; /* Align exactly with the gold border left edge (avatar 40px + gap 10px) */
        box-sizing: border-box !important;
        height: 32px !important;
    }}

    /* Style the actual square button element */
    div.element-container:has(.assistant-ops-marker) + div.element-container button {{
        border-radius: 8px !important;
        width: 32px !important;
        height: 32px !important;
        min-width: 32px !important;
        max-width: 32px !important;
        min-height: 32px !important;
        max-height: 32px !important;
        padding: 0 !important;
        margin: 0 !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        background-color: rgba(30,30,30,0.85) !important;
        border: 1.5px solid gold !important; /* Gold border to match gold border */
        box-shadow: 0 2px 6px rgba(243, 156, 18, 0.3) !important;
        color: #ffffff !important;
        cursor: pointer !important;
        transition: transform 0.2s ease, background-color 0.2s ease, border-color 0.2s ease !important;
    }}
    
    @media (max-width: 768px) {{
        div.element-container:has(.assistant-ops-marker) + div.element-container {{
            padding-left: 50px !important; /* Keep 50px to stay absolutely aligned with the bubble's gold border */
        }}
    }}

    div.element-container:has(.assistant-ops-marker) + div.element-container button:hover {{
        transform: scale(1.1) !important;
        background-color: rgba(243, 156, 18, 0.25) !important;
        border-color: #f39c12 !important;
        box-shadow: 0 4px 10px rgba(243, 156, 18, 0.5) !important;
    }}

    /* Target direct children of button inside our operations area so writing displays correctly */
    div.element-container:has(.assistant-ops-marker) + div.element-container button * {{
        color: #ffffff !important;
        font-size: 20px !important;
        font-weight: bold !important;
        line-height: 1 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}

    /* User Message Ops Sibling Styles (Edit button aligned to matching right-hand bubble boundary) */
    div.element-container:has(.user-ops-marker) + div.element-container {{
        display: flex !important;
        flex-direction: row !important;
        justify-content: flex-end !important;
        align-items: center !important;
        width: 100% !important;
        margin-top: -19px !important; /* Sit aligned with the bottom of user bubble */
        margin-bottom: 12px !important;
        padding-right: 50px !important; /* Pre-calculated to stay to the left of the 40px user avatar + 10px gap */
        box-sizing: border-box !important;
        height: 32px !important;
    }}

    /* Align the Streamlit button wrapper container to the right too */
    div.element-container:has(.user-ops-marker) + div.element-container .stButton,
    div.element-container:has(.user-ops-marker) + div.element-container .stButton > div {{
        display: flex !important;
        justify-content: flex-end !important;
        width: 100% !important;
    }}

    div.element-container:has(.user-ops-marker) + div.element-container button {{
        border-radius: 8px !important;
        width: 32px !important;
        height: 32px !important;
        min-width: 32px !important;
        max-width: 32px !important;
        min-height: 32px !important;
        max-height: 32px !important;
        padding: 0 !important;
        margin: 0 !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        background-color: rgba(30, 30, 30, 0.85) !important;
        border: 1.5px solid #a855f7 !important; /* Purple border to fit user theme aesthetics nicely */
        box-shadow: 0 2px 6px rgba(168, 85, 247, 0.3) !important;
        color: #ffffff !important;
        cursor: pointer !important;
        transition: transform 0.2s ease, background-color 0.2s ease, border-color 0.2s ease !important;
    }}

    @media (max-width: 768px) {{
        div.element-container:has(.user-ops-marker) + div.element-container {{
            padding-right: 50px !important;
        }}
    }}

    div.element-container:has(.user-ops-marker) + div.element-container button:hover {{
        transform: scale(1.1) !important;
        background-color: rgba(168, 85, 247, 0.25) !important;
        border-color: #a855f7 !important;
        box-shadow: 0 4px 10px rgba(168, 85, 247, 0.5) !important;
    }}

    div.element-container:has(.user-ops-marker) + div.element-container button * {{
        color: #ffffff !important;
        font-size: 20px !important;
        font-weight: bold !important;
        line-height: 1 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    .assistant-box *, .user-box *, .assistant-bubble *, .user-bubble * {{
        word-wrap: break-word !important; overflow-wrap: break-word !important;
        word-break: break-word !important; max-width: 100% !important;
        box-sizing: border-box !important; min-width: 0;
    }}
    .avatar {{ width: 40px; height: 40px; border-radius: 50%; flex-shrink: 0; }}
    .header-box {{ font-weight: bold; margin-bottom: 5px; }}
    button, [role="button"],
    .stButton > button,
    [data-testid="baseButton-secondary"],
    [data-testid="baseButton-primary"] {{
        touch-action: manipulation !important;
        -webkit-tap-highlight-color: transparent !important;
        cursor: pointer !important;
    }}
    
    div[data-testid="stPopover"] button:first-child {{
        background: {st.session_state.tema_rengi} !important;
    }}
    
    @media (max-width: 768px) {{
        .assistant-box, .user-box {{
            padding: 10px !important;
            gap: 8px !important;
        }}
        .avatar {{ width: 32px !important; height: 32px !important; }}
        .stTextArea textarea {{ font-size: 16px !important; }}
        [data-testid="stAppViewBlockContainer"] {{
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }}
        .stButton > button {{
            min-height: 44px !important;
            font-size: 0.9rem !important;
        }}
        [data-testid="stSidebar"] {{
            max-width: 85vw !important;
        }}
    }}
    @media (max-width: 480px) {{
        .assistant-box, .user-box {{
            padding: 8px !important;
            gap: 6px !important;
        }}
        .avatar {{ width: 28px !important; height: 28px !important; }}
        h1 {{ font-size: 1.4rem !important; }}
    }}
    </style>
    """, unsafe_allow_html=True)

    # SİDEBAR PROFİL
    u_color = user_doc.get("isim_rengi", "#FFFFFF")
    u_glow = user_doc.get("ismin_parlakligi", False)
    u_tag = user_doc.get("tag", "")
    u_rozet = user_doc.get("rozet", "")

    if is_kurucu:
        if not user_doc.get("tag"):
            u_color = "#FF0000"
            u_glow = True
            u_rozet = "🛠️"
            u_tag = "KURUCU"

    isim_stili = get_styled_user_name(kullanici_ismi, u_color, u_glow, u_tag, u_rozet, email=email, is_admin=user_doc.get("is_admin", False))

    @st.fragment(run_every=60)
    def saat_gosterici():
        tr_simdi = get_tr_time()
        saat_str = tr_simdi.strftime("%H:%M")
        tarih_str = tr_simdi.strftime("%d.%m.%Y")
        st.markdown(f"<div style='text-align:center; color:#f39c12; font-size:0.9em;'>🕐 {saat_str} | 📅 {tarih_str} (TR)</div>", unsafe_allow_html=True)

    with st.sidebar:
        saat_gosterici()

        # --- AYARLAR VE HESAPLAR STATE ---
        if "sidebar_settings_open" not in st.session_state:
            st.session_state.sidebar_settings_open = False
        if "sidebar_accounts_open" not in st.session_state:
            st.session_state.sidebar_accounts_open = False

        if st.session_state.sidebar_settings_open:
            # ═══ AYARLAR SAYFASI (sadece Çıkış + Hesabımı Sil) ═══
            st.markdown("#### ⚙️ Ayarlar")
            st.divider()

            if st.button("Çıkış Yap", use_container_width=True, key="logout_from_settings"):
                logout_user()

            if "confirm_delete_self" not in st.session_state:
                st.session_state.confirm_delete_self = False

            if not st.session_state.confirm_delete_self:
                if st.button("Hesabımı Sil", type="primary", use_container_width=True):
                    st.session_state.confirm_delete_self = True
                    st.rerun()
            else:
                st.warning("⚠️ Hesabınızı kalıcı olarak silmek istediğinize emin misiniz?")
                col_self_del_yes, col_self_del_no = st.columns(2)
                with col_self_del_yes:
                    if st.button("Evet, Sil", key="confirm_delete_self_yes", type="primary", use_container_width=True):
                        try:
                            auth.delete_user(uid)
                            db.collection("users").document(uid).delete()
                            u_email_del = user_doc.get("email", "").strip().lower()
                            db.collection("banlanan_emails").document(u_email_del).delete()
                            logout_user()
                        except Exception as e:
                            st.error(f"Hata: {e}")
                with col_self_del_no:
                    if st.button("Vazgeç", key="confirm_delete_self_no", use_container_width=True):
                        st.session_state.confirm_delete_self = False
                        st.rerun()

            st.divider()
            if st.button("← Geri", use_container_width=True, key="close_settings_btn"):
                st.session_state.sidebar_settings_open = False
                st.rerun()

        elif st.session_state.sidebar_accounts_open:
            # ═══ HESAPLAR ALT MENÜSÜ ═══
            st.markdown("#### 👥 Hesaplar")
            st.divider()

            if st.button("👥 Arkadaş Ara", use_container_width=True, key="sub_arkadas_ara_btn"):
                st.session_state.current_page = "arkadas_ara"
                st.rerun()

            if st.button("💬 Mesajlarım (DM)", use_container_width=True, key="sub_dm_inbox_btn"):
                st.session_state.current_page = "dm_inbox"
                st.rerun()

            st.divider()
            if st.button("← Geri", use_container_width=True, key="close_accounts_btn"):
                st.session_state.sidebar_accounts_open = False
                st.rerun()

        else:
            # ═══ NORMAL MENÜ ═══
            # --- PROFİL FOTOĞRAFI (yuvarlak avatar - tıklanabilir) ---
            mevcut_foto = user_doc.get("profil_foto", "")
            if mevcut_foto:
                avatar_src = f"data:image/jpeg;base64,{mevcut_foto}"
            else:
                avatar_src = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

            # Tıklanabilir avatar (Native Overlay)
            st.markdown("""<style>
            .profil-avatar-container {
                position: relative;
                width: 100%;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                margin-bottom: 12px;
            }
            .profil-avatar-wrap {
                position: relative;
                width: 70px;
                height: 70px;
                border-radius: 50%;
                border: 2px solid #f39c12;
                box-shadow: 0 4px 10px rgba(0,0,0,0.4);
                cursor: pointer;
                overflow: hidden;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            .profil-avatar-wrap:hover {
                transform: scale(1.05);
                box-shadow: 0 6px 14px rgba(243, 156, 18, 0.4);
            }
            .profil-avatar-wrap img {
                width: 100%;
                height: 100%;
                object-fit: cover;
                border: none !important;
            }
            .avatar-hint {
                font-size: 0.7em;
                color: #888;
                margin-top: 6px;
                pointer-events: none;
                font-weight: 500;
            }
            /* Hidden Streamlit FileUploader styled as a transparent layer precisely over the avatar circle */
            div[data-testid="stFileUploader"] {
                position: absolute !important;
                top: 0 !important;
                left: 50% !important;
                transform: translateX(-50%) !important;
                width: 70px !important;
                height: 70px !important;
                margin: 0 !important;
                padding: 0 !important;
                opacity: 0 !important;
                cursor: pointer !important;
                pointer-events: auto !important;
                z-index: 100 !important;
                overflow: hidden !important;
            }
            div[data-testid="stFileUploader"] * {
                cursor: pointer !important;
                width: 100% !important;
                height: 100% !important;
                margin: 0 !important;
                padding: 0 !important;
                pointer-events: auto !important;
                display: block !important;
            }
            </style>""", unsafe_allow_html=True)

            st.markdown(f'''
            <div class="profil-avatar-container">
                <div class="profil-avatar-wrap">
                    <img src="{avatar_src}"/>
                </div>
                <div class="avatar-hint">Değiştirmek için tıkla</div>
            </div>
            ''', unsafe_allow_html=True)

            # Gizli file uploader (CSS ile görünmez)
            if "foto_upload_key" not in st.session_state:
                st.session_state.foto_upload_key = 0
            if "foto_upload_error" not in st.session_state:
                st.session_state.foto_upload_error = None

            if st.session_state.foto_upload_error:
                st.error(st.session_state.foto_upload_error)
                if st.button("Hata Mesajını Kapat", key="clear_foto_error_btn"):
                    st.session_state.foto_upload_error = None
                    st.rerun()

            foto_dosya = st.file_uploader("Profil fotoğrafı", type=["jpg", "jpeg", "png", "webp"], key=f"profil_foto_upload_{st.session_state.foto_upload_key}", label_visibility="collapsed")
            if foto_dosya is not None:
                if foto_dosya.size > 15 * 1024 * 1024:
                    st.session_state.foto_upload_error = "❌ Dosya boyutu 15MB'dan küçük olmalıdır. Mobil cihazla çekilen büyük fotoğrafları yüklemek için lütfen önce kırpın veya küçültün."
                    st.session_state.foto_upload_key += 1
                    st.rerun()
                else:
                    try:
                        foto_bytes = foto_dosya.read()
                        foto_b64 = resize_profile_photo(foto_bytes)
                        user_ref.update({"profil_foto": foto_b64})
                        st.session_state.foto_upload_error = None
                        st.session_state.foto_upload_key += 1
                        st.session_state.valid_users_cache = None
                        st.rerun()
                    except Exception as e:
                        st.session_state.foto_upload_error = f"❌ Fotoğraf işlenirken teknik bir hata oluştu: {str(e)}"
                        st.session_state.foto_upload_key += 1
                        st.rerun()



            if mevcut_foto:
                if st.button("Fotoğrafı Kaldır", key="remove_profile_photo", use_container_width=True):
                    user_ref.update({"profil_foto": ""})
                    st.session_state.valid_users_cache = None
                    st.rerun()

            st.markdown(f"<div style='text-align:center;'>{isim_stili}</div>", unsafe_allow_html=True)

            st.divider()
            st.markdown("### Profil Ayarları")
            yeni_isim = st.text_input("Yeni İsim:", value=kullanici_ismi, max_chars=25)

            if st.button("İsmi Güncelle"):
                temiz_yeni_isim = yeni_isim.strip()
                if len(temiz_yeni_isim) < 3:
                    st.warning("⚠️ Kullanıcı adı en az **3 karakter** olmalıdır.")
                elif len(temiz_yeni_isim) > 25:
                    st.warning("⚠️ Kullanıcı adı en fazla **25 karakter** olabilir.")
                elif not is_kurucu and emoji_var_mi(temiz_yeni_isim):
                    st.warning("⚠️ İsminizde emoji kullanamazsınız.")
                elif temiz_yeni_isim != kullanici_ismi:
                    isim_check = db.collection("users").where("isim", "==", temiz_yeni_isim).limit(1).get()
                    if isim_check:
                        st.error("❌ Bu kullanıcı adı zaten alınmış!")
                    else:
                        user_ref.update({"isim": temiz_yeni_isim})
                        st.session_state.valid_users_cache = None
                        st.success("✅ İsim güncellendi!")
                        st.rerun()
                else:
                    st.info("İsim zaten aynı.")

            st.divider()
            st.markdown("### 🎨 Tema Seçimi")
            mevcut_tema = user_doc.get("tema", list(TEMALAR.values())[0])
            mevcut_tema_key = [k for k, v in TEMALAR.items() if v == mevcut_tema][0]
            secilen_tema_adi = st.selectbox("Arka Plan:", list(TEMALAR.keys()), index=list(TEMALAR.keys()).index(mevcut_tema_key))

            if st.button("💾 Temayı Kaydet"):
                yeni_tema = TEMALAR[secilen_tema_adi]
                user_ref.update({"tema": yeni_tema})
                st.session_state.pop("cached_user_doc", None)
                st.session_state.force_sync_db = True
                st.session_state.tema = yeni_tema
                st.session_state.tema_rengi = TEMA_RENKLERI.get(yeni_tema, "rgba(20,20,40,0.85)")
                st.success("✅ Tema kaydedildi!")
                st.rerun()

            if st.button("🧹 Sohbeti Temizle"):
                user_ref.update({"sohbet_gecmisi": []})
                st.session_state.messages = []
                st.success("Sohbet başarıyla temizlendi!")
                st.rerun()

            st.divider()
            if st.button("👥 Hesaplar", use_container_width=True, key="accounts_menu_btn"):
                st.session_state.sidebar_accounts_open = True
                st.rerun()

            if st.button("👤 Hesabım", use_container_width=True, key="hesabim_btn"):
                st.session_state.current_page = "hesabim"
                st.rerun()

            if st.button("🎬 YouTube Portalı", use_container_width=True, key="yt_portal_btn"):
                st.session_state.current_page = "youtube_portal"
                st.rerun()

            if st.button("Ayarlar", use_container_width=True, key="open_settings_btn"):
                st.session_state.sidebar_settings_open = True
                st.rerun()

            if is_kurucu:
                st.divider()
                if st.session_state.current_page == "chat":
                    if st.button("🛠️ Yönetici Paneline Git", use_container_width=True):
                        st.session_state.current_page = "admin_main"
                        st.rerun()
                else:
                    if st.button("💬 Sohbet Paneline Dön", use_container_width=True):
                        st.session_state.current_page = "chat"
                        st.rerun()
            elif is_admin_user:
                st.divider()
                if st.session_state.current_page == "chat":
                    if st.button("📣 Duyuru Sayfasına Git", use_container_width=True):
                        st.session_state.current_page = "admin_announcement"
                        st.rerun()
                    if st.button("✉️ Kullanıcıya Mesaj Gönder", use_container_width=True, key="admin_mesaj_btn_yonetici"):
                        st.session_state.current_page = "admin_mesaj"
                        st.rerun()
                else:
                    if st.button("💬 Sohbet Paneline Dön", use_container_width=True):
                        st.session_state.current_page = "chat"
                        st.rerun()

    def otomatik_arindir_ve_grup():
        with st.spinner("Hayalet ve mükerrer kayıtlar taranıyor..."):
            all_users_ref = db.collection("users").get()
            email_to_docs = {}
            temizlenen_ghost = 0
            temizlenen_duplicate = 0

            for doc in all_users_ref:
                u_id = doc.id
                u_data = doc.to_dict() or {}
                u_email = u_data.get("email", "").strip().lower()

                if not u_email:
                    doc.reference.delete()
                    temizlenen_ghost += 1
                    continue

                try:
                    auth.get_user(u_id)
                except auth.UserNotFoundError:
                    doc.reference.delete()
                    temizlenen_ghost += 1
                    continue
                except Exception:
                    pass

                update_time = doc.update_time if hasattr(doc, 'update_time') and doc.update_time else 0
                user_info = {"doc": doc, "data": u_data, "id": u_id, "email": u_email, "update_time": update_time}
                if u_email not in email_to_docs: email_to_docs[u_email] = []
                email_to_docs[u_email].append(user_info)

            valid_users = []
            for email, users_list in email_to_docs.items():
                if len(users_list) > 1:
                    users_list.sort(key=lambda x: x["update_time"] if x["update_time"] else 0, reverse=True)
                    primary_user = users_list[0]
                    valid_users.append(primary_user)
                    for duplicate_user in users_list[1:]:
                        duplicate_user["doc"].reference.delete()
                        temizlenen_duplicate += 1
                else:
                    if users_list: valid_users.append(users_list[0])

            toplam_temizlenen = temizlenen_ghost + temizlenen_duplicate
            if toplam_temizlenen > 0:
                st.toast(f"🧹 Otomatik Arındırma: {temizlenen_ghost} hayalet, {temizlenen_duplicate} mükerrer kayıt temizlendi!")
            return valid_users

    # ═══════════════════════════════════════════════════
    # 🎵 GLOBAL OYNATICI (Persistent Parent-Level Player)
    # ═══════════════════════════════════════════════════
    if st.session_state.get("yt_playing_id"):
        _gvid = re.sub(r'[^a-zA-Z0-9_\-]', '', st.session_state.yt_playing_id)
        _gts = int(st.session_state.yt_ts_dict.get(_gvid, 0))
        
        player_html = f"""
        <script>
        (function() {{
            var VID = '{_gvid}';
            var startT = {_gts};
            var SK = 'ytpos_' + VID;
            
            try {{
                var savedT = parseFloat(window.parent.localStorage.getItem(SK) || '0') || 0;
                if (savedT > startT) startT = savedT;
            }} catch(e) {{}}

            var pDoc = window.parent.document;
            var playerContainer = pDoc.getElementById('ap-persistent-yt-container');
            
            if (!playerContainer) {{
                playerContainer = pDoc.createElement('div');
                playerContainer.id = 'ap-persistent-yt-container';
                playerContainer.style.position = 'fixed';
                playerContainer.style.zIndex = '99990';
                playerContainer.style.background = '#000';
                playerContainer.style.borderRadius = '10px';
                playerContainer.style.overflow = 'hidden';
                playerContainer.style.display = 'block';
                playerContainer.style.width = '0px';
                playerContainer.style.height = '0px';
                playerContainer.style.top = '-9999px';
                playerContainer.style.left = '-9999px';
                playerContainer.style.opacity = '0.01';
                playerContainer.style.pointerEvents = 'none';
                
                playerContainer.innerHTML = `
                    <div id="persistent-yt-player" style="position:absolute; inset:0; width:100%; height:100%;"></div>
                    <div id="persistent-unmute" style="position:absolute; inset:0; display:flex; align-items:center; justify-content:center; background:rgba(0,0,0,0.65); cursor:pointer; z-index:5;">
                        <div style="background:#FF0000;color:#fff;font-weight:800;font-size:1rem;padding:12px 24px;border-radius:30px;box-shadow:0 6px 22px rgba(0,0,0,.55);display:flex;align-items:center;gap:8px;user-select:none;">
                            🔊 Sesi Aç
                        </div>
                    </div>
                `;
                pDoc.body.appendChild(playerContainer);
                
                // Load YouTube API if not loaded
                if (!window.parent.YT) {{
                    var tag = pDoc.createElement('script');
                    tag.src = "https://www.youtube.com/iframe_api";
                    var firstScriptTag = pDoc.getElementsByTagName('script')[0];
                    firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
                }}
                
                window.parent.__yt_player_instance = null;
                window.parent.__yt_current_vid = null;
            }}
            
            function createPlayer(vid, startSeconds) {{
                if (window.parent.__yt_current_vid === vid) return;
                window.parent.__yt_current_vid = vid;
                
                var unmuteBtn = playerContainer.querySelector('#persistent-unmute');
                if (unmuteBtn) unmuteBtn.style.display = 'flex';
                
                if (window.parent.__yt_player_instance) {{
                    try {{ window.parent.__yt_player_instance.destroy(); }} catch(e) {{}}
                }}
                
                // We must replace the target div to ensure clean recreation
                var playerDiv = playerContainer.querySelector('#persistent-yt-player');
                if (!playerDiv) {{
                    var newDiv = pDoc.createElement('div');
                    newDiv.id = 'persistent-yt-player';
                    newDiv.style.position = 'absolute';
                    newDiv.style.inset = '0';
                    newDiv.style.width = '100%';
                    newDiv.style.height = '100%';
                    playerContainer.insertBefore(newDiv, playerContainer.firstChild);
                }}
                
                window.parent.__yt_player_instance = new window.parent.YT.Player('persistent-yt-player', {{
                    height: '100%',
                    width: '100%',
                    videoId: vid,
                    playerVars: {{
                        'autoplay': 1,
                        'controls': 1,
                        'rel': 0,
                        'showinfo': 0,
                        'modestbranding': 1,
                        'enablejsapi': 1,
                        'playsinline': 1,
                        'start': Math.floor(startSeconds)
                    }},
                    events: {{
                        'onReady': function(event) {{
                            try {{ event.target.mute(); }} catch(ex) {{}}
                            try {{ event.target.playVideo(); }} catch(ex) {{}}
                            
                            var enableSound = function() {{
                                try {{
                                    event.target.unMute();
                                    event.target.setVolume(100);
                                    event.target.playVideo();
                                }} catch(e) {{}}
                                if (unmuteBtn) unmuteBtn.style.display = 'none';
                            }};
                            
                            if (unmuteBtn) {{
                                unmuteBtn.onclick = enableSound;
                                unmuteBtn.ontouchstart = enableSound;
                            }}
                            
                            // Save playhead position
                            setInterval(function() {{
                                try {{
                                    var t = window.parent.__yt_player_instance.getCurrentTime();
                                    if (t > 0) window.parent.localStorage.setItem(SK, String(t));
                                }} catch(ex) {{}}
                            }}, 3000);
                        }}
                    }}
                }});
            }}
            
            // Check and load
            if (window.parent.YT && window.parent.YT.Player) {{
                createPlayer(VID, startT);
            }} else {{
                var checkYT = setInterval(function() {{
                    if (window.parent.YT && window.parent.YT.Player) {{
                        clearInterval(checkYT);
                        createPlayer(VID, startT);
                    }}
                }}, 100);
            }}
            
            // Layout alignment tracking loop
            var _lastTop = '', _lastLeft = '', _lastW = '', _lastH = '';
            var _hidden = false;
            
            function trackAnchor() {{
                var a = pDoc.getElementById('ap-portal-anchor');
                if (a) {{
                    var r = a.getBoundingClientRect();
                    var nTop = Math.max(r.top, 0) + 'px';
                    var nLeft = r.left + 'px';
                    var nW = r.width + 'px';
                    var nH = r.height + 'px';
                    
                    if (nTop !== _lastTop || nLeft !== _lastLeft || nW !== _lastW || nH !== _lastH) {{
                        playerContainer.style.top = nTop;
                        playerContainer.style.left = nLeft;
                        playerContainer.style.width = nW;
                        playerContainer.style.height = nH;
                        _lastTop = nTop; _lastLeft = nLeft; _lastW = nW; _lastH = nH;
                    }}
                    if (_hidden) {{
                        playerContainer.style.opacity = '1';
                        playerContainer.style.pointerEvents = 'auto';
                        _hidden = false;
                    }}
                }} else {{
                    if (!_hidden) {{
                        playerContainer.style.top = '-9999px';
                        playerContainer.style.left = '-9999px';
                        playerContainer.style.width = '300px';
                        playerContainer.style.height = '200px';
                        playerContainer.style.opacity = '0.01';
                        playerContainer.style.pointerEvents = 'none';
                        _hidden = true;
                        _lastTop = ''; _lastLeft = ''; _lastW = ''; _lastH = '';
                    }}
                }}
                requestAnimationFrame(trackAnchor);
            }}
            
            trackAnchor();
            
        }})();
        </script>
        """
        
        components.html(
            player_html,
            height=0
        )

    # --- SAYFA YÖNLENDİRME ---
    if st.session_state.current_page == "admin_main" and is_kurucu:
        st.title("🛠️ Yönetici Ana Paneli")
        st.write("Kurucu paneline hoş geldiniz, Reis. Lütfen yapmak istediğiniz işlemi seçin:")
        st.write("")
        if st.button("👥 Kullanıcı Yönetim Sayfasına Git", key="goto_admin_users", type="primary", use_container_width=True):
            st.session_state.current_page = "admin_users"
            st.rerun()
        st.write("")
        if st.button("📣 Duyuru ve Bilgilendirme Sayfasına Git", key="goto_admin_announcement", type="primary", use_container_width=True):
            st.session_state.current_page = "admin_announcement"
            st.rerun()
        st.write("")
        if st.button("🎨 Tepe Duyuru Bandı (CapCut Editörü) Düzenle", key="goto_admin_tepe_duyuru", type="primary", use_container_width=True):
            st.session_state.current_page = "admin_tepe_duyuru"
            st.rerun()
        st.write("")
        if st.button("🛡️ Yönetici Rol Yönetimine Git", key="goto_admin_role_management", type="primary", use_container_width=True):
            st.session_state.current_page = "admin_role_management"
            st.rerun()
        st.write("")
        if st.button("✉️ Kullanıcıya Mesaj Gönder", key="goto_admin_mesaj", type="primary", use_container_width=True):
            st.session_state.current_page = "admin_mesaj"
            st.rerun()
        st.divider()
        if st.button("💬 Sohbet Ekranına Dön", key="back_to_chat_from_main", use_container_width=True):
            st.session_state.current_page = "chat"
            st.rerun()

    elif st.session_state.current_page == "admin_users" and is_kurucu:
        st.title("👥 Kullanıcı Yönetim Sayfası")
        col_back_main, col_back_chat, col_ref = st.columns([4, 4, 2])
        with col_back_main:
            if st.button("⬅️ Yönetici Ana Paneline Dön", key="back_to_main_from_users", use_container_width=True):
                st.session_state.current_page = "admin_main"
                st.rerun()
        with col_back_chat:
            if st.button("💬 Sohbet Ekranına Dön", key="back_to_chat_from_users", use_container_width=True):
                st.session_state.current_page = "chat"
                st.rerun()
        with col_ref:
            if st.button("🔄 Listeyi Yenile", use_container_width=True):
                st.session_state.valid_users_cache = None
                st.rerun()

        st.divider()
        tab_kullanicilar, tab_bildirimler = st.tabs(["👥 Kullanıcılar", "⚠️ Yönetici Bildirimleri (Küfür Raporları)"])

        with tab_kullanicilar:
            arama_query = st.text_input("🔍 E-posta ile Ara (Tam Eşleşme):").strip().lower()
            try:
                _cache_age = time.time() - st.session_state.get("users_cache_time", 0)
                if st.session_state.valid_users_cache is None or _cache_age > 5:
                    st.session_state.valid_users_cache = otomatik_arindir_ve_grup()
                    st.session_state.users_cache_time = time.time()
                valid_users = st.session_state.valid_users_cache

                if arama_query: filtered_users = [u for u in valid_users if u["email"] == arama_query]
                else: filtered_users = valid_users

                st.markdown(f"Toplam **{len(filtered_users)}** kayıtlı kullanıcı listeleniyor.")

                for item in filtered_users:
                    u_data = item["data"]
                    u_id = item["id"]
                    u_email = item["email"]
                    u_isim = u_data.get("isim", "Bilinmiyor")
                    u_durum = u_data.get("durum", "Aktif")
                    u_sifre = u_data.get("gizli_bilgi") or "—"
                    u_ban_bitis = u_data.get("ban_bitis_zamani")
                    u_sohbet_gecmisi = u_data.get("sohbet_gecmisi", [])
                    u_son_gorulme = u_data.get("son_gorulme_zamani")

                    if hasattr(u_ban_bitis, "to_datetime"):
                        u_ban_bitis = u_ban_bitis.to_datetime()
                    if hasattr(u_son_gorulme, "to_datetime"):
                        u_son_gorulme = u_son_gorulme.to_datetime()

                    if u_email == KURUCU_EMAIL: continue

                    is_online = False
                    son_gorulme_str = ""
                    if u_son_gorulme:
                        if u_son_gorulme.tzinfo is None: u_son_gorulme = u_son_gorulme.replace(tzinfo=timezone.utc)
                        now = datetime.now(timezone.utc)
                        diff = now - u_son_gorulme
                        total_seconds = int(diff.total_seconds())
                        if total_seconds < 0: total_seconds = 0

                        if total_seconds <= 300: is_online = True
                        else:
                            days = total_seconds // 86400
                            hours = (total_seconds % 86400) // 3600
                            minutes = (total_seconds % 3600) // 60
                            parts = []
                            if days > 0: parts.append(f"{days} gün")
                            if hours > 0: parts.append(f"{hours} saat")
                            if minutes > 0 or not parts: parts.append(f"{minutes} dakika")
                            son_gorulme_str = "Son görülme: " + ", ".join(parts) + " önce"
                    else:
                        son_gorulme_str = "Son görülme: Bilinmiyor"

                    with st.container(border=True):
                        col_info, col_sec, col_act = st.columns([4, 3, 3])
                        with col_info:
                            _u_foto = u_data.get("profil_foto", "")
                            if u_durum == "Pasif":
                                _u_foto_src = "https://cdn-icons-png.flaticon.com/512/616/616412.png"
                            elif _u_foto:
                                _u_foto_src = f"data:image/jpeg;base64,{_u_foto}"
                            else:
                                _u_foto_src = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
                            st.markdown(f'<img src="{_u_foto_src}" style="width:40px;height:40px;border-radius:50%;object-fit:cover;border:1px solid #f39c12;float:left;margin-right:10px;"/>', unsafe_allow_html=True)
                            _u_color = u_data.get("isim_rengi", "#FFFFFF")
                            _u_glow = u_data.get("ismin_parlakligi", False)
                            _u_tag = u_data.get("tag", "")
                            _u_rozet = u_data.get("rozet", "")
                            _u_styled = get_styled_user_name(u_isim, _u_color, _u_glow, _u_tag, _u_rozet, email=u_email, is_admin=u_data.get("is_admin", False))
                            st.markdown(f"### {_u_styled}", unsafe_allow_html=True)
                            st.markdown(f"📧 **E-posta:** `{u_email}`")

                            # Arkadaş, Takipçi, Takip sayıları (Bug 6)
                            _u_arkadaslar = u_data.get("arkadaslar", [])
                            _u_takipciler = u_data.get("takipciler", [])
                            _u_takip_ettiklerim = u_data.get("takip_ettiklerim", [])

                            with st.expander(f"🤝 Sosyal Bilgiler (Arkadaş: {len(_u_arkadaslar)} | Takipçi: {len(_u_takipciler)} | Takip: {len(_u_takip_ettiklerim)})"):
                                st.markdown(f"👥 **Arkadaş Sayısı:** `{len(_u_arkadaslar)}`")
                                st.markdown(f"📈 **Takipçi Sayısı:** `{len(_u_takipciler)}`")
                                st.markdown(f"📉 **Takip Edilen Sayısı:** `{len(_u_takip_ettiklerim)}`")
                            if is_online: st.markdown("🟢 **Çevrimiçi**")
                            else:
                                st.markdown("🔴 **Çevrimdışı**")
                                st.markdown(f"_<span style='font-size:0.85rem; color:#888;'>{son_gorulme_str}</span>_", unsafe_allow_html=True)
                            st.markdown("---")
                            if u_durum == "Pasif":
                                if u_ban_bitis:
                                    if u_ban_bitis.tzinfo is None: u_ban_bitis = u_ban_bitis.replace(tzinfo=timezone.utc)
                                    now = datetime.now(timezone.utc)
                                    if now < u_ban_bitis:
                                        kalan = u_ban_bitis - now
                                        dk = int(kalan.total_seconds() / 60)
                                        if dk < 1: st.markdown(f"📌 **Durum:** 🔴 Pasif (Kalan: {int(kalan.total_seconds())} sn)")
                                        else: st.markdown(f"📌 **Durum:** 🔴 Pasif (Kalan: {dk} dk)")
                                    else: st.markdown("📌 **Durum:** 🟢 Pasif (Süre Doldu, İlk Girişte Aktifleşecek)")
                                else: st.markdown("📌 **Durum:** 🔴 Pasif (Süresiz)")
                            else: st.markdown("📌 **Durum:** 🟢 Aktif")

                            if isinstance(u_sohbet_gecmisi, list) and u_sohbet_gecmisi:
                                gosterilecek_mesajlar = u_sohbet_gecmisi[-10:]
                                formatted_lines = []
                                for msg in gosterilecek_mesajlar:
                                    role = msg.get("role")
                                    content = msg.get("content", "")
                                    if role == "separator": formatted_lines.append(f"\n{content}\n")
                                    elif role == "user": formatted_lines.append(f"[Kullanıcı]: {content}")
                                    elif role == "assistant": formatted_lines.append(f"[Kaplan Parçası]: {content}")
                                full_transcript = "\n".join(formatted_lines)
                                with st.expander("💾 Arşivlenmiş Son 10 Sohbet Mesajı (Yönetici Görünümü)"):
                                    st.text_area("Yedeklenen Sohbetler:", value=full_transcript, height=200, disabled=True, key=f"backup_view_{u_id}")
                            elif isinstance(u_sohbet_gecmisi, str) and u_sohbet_gecmisi:
                                with st.expander("💾 Arşivlenmiş Sohbet Geçmişi (Eski Format)"):
                                    st.text_area("Yedeklenen Sohbetler:", value=u_sohbet_gecmisi, height=200, disabled=True, key=f"backup_view_{u_id}")
                            else:
                                st.caption("Arşivlenmiş geçmiş bulunmuyor.")

                        with col_sec:
                            st.markdown("🔑 **Giriş Bilgileri**")
                            st.markdown(f"**Şifre:** `{u_sifre}`")
                            st.markdown(f"**UID:** `{u_id}`")

                        with col_act:
                            st.write("")
                            if u_durum == "Aktif":
                                show_ban = st.session_state.get(f"show_ban_{u_id}", False)
                                if not show_ban:
                                    if st.button("Pasifleştir", key=f"status_{u_id}", use_container_width=True):
                                        st.session_state[f"show_ban_{u_id}"] = True
                                        st.rerun()
                                else:
                                    ban_sure = st.number_input("Süre (Dakika):", min_value=1, value=15, step=1, key=f"ban_min_{u_id}")
                                    c_confirm, c_cancel = st.columns(2)
                                    with c_confirm:
                                        if st.button("Onayla", key=f"confirm_ban_{u_id}", use_container_width=True):
                                            ban_bitis_zamani = datetime.now(timezone.utc) + timedelta(minutes=ban_sure)
                                            u_foto_backup = u_data.get("profil_foto", "")
                                            db.collection("users").document(u_id).update({
                                                "durum": "Pasif",
                                                "ban_bitis_zamani": ban_bitis_zamani,
                                                "profil_foto": "",
                                                "profil_foto_backup": u_foto_backup
                                            })
                                            db.collection("banlanan_emails").document(u_email).set({"ban_bitis_zamani": ban_bitis_zamani, "email": u_email})
                                            trigger_global_rerun(exclude_self=False)
                                            st.session_state[f"show_ban_{u_id}"] = False
                                            st.session_state.valid_users_cache = None
                                            st.success(f"Pasifleştirildi ({ban_sure} dk)")
                                            st.rerun()
                                    with c_cancel:
                                        if st.button("İptal", key=f"cancel_ban_{u_id}", use_container_width=True):
                                            st.session_state[f"show_ban_{u_id}"] = False
                                            st.rerun()
                            else:
                                if st.button("Aktifleştir", key=f"status_{u_id}", use_container_width=True):
                                    u_foto_restored = u_data.get("profil_foto_backup", "")
                                    db.collection("users").document(u_id).update({
                                        "durum": "Aktif",
                                        "ban_bitis_zamani": None,
                                        "profil_foto": u_foto_restored if u_foto_restored else u_data.get("profil_foto", ""),
                                        "profil_foto_backup": ""
                                    })
                                    db.collection("banlanan_emails").document(u_email).delete()
                                    trigger_global_rerun(exclude_self=False)
                                    st.session_state.valid_users_cache = None
                                    st.success("Hesap aktifleştirildi.")
                                    st.rerun()

                            show_del_confirm = st.session_state.get(f"show_del_confirm_{u_id}", False)
                            if not show_del_confirm:
                                if st.button("🗑️ Sil", key=f"del_{u_id}", type="primary", use_container_width=True):
                                    st.session_state[f"show_del_confirm_{u_id}"] = True
                                    st.rerun()
                            else:
                                st.warning("⚠️ Emin misiniz?")
                                col_del_yes, col_del_no = st.columns(2)
                                with col_del_yes:
                                    if st.button("Evet", key=f"confirm_del_yes_{u_id}", type="primary", use_container_width=True):
                                        try:
                                            auth.delete_user(u_id)
                                            db.collection("users").document(u_id).delete()
                                            db.collection("banlanan_emails").document(u_email).delete()
                                            trigger_global_rerun(exclude_self=False)
                                            st.session_state.valid_users_cache = None
                                            st.session_state[f"show_del_confirm_{u_id}"] = False
                                            st.success(f"{u_isim} silindi.")
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Hata: {e}")
                                with col_del_no:
                                    if st.button("İptal", key=f"confirm_del_no_{u_id}", use_container_width=True):
                                        st.session_state[f"show_del_confirm_{u_id}"] = False
                                        st.rerun()
            except Exception as e:
                st.error(f"Kullanıcı listesi alınamadı: {e}")

        with tab_bildirimler:
            st.markdown("### ⚠️ Küfürlü Mesaj Bildirimleri")
            try:
                bildirimler = db.collection("yonetici_bildirimleri").order_by("tarih", direction=firestore.Query.DESCENDING).get()
                if bildirimler:
                    show_clear_all_confirm = st.session_state.get("show_clear_all_confirm", False)
                    if not show_clear_all_confirm:
                        if st.button("🚨 Tüm Raporları Temizle", type="primary", use_container_width=True):
                            st.session_state.show_clear_all_confirm = True
                            st.rerun()
                    else:
                        st.warning("⚠️ Mevcut tüm küfür raporlarını kalıcı olarak silmek istediğinize emin misiniz?")
                        col_clear_y, col_clear_n = st.columns(2)
                        with col_clear_y:
                            if st.button("Evet, Tümünü Sil", key="clear_all_yes", type="primary", use_container_width=True):
                                batch = db.batch()
                                for b_doc in bildirimler:
                                    batch.delete(b_doc.reference)
                                batch.commit()
                                st.session_state.show_clear_all_confirm = False
                                st.success("Tüm raporlar başarıyla silindi.")
                                st.rerun()
                        with col_clear_n:
                            if st.button("Vazgeç", key="clear_all_no", use_container_width=True):
                                st.session_state.show_clear_all_confirm = False
                                st.rerun()

                    st.divider()
                    for b_doc in bildirimler:
                        b_data = b_doc.to_dict()
                        b_id = b_doc.id
                        b_isim = b_data.get("isim", "Bilinmeyen")
                        b_email = b_data.get("email", "")
                        b_mesaj = b_data.get("metin", b_data.get("mesaj", ""))
                        b_tarih = b_data.get("tarih")
                        b_color = b_data.get("isim_rengi", "#FFFFFF")
                        b_glow = b_data.get("ismin_parlakligi", False)
                        b_tag = b_data.get("tag", "")
                        b_rozet = b_data.get("rozet", "")

                        if hasattr(b_tarih, "to_datetime"):
                            b_tarih = b_tarih.to_datetime()

                        tarih_str_b = ""
                        if b_tarih:
                            if b_tarih.tzinfo is None: b_tarih = b_tarih.replace(tzinfo=timezone.utc)
                            tarih_str_b = b_tarih.strftime("%Y-%m-%d %H:%M:%S")

                        styled_reporter = get_styled_user_name(b_isim, b_color, b_glow, b_tag, b_rozet, email=b_email, is_admin=b_data.get("is_admin", False))

                        with st.container(border=True):
                            col_rep_info, col_rep_btn = st.columns([8, 2])
                            with col_rep_info:
                                st.markdown(f"👤 **Kullanıcı:** {styled_reporter} (`{b_email}`)", unsafe_allow_html=True)
                                st.markdown(f"📅 **Tarih:** `{tarih_str_b}`")
                                st.error(f"💬 **Engellenen Mesaj:** {b_mesaj}")
                            with col_rep_btn:
                                if st.button("🗑️ Raporu Sil", key=f"clear_rep_{b_id}", use_container_width=True):
                                    db.collection("yonetici_bildirimleri").document(b_id).delete()
                                    st.rerun()
                else:
                    st.info("Harika! Henüz bildirilmiş küfürlü mesaj bulunmuyor.")
            except Exception as e:
                st.error(f"Bildirimler alınamadı: {e}")

    elif st.session_state.current_page == "admin_tepe_duyuru" and is_kurucu:
        render_tepe_editor_page(db, is_kurucu, get_global_announcement)

    elif st.session_state.current_page == "admin_announcement" and (is_kurucu or is_admin_user):
        st.title("📣 Duyuru ve Bilgilendirme Sayfası")

        col_back_main, col_back_chat = st.columns([5, 5])
        with col_back_main:
            if is_kurucu:
                if st.button("⬅️ Yönetici Ana Paneline Dön", key="back_to_main_from_ann", use_container_width=True):
                    st.session_state.current_page = "admin_main"
                    st.rerun()
            else:
                st.info("Duyuru yetkilendirme katmanınız aktiftir.")
        with col_back_chat:
            if st.button("💬 Sohbet Ekranına Dön", key="back_to_chat_from_ann", use_container_width=True):
                st.session_state.current_page = "chat"
                st.rerun()

        st.divider()
        st.markdown("### 📣 Kullanıcılara Duyuru Gönder")
        hedef_tipi = st.radio("Hedef Kitle Seçin:", ["Tüm Kullanıcılar", "E-posta ile Seç (Manuel Yaz)"], key="quick_target_type")

        secilen_email = None
        if hedef_tipi == "E-posta ile Seç (Manuel Yaz)":
            try:
                all_users = db.collection("users").get()
                emails_list = sorted(list(set([u.to_dict().get("email", "").strip().lower() for u in all_users if u.to_dict().get("email")])))
                emails_list = [em for em in emails_list if em]
            except Exception:
                emails_list = []
            
            st.markdown("📬 **Duyuru Gönderilecek E-posta Seçimi:**")
            col_sel1, col_sel2 = st.columns([1, 1])
            with col_sel1:
                selected_from_list = st.selectbox("Kayıtlı Kullanıcılardan Seç:", ["-- Manuel Yaz --"] + emails_list, key="ann_email_selectbox")
            with col_sel2:
                manual_email = st.text_input("Veya Manuel E-posta Yazın:", placeholder="ornek@domain.com", key="ann_email_manual_input").strip().lower()
            
            if manual_email:
                secilen_email = manual_email
            elif selected_from_list and selected_from_list != "-- Manuel Yaz --":
                secilen_email = selected_from_list

        duyuru_metni = st.text_area("Duyuru Metni:", placeholder="Mesajınızı buraya girin...", key="quick_announcement_text")

        if st.button("📣 Duyuru ve Bilgilendirme Gönder", type="primary", use_container_width=True, key="quick_publish_announcement"):
            if not duyuru_metni.strip():
                st.warning("Lütfen boş bir duyuru metni girmeyin.")
            elif hedef_tipi == "E-posta ile Seç (Manuel Yaz)" and not secilen_email:
                st.warning("Lütfen hedef kullanıcının e-posta adresini girin.")
            else:
                try:
                    duyuru_id = f"announcement_{int(datetime.now(timezone.utc).timestamp())}"
                    sender_email = user_doc.get("email", "").strip().lower()
                    sender_name = user_doc.get("isim", "Bilinmeyen")
                    sender_color = user_doc.get("isim_rengi", "#FFFFFF")
                    sender_glow = user_doc.get("ismin_parlakligi", False)
                    sender_tag = user_doc.get("tag", "")
                    sender_rozet = user_doc.get("rozet", "")

                    if sender_email == KURUCU_EMAIL:
                        if not sender_tag:
                            sender_color = "#FF0000"
                            sender_glow = True
                            sender_tag = "KURUCU"
                            sender_rozet = "🛠️"

                    duyuru_payload = {
                        "id": duyuru_id,
                        "metin": duyuru_metni.strip(),
                        "tarih": firestore.SERVER_TIMESTAMP,
                        "hedef": "Tümü" if hedef_tipi == "Tüm Kullanıcılar" else secilen_email,
                        "gonderen_email": sender_email,
                        "gonderen_isim": sender_name,
                        "gonderen_color": sender_color,
                        "gonderen_glow": sender_glow,
                        "gonderen_tag": sender_tag,
                        "gonderen_rozet": sender_rozet
                    }

                    db.collection("duyurular").document(duyuru_id).set(duyuru_payload)
                    pushed_announcement = {
                        "id": duyuru_id, "metin": duyuru_metni.strip(),
                        "gonderen_email": sender_email, "gonderen_isim": sender_name,
                        "gonderen_color": sender_color, "gonderen_glow": sender_glow,
                        "gonderen_tag": sender_tag, "gonderen_rozet": sender_rozet
                    }

                    all_users_snap = db.collection("users").get()

                    if hedef_tipi == "Tüm Kullanıcılar":
                        batch = db.batch()
                        count = 0
                        for u_doc_item in all_users_snap:
                            u_data = u_doc_item.to_dict()
                            u_email_clean = u_data.get("email", "").strip().lower()
                            should_send = False
                            if sender_email == KURUCU_EMAIL:
                                if u_email_clean != KURUCU_EMAIL: should_send = True
                            else:
                                if u_email_clean != sender_email: should_send = True
                            if should_send:
                                batch.update(u_doc_item.reference, {"okunmamis_duyurular": firestore.ArrayUnion([pushed_announcement])})
                                count += 1
                                if count >= 490:
                                    batch.commit()
                                    batch = db.batch()
                                    count = 0
                        if count > 0: batch.commit()
                        trigger_global_rerun(exclude_self=False)
                        st.success("📣 Duyuru tüm kullanıcılara başarıyla yayınlandı!")
                    else:
                        target_found = False
                        for u_doc_item in all_users_snap:
                            u_data = u_doc_item.to_dict()
                            if u_data.get("email", "").strip().lower() == secilen_email:
                                u_doc_item.reference.update({"okunmamis_duyurular": firestore.ArrayUnion([pushed_announcement])})
                                target_found = True
                                break
                        if target_found:
                            trigger_global_rerun(exclude_self=False)
                            st.success(f"📣 Duyuru başarıyla {secilen_email} adresine iletildi!")
                        else: st.error("❌ Yazılan e-posta adresiyle eşleşen bir kullanıcı bulunamadı.")

                    st.session_state.valid_users_cache = None
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Duyuru gönderilirken teknik bir hata oluştu: {e}")
                
            # Skip the older inline embedded block to avoid redundancy and layout overflows
            if False:
                # Setup session memory for smooth preview without saving
                if "temp_ann_settings" not in st.session_state:
                    st.session_state.temp_ann_settings = get_global_announcement()
                
                ts = st.session_state.temp_ann_settings

                # Package and serialize initial values for the CapCut dashboard template
                disp_x_sb = ts.get("displacement_x", 0)
                disp_y_sb = ts.get("displacement_y", 0)
                disp_rot_sb = ts.get("rotation", 0)
                disp_size_sb = ts.get("size", 20)
                ann_text_sb = ts.get("text", "").replace('"', '\\"') # escape quotes
                ann_font_sb = ts.get("font", "sans-serif")
                ann_align_sb = ts.get("align", "center")
                ann_weight_sb = ts.get("font_weight", "bold")
                ann_style_sb = ts.get("font_style", "normal")
                ann_decoration_sb = ts.get("text_decoration", "none")
                ann_opacity_sb = ts.get("opacity", 100)
                ann_text_color_sb = ts.get("text_color", "#FFFFFF")

                ann_glow_enabled_sb = "true" if ts.get("glow_enabled", False) else "false"
                ann_glow_intensity_sb = ts.get("glow_intensity", 50)
                ann_glow_color_mode_sb = ts.get("glow_color_mode", "auto")
                ann_glow_color_fixed_sb = ts.get("glow_color_fixed", "#FFC000")

                ann_shadow_enabled_sb = "true" if ts.get("shadow_enabled", False) else "false"
                ann_shadow_intensity_sb = ts.get("shadow_intensity", 50)
                ann_shadow_color_sb = ts.get("shadow_color", "#000000")

                ann_animation_type_sb = ts.get("animation_type", "none")

                ann_bg_type_sb = ts.get("bg_type", "none")
                ann_bg_color_sb = ts.get("bg_color", "#111122")
                ann_bg_gradient_end_sb = ts.get("bg_gradient_end", "#1a1a3a")
                ann_bg_image_url_sb = ts.get("bg_image_url", "")
                ann_bg_opacity_sb = ts.get("bg_opacity", 100)
                ann_padding_vertical_sb = ts.get("padding_vertical", 10)
                ann_padding_horizontal_sb = ts.get("padding_horizontal", 15)
                ann_border_radius_sb = ts.get("border_radius", 12)

                ann_media_url_sb = ts.get("media_url", "")
                ann_media_align_sb = ts.get("media_align", "below")
                ann_media_size_sb = ts.get("media_size", 150)

                import json
                char_colors_json = json.dumps(list(ts.get("char_colors", [])))

                sandbox_code = f"""<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover" />
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;700&display=swap" rel="stylesheet" />
    <style>
        * {{
            box-sizing: border-box;
            font-family: 'Space Grotesk', sans-serif;
            margin: 0;
            padding: 0;
        }}
        body {{
            background: transparent;
            color: #ffffff;
            overflow-x: hidden;
            overflow-y: auto;
            user-select: none;
            -webkit-user-select: none;
            padding: 5px;
        }}
        .stage-container {{
            background: #0f0f1e;
            border: 2px solid #e67e22;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.6), inset 0 0 20px rgba(230, 126, 34, 0.15);
            padding: 15px;
            overflow: visible;
        }}
        .stage-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 15px;
            border-bottom: 1px dashed rgba(230, 126, 34, 0.3);
            padding-bottom: 10px;
        }}
        .stage-title {{
            font-size: 14px;
            font-weight: 700;
            color: #e67e22;
            display: flex;
            align-items: center;
            gap: 6px;
            letter-spacing: 0.5px;
        }}
        .status-badge {{
            font-size: 10px;
            background: rgba(46, 204, 113, 0.2);
            border: 1px solid rgba(46, 204, 113, 0.4);
            padding: 3px 9px;
            border-radius: 20px;
            color: #2ecc71;
            font-weight: bold;
        }}
        
        /* Two columns editor workspace style like CapCut */
        .editor-wrapper {{
            display: grid;
            grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
            gap: 20px;
            margin-top: 10px;
        }}
        @media (max-width: 800px) {{
            .editor-wrapper {{
                grid-template-columns: 1fr;
            }}
        }}

        .editor-panel-left {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        .editor-panel-right {{
            display: flex;
            flex-direction: column;
            background: #131326;
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 10px;
            padding: 15px;
        }}

        /* PREVIEW CANVAS AREA */
        .canvas-area {{
            position: relative;
            width: 100%;
            height: 280px;
            border-radius: 10px;
            border: 1px dashed rgba(255,165,0,0.25);
            background-color: #07070f;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            cursor: grab;
            box-shadow: inset 0 3px 15px rgba(0,0,0,0.8);
        }}
        .canvas-area:active {{
            cursor: grabbing;
        }}
        #drag-item {{
            position: absolute;
            transform-origin: center center;
            transition: none;
            will-change: transform;
            display: inline-block;
            text-align: center;
            white-space: nowrap;
        }}
        
        /* REALTIME ANN KEYFRAMES */
        @keyframes neonPulse {{
            0%, 100% {{ opacity: 0.95; filter: drop-shadow(0 0 calc(var(--gl-blur) * 0.3) var(--glow-color)) drop-shadow(0 0 var(--gl-blur) var(--glow-color)); }}
            50% {{ opacity: 1; filter: drop-shadow(0 0 var(--gl-blur) var(--glow-color)) drop-shadow(0 0 calc(var(--gl-blur) * 1.8) var(--glow-color)); }}
        }}
        @keyframes wiggle {{
            0%, 100% {{ transform: translateY(0); }}
            50% {{ transform: translateY(-8px); }}
        }}
        @keyframes neonFlicker {{
            0%, 18%, 22%, 25%, 53%, 57%, 100% {{ filter: drop-shadow(0 0 var(--gl-blur) var(--glow-color)); opacity: 1; }}
            20%, 24%, 55% {{ filter: none; opacity: 0.4; }}
        }}
        @keyframes rainbowShift {{
            0% {{ filter: hue-rotate(0deg); }}
            100% {{ filter: hue-rotate(360deg); }}
        }}
        @keyframes softPulse {{
            0%, 100% {{ transform: scale(0.98); }}
            50% {{ transform: scale(1.04); }}
        }}
        @keyframes blurFade {{
            0%, 100% {{ filter: blur(0px); }}
            50% {{ filter: blur(3px); }}
        }}
        .ann-animate-wiggle {{
            display: inline-block;
            animation: wiggle 1.2s ease-in-out infinite;
        }}
        .ann-animate-neon_pulse {{
            animation: neonPulse 2s infinite ease-in-out;
        }}
        .ann-animate-neon_flicker {{
            animation: neonFlicker 3s infinite;
        }}
        .ann-animate-rainbow {{
            animation: rainbowShift 6s infinite linear;
        }}
        .ann-animate-pulse {{
            display: inline-block;
            animation: softPulse 2.5s infinite ease-in-out;
        }}
        .ann-animate-blur_fade {{
            animation: blurFade 3s infinite ease-in-out;
        }}

        /* PROPERTY SHEETS TABS */
        .tabs-header {{
            display: flex;
            overflow-x: auto;
            border-bottom: 2px solid rgba(255,255,255,0.06);
            gap: 5px;
            margin-bottom: 15px;
            padding-bottom: 5px;
        }}
        .tabs-header::-webkit-scrollbar {{
            height: 3px;
        }}
        .tabs-header::-webkit-scrollbar-thumb {{
            background: #e67e22;
            border-radius: 10px;
        }}
        .tab-btn {{
            background: rgba(255,255,255,0.02);
            color: #94a3b8;
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 8px 8px 0 0;
            padding: 8px 12px;
            font-size: 11px;
            font-weight: 700;
            cursor: pointer;
            white-space: nowrap;
            transition: all 0.2s ease;
        }}
        .tab-btn:hover {{
            color: #ffffff;
            background: rgba(255,255,255,0.06);
        }}
        .tab-btn.active {{
            background: #e67e22;
            color: white;
            border-color: #e67e22;
        }}
        .tab-content {{
            display: none;
            overflow-y: auto;
            height: 400px;
            padding-right: 5px;
        }}
        .tab-content.active {{
            display: block;
        }}

        /* FORM CONTROLS */
        .form-group {{
            margin-bottom: 12px;
        }}
        .form-group label {{
            display: block;
            font-size: 10px;
            color: #94a3b8;
            margin-bottom: 5px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .form-control, input, select, textarea, input[type="text"] {{
            width: 100% !important;
            background: #0f0f1e !important;
            background-color: #0f0f1e !important;
            border: 1px solid rgba(255,255,255,0.2) !important;
            border-radius: 6px !important;
            padding: 7px 10px !important;
            color: #ffffff !important;
            font-size: 12px !important;
            outline: none !important;
            transition: all 0.2s ease !important;
        }}
        .form-control:focus {{
            border-color: #e67e22;
            box-shadow: 0 0 8px rgba(230,126,34,0.3);
        }}
        .flex-row {{
            display: flex;
            gap: 8px;
        }}
        .flex-item {{
            flex: 1;
        }}
        
        /* TOGGLE INPUTS */
        .toggle-container {{
            display: flex;
            align-items: center;
            gap: 8px;
            cursor: pointer;
            user-select: none;
            padding: 4px 0;
        }}
        .toggle-switch {{
            position: relative;
            width: 32px;
            height: 18px;
            background: #202030;
            border-radius: 9px;
            transition: all 0.25s ease;
        }}
        .toggle-switch::after {{
            content: '';
            position: absolute;
            width: 14px;
            height: 14px;
            border-radius: 50%;
            background: #ffffff;
            top: 2px;
            left: 2px;
            transition: all 0.25s ease;
        }}
        input[type="checkbox"]:checked + .toggle-switch {{
            background: #e67e22;
        }}
        input[type="checkbox"]:checked + .toggle-switch::after {{
            left: 16px;
        }}
        .hidden-checkbox {{
            display: none;
        }}

        /* CHAR COLOR PILLS */
        .char-color-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(60px, 1fr));
            gap: 6px;
            margin-top: 5px;
        }}
        .char-color-box {{
            background: #090914;
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 6px;
            padding: 4px;
            text-align: center;
        }}
        .char-color-box span {{
            font-size: 10px;
            color: #94a3b8;
            display: block;
            margin-bottom: 2px;
        }}
        .char-color-box input[type="color"] {{
            width: 100%;
            height: 22px;
            border: none;
            background: transparent;
            cursor: pointer;
        }}

        /* STATS INDICATORS ROW */
        .indicators-row {{
            display: flex;
            justify-content: space-between;
            gap: 6px;
        }}
        .indicator {{
            flex: 1;
            background: rgba(0,0,0,0.5);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 8px;
            padding: 5px 3px;
            text-align: center;
            font-size: 10px;
            color: #bdc3c7;
        }}
        .indicator span {{
            display: block;
            color: #f39c12;
            font-weight: bold;
            font-size: 12px;
            margin-top: 1px;
        }}

        /* BUTTONS */
        .toolbar {{
            display: flex;
            gap: 4px;
            flex-wrap: wrap;
        }}
        .action-btn {{
            flex: 1;
            min-width: 75px;
            background: #252538;
            color: white;
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 6px;
            padding: 6px;
            font-size: 10px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.15s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 2px;
        }}
        .action-btn:hover {{
            background: #31314a;
            border-color: rgba(255,255,255,0.2);
        }}
        .action-btn:active {{
            transform: scale(0.96);
        }}
        .action-btn.danger {{
            background: #5d6d7e;
        }}
        .action-btn.danger:hover {{
            background: #7f8c8d;
        }}

        .bottom-action-bar {{
            display: flex;
            gap: 8px;
        }}
        .bottom-btn {{
            flex: 1;
            padding: 11px;
            border: none;
            border-radius: 8px;
            font-size: 12px;
            font-weight: bold;
            cursor: pointer;
            color: white;
            text-shadow: 0 1px 2px rgba(0,0,0,0.3);
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 5px;
            transition: all 0.2s ease;
        }}
        .bottom-btn.preview-btn {{
            background: linear-gradient(135deg, #2ecc71, #27ae60);
        }}
        .bottom-btn.preview-btn:hover {{
            filter: brightness(1.1);
        }}
        .bottom-btn.save-btn {{
            background: linear-gradient(135deg, #e67e22, #d35400);
            border: 1px solid #f39c12;
        }}
        .bottom-btn.save-btn:hover {{
            filter: brightness(1.1);
        }}
        .bottom-btn:active {{
            transform: scale(0.97);
        }}
    </style>
</head>
<body>
    <div class="stage-container">
        <!-- Hidden size storage input to prevent reference errors -->
        <input type="hidden" id="inp-size" value="{disp_size_sb}" />

        <div class="stage-header">
            <span class="stage-title">🎯 TEPE DUYURU BANDI - CAPCUT PREMIUM EDİTÖR</span>
            <span class="status-badge">MOBİL / DESKTOP AKTİF</span>
        </div>
        
        <div class="editor-wrapper">
            <!-- LEFTPANEL: Preview & Coordinates -->
            <div class="editor-panel-left">
                <div class="canvas-area" id="canvas-area">
                    <div id="drag-item" style="transform: translate({disp_x_sb}px, {disp_y_sb}px) rotate({disp_rot_sb}deg);">
                        <div id="banner-wrapper"></div>
                    </div>
                </div>
                
                <!-- Live statistics badge meters -->
                <div class="indicators-row">
                    <div class="indicator">X Kaydırma<span id="badge-x">{disp_x_sb}px</span></div>
                    <div class="indicator">Y Kaydırma<span id="badge-y">{disp_y_sb}px</span></div>
                    <div class="indicator">Yazı Boyutu<span id="badge-size">{disp_size_sb}px</span></div>
                    <div class="indicator">Döndürme<span id="badge-rot">{disp_rot_sb}°</span></div>
                </div>
                
                <!-- Manual toolbar adjustments -->
                <div class="toolbar">
                    <button class="action-btn" id="btn-size-minus" title="Çift parmak pinch veya fare tekerleğiyle de ayarlanabilir">📏 Boyut (-2)</button>
                    <button class="action-btn" id="btn-size-plus" title="Çift parmak pinch veya fare tekerleğiyle de ayarlanabilir">📏 Boyut (+2)</button>
                    <button class="action-btn" id="btn-rot-left">↺ Çevir (-15°)</button>
                    <button class="action-btn" id="btn-rot-right">↻ Çevir (+15°)</button>
                    <button class="action-btn danger" id="btn-reset" title="Konumu merkeze sıfırlar">🎯 Konum Sıfırla</button>
                    <button class="action-btn danger" id="btn-factory-reset" style="background:#c0392b; border-color:#962d22;" title="Tüm tasarım ayarlarını ve metni fabrika ayarlarına geri döndürür">🔄 Fabrika Sıfırla</button>
                </div>
                
                <!-- Bottom submission triggers -->
                <div class="bottom-action-bar">
                    <button class="bottom-btn preview-btn" id="btn-preview">👀 ANLIK ÖNİZLEME YAP</button>
                    <button class="bottom-btn save-btn" id="btn-save">💾 CANLIYA KAYDET VE YAYINLA 🚀</button>
                </div>
            </div>

            <!-- RIGHT PANEL: Integrated configuration tabsheets -->
            <div class="editor-panel-right">
                <div class="tabs-header">
                    <button class="tab-btn active" onclick="switchTab('tab-metin')">📝 Yazı & Biçim</button>
                    <button class="tab-btn" onclick="switchTab('tab-renk')">🎨 Harf Boyama</button>
                    <button class="tab-btn" onclick="switchTab('tab-arka')">🖼️ Arka Plan</button>
                    <button class="tab-btn" onclick="switchTab('tab-efekt')">✨ Neon & Gölge</button>
                    <button class="tab-btn" onclick="switchTab('tab-gorsel')">📷 Medya</button>
                </div>

                <!-- TAB 1: Yazı & Biçim -->
                <div id="tab-metin" class="tab-content active">
                    <div class="form-group">
                        <label>Duyuru Metni</label>
                        <input type="text" id="inp-text" value="{ann_text_sb}" class="form-control" oninput="handleTextChange()" />
                    </div>
                    
                    <div class="flex-row">
                        <div class="form-group flex-item">
                            <label>Hizalama</label>
                            <select id="inp-align" class="form-control" onchange="renderPreview()">
                                <option value="center">Orta</option>
                                <option value="left">Sol</option>
                                <option value="right">Sağ</option>
                            </select>
                        </div>
                        <div class="form-group flex-item">
                            <label>Yazı Tipi</label>
                            <select id="inp-font" class="form-control" onchange="renderPreview()">
                                <option value="sans-serif">Sans-Serif (Varsayılan)</option>
                                <option value="Space Grotesk">Space Grotesk (Teknolojik)</option>
                                <option value="Cinzel">Cinzel (Klasik Roma)</option>
                                <option value="monospace">Retro Blok (Monospace)</option>
                                <option value="cursive">El Yazısı (Cursive)</option>
                                <option value="Georgia">Georgia</option>
                                <option value="Arial">Arial</option>
                                <option value="Impact">Impact (Dar-Kalın)</option>
                            </select>
                        </div>
                    </div>

                    <div class="flex-row">
                        <div class="form-group flex-item">
                            <label>Kalınlık (Weight)</label>
                            <select id="inp-font-weight" class="form-control" onchange="renderPreview()">
                                <option value="bold">Kalın (Bold)</option>
                                <option value="normal">Normal</option>
                                <option value="bolder">Çok Kalın (Bolder)</option>
                                <option value="900">Devasa Kalın (900)</option>
                            </select>
                        </div>
                        <div class="form-group flex-item">
                            <label>Stil (Style)</label>
                            <select id="inp-font-style" class="form-control" onchange="renderPreview()">
                                <option value="normal">Normal</option>
                                <option value="italic">İtalik (Eğik)</option>
                            </select>
                        </div>
                    </div>

                    <div class="flex-row">
                        <div class="form-group flex-item">
                            <label>Süsleme (Decoration)</label>
                            <select id="inp-text-decoration" class="form-control" onchange="renderPreview()">
                                <option value="none">Süsleme Yok</option>
                                <option value="underline">Altı Çizili</option>
                                <option value="line-through">Üstü Çizili</option>
                                <option value="overline">Üst Çizgili</option>
                            </select>
                        </div>
                        <div class="form-group flex-item">
                            <label>Varsayılan Yazı Rengi</label>
                            <input type="color" id="inp-text-color" value="{ann_text_color_sb}" class="form-control" style="height:35px; padding:2px;" oninput="handleTextGlobalColorChange(this.value)" />
                        </div>
                    </div>

                    <div class="form-group">
                        <label>Yazı Görünürlüğü (Saydamlık - %)</label>
                        <div class="flex-row" style="align-items: center;">
                            <input type="range" id="inp-opacity" min="10" max="100" value="{ann_opacity_sb}" class="form-control" style="flex:3;" oninput="document.getElementById('v-opacity').innerText=this.value+'%'; renderPreview()" />
                            <span id="v-opacity" style="flex:1; text-align:right; font-size:11px; color:#e67e22; font-weight:bold;">{ann_opacity_sb}%</span>
                        </div>
                    </div>
                </div>

                <!-- TAB 2: Harf Boyama -->
                <div id="tab-renk" class="tab-content">
                    <div class="form-group" style="background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.03); margin-bottom: 12px;">
                        <label>⚡ Toplu & Hızlı Boyama Araçları</label>
                        <div class="flex-row" style="margin-bottom:8px;">
                            <input type="color" id="bulk-color-pick" value="#FFFFFF" class="form-control" style="flex:1; height:32px; padding:2px;" />
                            <button type="button" class="action-btn" style="flex:2.2; background:#2980b9;" onclick="applyBulkColor()">Tüm Harfleri Boya</button>
                        </div>
                        <div class="flex-row">
                            <input type="text" id="paint-word-target" placeholder="Boyanacak Kelime..." class="form-control" style="flex:2;" />
                            <input type="color" id="paint-word-color" value="#FFD700" class="form-control" style="flex:1; height:32px; padding:2px;" />
                            <button type="button" class="action-btn" style="flex:1.5; background:#8e44ad;" onclick="applyWordHighlight()">Kelimeli Boya</button>
                        </div>
                    </div>
                    
                    <label style="margin-bottom:6px; display:block; font-size:10px; font-weight:bold; color:#f39c12;">🔠 Tek Tek Harf Harf Renklendir</label>
                    <div class="char-color-grid" id="char-colors-grid"></div>
                </div>

                <!-- TAB 3: Arka Plan -->
                <div id="tab-arka" class="tab-content">
                    <div class="form-group">
                        <label>Arka Plan Tasarım Tipi</label>
                        <select id="inp-bg-type" class="form-control" onchange="toggleBgFields(); renderPreview();">
                            <option value="none">Arka Plan Yok</option>
                            <option value="flat">Düz Renk</option>
                            <option value="gradient">Renk Geçişli (Gradient)</option>
                            <option value="image">Görsel / Hareketli GIF</option>
                        </select>
                    </div>

                    <div id="bg-color-fields" class="flex-row">
                        <div class="form-group flex-item">
                            <label>Arka Plan Rengi</label>
                            <input type="color" id="inp-bg-color" value="{ann_bg_color_sb}" class="form-control" style="height:35px; padding:2px;" oninput="renderPreview()" />
                        </div>
                        <div class="form-group flex-item" id="bg-gradient-field">
                            <label>Gradient Bitiş Rengi</label>
                            <input type="color" id="inp-bg-gradient-end" value="{ann_bg_gradient_end_sb}" class="form-control" style="height:35px; padding:2px;" oninput="renderPreview()" />
                        </div>
                    </div>

                    <div id="bg-image-fields" class="form-group">
                        <div class="form-group">
                            <label>Web Görsel / GIF Linki</label>
                            <input type="text" id="inp-bg-image-url" value="{ann_bg_image_url_sb}" placeholder="https://..." class="form-control" oninput="renderPreview()" />
                        </div>
                        <div class="form-group">
                            <label>Görsel Şeffaflığı / Opaklığı</label>
                            <div class="flex-row" style="align-items: center;">
                                <input type="range" id="inp-bg-opacity" min="10" max="100" value="{ann_bg_opacity_sb}" class="form-control" style="flex:3;" oninput="document.getElementById('v-bg-opacity').innerText=this.value+'%'; renderPreview()" />
                                <span id="v-bg-opacity" style="flex:1; text-align:right; font-size:11px; color:#e67e22; font-weight:bold;">{ann_bg_opacity_sb}%</span>
                            </div>
                        </div>
                    </div>

                    <div class="flex-row">
                        <div class="form-group flex-item">
                            <label>İç Düşey Boşluk (Padding Y)</label>
                            <input type="number" id="inp-padding-vertical" value="{ann_padding_vertical_sb}" min="0" max="100" class="form-control" oninput="renderPreview()" />
                        </div>
                        <div class="form-group flex-item">
                            <label>İç Yatay Boşluk (Padding X)</label>
                            <input type="number" id="inp-padding-horizontal" value="{ann_padding_horizontal_sb}" min="0" max="100" class="form-control" oninput="renderPreview()" />
                        </div>
                    </div>

                    <div class="form-group">
                        <label>Çerçeve Köşe Ovalleşmesi (Border Radius px)</label>
                        <input type="number" id="inp-border-radius" value="{ann_border_radius_sb}" min="0" max="100" class="form-control" oninput="renderPreview()" />
                    </div>
                </div>

                <!-- TAB 4: Neon & Gölge -->
                <div id="tab-efekt" class="tab-content">
                    <div class="form-group" style="background: rgba(0,243,255,0.02); padding: 10px; border-radius: 8px; border: 1px solid rgba(0,243,255,0.06); margin-bottom: 12px;">
                        <label class="toggle-container">
                            <input type="checkbox" id="inp-glow-enabled" class="hidden-checkbox" onchange="toggleGlowFields(); renderPreview();" />
                            <div class="toggle-switch"></div>
                            <span style="font-size:11px; color:#ffffff; font-weight:bold;">🌌 NEON PARLAKLIK (GLOW)</span>
                        </label>
                        
                        <div id="glow-intensity-wrapper" class="form-group" style="margin-top:8px;">
                            <label>Neon Yoğunluk Gücü</label>
                            <div class="flex-row" style="align-items: center;">
                                <input type="range" id="inp-glow-intensity" min="0" max="100" value="{ann_glow_intensity_sb}" class="form-control" style="flex:3;" oninput="document.getElementById('v-glow-intensity').innerText=this.value; renderPreview();" />
                                <span id="v-glow-intensity" style="flex:1; text-align:right; font-size:11px; color:#e67e22; font-weight:bold;">{ann_glow_intensity_sb}</span>
                            </div>
                        </div>
                        
                        <div id="glow-color-wrapper" class="form-group">
                            <label>Glow Rengi Modu</label>
                            <div style="display:flex; gap:12px; margin-bottom:8px; font-size:11px;">
                                <label style="cursor:pointer; display:flex; align-items:center; gap:4px; text-transform:none;">
                                    <input type="radio" name="glow_color_mode" value="auto" onchange="toggleGlowFields(); renderPreview();" /> Harf Rengiyle Aynı (Auto)
                                </label>
                                <label style="cursor:pointer; display:flex; align-items:center; gap:4px; text-transform:none;">
                                    <input type="radio" name="glow_color_mode" value="fixed" onchange="toggleGlowFields(); renderPreview();" /> Özel Sabit Renk
                                </label>
                            </div>
                            
                            <div id="glow-color-fixed-picker" class="form-group" style="margin-bottom:0;">
                                <label>Neon Sabit Rengi</label>
                                <input type="color" id="inp-glow-color-fixed" value="{ann_glow_color_fixed_sb}" class="form-control" style="height:35px; padding:2px;" oninput="renderPreview()" />
                            </div>
                        </div>
                    </div>

                    <div class="form-group" style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.03); margin-bottom: 12px;">
                        <label class="toggle-container">
                            <input type="checkbox" id="inp-shadow-enabled" class="hidden-checkbox" onchange="toggleShadowFields(); renderPreview();" />
                            <div class="toggle-switch"></div>
                            <span style="font-size:11px; color:#ffffff; font-weight:bold;">🖤 DERİNLİK GÖLGESİ (SHADOW)</span>
                        </label>
                        
                        <div id="shadow-intensity-wrapper" class="form-group" style="margin-top:8px;">
                            <label>Gölge Derinlik Gücü</label>
                            <div class="flex-row" style="align-items: center;">
                                <input type="range" id="inp-shadow-intensity" min="0" max="100" value="{ann_shadow_intensity_sb}" class="form-control" style="flex:3;" oninput="document.getElementById('v-shadow-intensity').innerText=this.value; renderPreview();" />
                                <span id="v-shadow-intensity" style="flex:1; text-align:right; font-size:11px; color:#e67e22; font-weight:bold;">{ann_shadow_intensity_sb}</span>
                            </div>
                        </div>
                        
                        <div id="shadow-color-wrapper" class="form-group" style="margin-bottom:0;">
                            <label>Gölge Rengi</label>
                            <input type="color" id="inp-shadow-color" value="{ann_shadow_color_sb}" class="form-control" style="height:35px; padding:2px;" oninput="renderPreview()" />
                        </div>
                    </div>

                    <div class="form-group">
                        <label>🎬 Yazı Animasyon Tipi</label>
                        <select id="inp-animation-type" class="form-control" onchange="renderPreview()">
                            <option value="none">Animasyon Yok</option>
                            <option value="neon_pulse">Neon Nefes Girişi (Pulse)</option>
                            <option value="wiggle">Dalgalanma (Wiggle Wave)</option>
                            <option value="neon_flicker">Retro Neon Titremesi (Flicker)</option>
                            <option value="rainbow">Gökkuşağı Renk Akışı (Rainbow)</option>
                            <option value="pulse">Yumuşak Genişleme</option>
                            <option value="blur_fade">Bulanıklaşan Odaklama (Blur Fade)</option>
                        </select>
                    </div>
                </div>

                <!-- TAB 5: Medya -->
                <div id="tab-gorsel" class="tab-content">
                    <div class="form-group">
                        <label>Ek Görsel / Hareketli GIF URL</label>
                        <input type="text" id="inp-media-url" value="{ann_media_url_sb}" placeholder="https://..." class="form-control" oninput="renderPreview()" />
                    </div>
                    
                    <div class="form-group">
                        <label>Görsel Konumu (Align)</label>
                        <select id="inp-media-align" class="form-control" onchange="renderPreview()">
                            <option value="below">Yazının Altında</option>
                            <option value="above">Yazının Üstünde</option>
                            <option value="left">Yazının Solunda</option>
                            <option value="right">Yazının Sağında</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label>Görsel Genişliği (px)</label>
                        <div class="flex-row" style="align-items: center;">
                            <input type="range" id="inp-media-size" min="20" max="500" value="{ann_media_size_sb}" class="form-control" style="flex:3;" oninput="document.getElementById('v-media-size').innerText=this.value+'px'; renderPreview()" />
                            <span id="v-media-size" style="flex:1; text-align:right; font-size:11px; color:#e67e22; font-weight:bold;">{ann_media_size_sb}px</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const parentDoc = window.parent.document;
        
        // Touch & Drag Position state
        let x = {disp_x_sb};
        let y = {disp_y_sb};
        let size = {disp_size_sb};
        let rot = {disp_rot_sb};
        
        // Global colors array
        let charColorsArray = {char_colors_json};
        
        const dragItem = document.getElementById('drag-item');
        const canvasArea = document.getElementById('canvas-area');
        
        // Tab switching controller
        function switchTab(tabId) {{
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            
            const btn = Array.from(document.querySelectorAll('.tab-btn')).find(b => b.getAttribute('onclick').includes(tabId));
            if (btn) btn.classList.add('active');
            
            const content = document.getElementById(tabId);
            if (content) content.classList.add('active');
        }}

        // Dynamic show/hide of specific background fields
        function toggleBgFields() {{
            const bgType = document.getElementById('inp-bg-type').value;
            const colorFields = document.getElementById('bg-color-fields');
            const gradientField = document.getElementById('bg-gradient-field');
            const imageFields = document.getElementById('bg-image-fields');
            
            if (bgType === "none") {{
                colorFields.style.display = "none";
                imageFields.style.display = "none";
            }} else if (bgType === "flat") {{
                colorFields.style.display = "flex";
                gradientField.style.display = "none";
                imageFields.style.display = "none";
            }} else if (bgType === "gradient") {{
                colorFields.style.display = "flex";
                gradientField.style.display = "block";
                imageFields.style.display = "none";
            }} else if (bgType === "image") {{
                colorFields.style.display = "none";
                imageFields.style.display = "block";
            }}
        }}

        // Dynamic show/hide of Neon Glow fields
        function toggleGlowFields() {{
            const glowEnabled = document.getElementById('inp-glow-enabled').checked;
            const intensityWrapper = document.getElementById('glow-intensity-wrapper');
            const colorWrapper = document.getElementById('glow-color-wrapper');
            
            if (glowEnabled) {{
                intensityWrapper.style.display = "block";
                colorWrapper.style.display = "block";
                
                const glowMode = document.querySelector('input[name="glow_color_mode"]:checked').value;
                const fixedPicker = document.getElementById('glow-color-fixed-picker');
                if (glowMode === "fixed") {{
                    fixedPicker.style.display = "block";
                }} else {{
                    fixedPicker.style.display = "none";
                }}
            }} else {{
                intensityWrapper.style.display = "none";
                colorWrapper.style.display = "none";
            }}
        }}

        // Dynamic show/hide of Shadow fields
        function toggleShadowFields() {{
            const shadowEnabled = document.getElementById('inp-shadow-enabled').checked;
            const intensityWrapper = document.getElementById('shadow-intensity-wrapper');
            const colorWrapper = document.getElementById('shadow-color-wrapper');
            
            if (shadowEnabled) {{
                intensityWrapper.style.display = "block";
                colorWrapper.style.display = "block";
            }} else {{
                intensityWrapper.style.display = "none";
                colorWrapper.style.display = "none";
            }}
        }}

        // Rebuild character list & handle character color bindings
        function syncCharColorsCount(textLength) {{
            const textColor = document.getElementById('inp-text-color').value;
            
            if (charColorsArray.length < textLength) {{
                while (charColorsArray.length < textLength) {{
                    charColorsArray.push(textColor);
                }}
            }} else if (charColorsArray.length > textLength) {{
                charColorsArray = charColorsArray.slice(0, textLength);
            }}
            
            const grid = document.getElementById('char-colors-grid');
            if (!grid) return;
            
            const textValue = document.getElementById('inp-text').value;
            let html = "";
            for (let i = 0; i < textLength; i++) {{
                let charStr = textValue[i] || " ";
                if (charStr.trim() === "") charStr = "Boşluk";
                html += `
                <div class="char-color-box">
                    <span>'${{charStr}}'</span>
                    <input type="color" id="char-color-pick-${{i}}" value="${{charColorsArray[i]}}" oninput="updateSingleCharColor(${{i}}, this.value)" />
                </div>`;
            }}
            grid.innerHTML = html;
        }}

        function updateSingleCharColor(index, colorVal) {{
            charColorsArray[index] = colorVal;
            renderPreview();
        }}

        function handleTextChange() {{
            const text = document.getElementById('inp-text').value;
            syncCharColorsCount(text.length);
            renderPreview();
        }}

        function handleTextGlobalColorChange(newColor) {{
            const textVal = document.getElementById('inp-text').value;
            charColorsArray = Array(textVal.length).fill(newColor);
            syncCharColorsCount(textVal.length);
            renderPreview();
        }}

        // Bulk paint helpers
        function applyBulkColor() {{
            const bulkColor = document.getElementById('bulk-color-pick').value;
            const text = document.getElementById('inp-text').value;
            charColorsArray = Array(text.length).fill(bulkColor);
            syncCharColorsCount(text.length);
            renderPreview();
        }}

        function applyWordHighlight() {{
            const textVal = document.getElementById('inp-text').value;
            const target = document.getElementById('paint-word-target').value;
            const color = document.getElementById('paint-word-color').value;
            if (!target) return;
            
            let startPos = 0;
            while (true) {{
                const idx = textVal.indexOf(target, startPos);
                if (idx === -1) break;
                for (let i = idx; i < idx + target.length; i++) {{
                    if (i < charColorsArray.length) {{
                        charColorsArray[i] = color;
                    }}
                }}
                startPos = idx + target.length;
            }}
            syncCharColorsCount(textVal.length);
            renderPreview();
        }}

        // Dynamic render module: mimics python side rendering
        const loadedGoogleFonts = new Set();
        function loadGoogleFontIfNeeded(fontName) {{
            if (fontName === "Space Grotesk" && !loadedGoogleFonts.has("Space Grotesk")) {{
                const link = document.createElement('link');
                link.href = "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;700&display=swap";
                link.rel = "stylesheet";
                document.head.appendChild(link);
                loadedGoogleFonts.add("Space Grotesk");
            }} else if (fontName === "Cinzel" && !loadedGoogleFonts.has("Cinzel")) {{
                const link = document.createElement('link');
                link.href = "https://fonts.googleapis.com/css2?family=Cinzel:wght@700&display=swap";
                link.rel = "stylesheet";
                document.head.appendChild(link);
                loadedGoogleFonts.add("Cinzel");
            }}
        }}

        function renderPreview() {{
            const text = document.getElementById('inp-text').value;
            const font = document.getElementById('inp-font').value;
            const align = document.getElementById('inp-align').value;
            const sizeInp = parseInt(document.getElementById('inp-size').value) || 20;
            const font_weight = document.getElementById('inp-font-weight').value;
            const font_style = document.getElementById('inp-font-style').value;
            const text_decoration = document.getElementById('inp-text-decoration').value;
            const opacity = (parseInt(document.getElementById('inp-opacity').value) || 100) / 100;
            
            const glow_enabled = document.getElementById('inp-glow-enabled').checked;
            const glow_intensity = parseInt(document.getElementById('inp-glow-intensity').value) || 50;
            const glow_color_mode_el = document.querySelector('input[name="glow_color_mode"]:checked');
            const glow_color_mode = glow_color_mode_el ? glow_color_mode_el.value : "auto";
            const glow_color_fixed = document.getElementById('inp-glow-color-fixed').value;
            
            const shadow_enabled = document.getElementById('inp-shadow-enabled').checked;
            const shadow_intensity = parseInt(document.getElementById('inp-shadow-intensity').value) || 50;
            const shadow_color = document.getElementById('inp-shadow-color').value;
            
            const animation_type = document.getElementById('inp-animation-type').value;
            const bg_type = document.getElementById('inp-bg-type').value;
            const bg_color = document.getElementById('inp-bg-color').value;
            const bg_gradient_end = document.getElementById('inp-bg-gradient-end').value;
            const bg_image_url = document.getElementById('inp-bg-image-url').value;
            const bg_opacity = (parseInt(document.getElementById('inp-bg-opacity').value) || 100) / 100;
            const padding_vertical = parseInt(document.getElementById('inp-padding-vertical').value) || 0;
            const padding_horizontal = parseInt(document.getElementById('inp-padding-horizontal').value) || 0;
            const border_radius = parseInt(document.getElementById('inp-border-radius').value) || 0;
            
            const media_url = document.getElementById('inp-media-url').value;
            const media_align = document.getElementById('inp-media-align').value;
            const media_size = parseInt(document.getElementById('inp-media-size').value) || 150;
            
            const text_color = document.getElementById('inp-text-color').value;

            // 1. BG css decoration
            let bg_css = "background: transparent; border: 1px dashed rgba(255,255,255,0.1); padding: 5px;";
            if (bg_type === "flat") {{
                bg_css = `background: ${{bg_color}}; border: 1px solid rgba(255,255,255,0.1); border-radius: ${{border_radius}}px; padding: ${{padding_vertical}}px ${{padding_horizontal}}px;`;
            }} else if (bg_type === "gradient") {{
                bg_css = `background: linear-gradient(135deg, ${{bg_color}}, ${{bg_gradient_end}}); border: 1px solid rgba(255,255,255,0.15); border-radius: ${{border_radius}}px; padding: ${{padding_vertical}}px ${{padding_horizontal}}px;`;
            }} else if (bg_type === "image") {{
                const overlay_op = 1.0 - bg_opacity;
                bg_css = `background: linear-gradient(rgba(17,17,34,${{overlay_op.toFixed(2)}}), rgba(17,17,34,${{overlay_op.toFixed(2)}})), url('${{bg_image_url}}'); background-size: cover; background-position: center; border: 1px solid rgba(255,255,255,0.15); border-radius: ${{border_radius}}px; padding: ${{padding_vertical}}px ${{padding_horizontal}}px;`;
            }}
            
            const bannerWrapper = document.getElementById('banner-wrapper');
            bannerWrapper.className = "";
            bannerWrapper.style.cssText = bg_css + ` text-align: ${{align}}; font-family: '${{font}}', sans-serif; font-size: ${{sizeInp}}px; transition: all 0.15s ease; width: 100%;`;

            // 2. Shadows
            let shadow_css = "";
            if (shadow_enabled) {{
                const off = shadow_intensity * 0.08;
                const blur_s = shadow_intensity * 0.16;
                shadow_css = `${{off.toFixed(1)}}px ${{off.toFixed(1)}}px ${{blur_s.toFixed(1)}}px ${{shadow_color}}`;
            }}

            // 3. Characters
            let rendered_chars_html = "";
            for (let i = 0; i < text.length; i++) {{
                const char = text[i];
                let char_color = charColorsArray[i] || text_color;
                
                let local_glow_color = char_color;
                if (glow_color_mode === "fixed") {{
                    local_glow_color = glow_color_fixed;
                }}
                
                let glow_css = "";
                if (glow_enabled) {{
                    const blur_1 = glow_intensity * 0.2;
                    const blur_2 = glow_intensity * 0.4;
                    glow_css = `0 0 ${{blur_1.toFixed(1)}}px ${{local_glow_color}}, 0 0 ${{blur_2.toFixed(1)}}px ${{local_glow_color}}`;
                }}
                
                let combined_shadows = [glow_css, shadow_css].filter(Boolean).join(", ");
                let shadow_style = combined_shadows ? `text-shadow: ${{combined_shadows}};` : "";
                let glow_val_style = glow_enabled ? `--glow-color: ${{local_glow_color}}; --gl-blur: ${{ (glow_intensity * 0.4).toFixed(1) }}px;` : "";
                let italic_bold_style = `font-weight: ${{font_weight}}; font-style: ${{font_style}}; text-decoration: ${{text_decoration}};`;
                let anim_delay_style = (animation_type === 'wiggle') ? `animation-delay: ${{ (i * 0.08).toFixed(2) }}s;` : "";
                
                let span_class = "";
                if (["neon_pulse", "wiggle", "neon_flicker", "rainbow", "pulse", "blur_fade"].includes(animation_type)) {{
                    span_class = `ann-animate-${{animation_type}}`;
                }}
                
                rendered_chars_html += `<span class="${{span_class}}" style="display: inline-block; white-space: pre-wrap; color: ${{char_color}}; ${{glow_val_style}} ${{shadow_style}} ${{italic_bold_style}} ${{anim_delay_style}}">${{char}}</span>&#8203;`;
            }}

            // 4. Media Render
            let media_html = "";
            if (media_url) {{
                media_html = `<img src="${{media_url}}" style="width: ${{media_size}}px; height: auto; border-radius: 8px; margin: 8px; vertical-align: middle; max-width: 100%; box-shadow: 0 4px 12px rgba(0,0,0,0.4);" />`;
            }}

            // 5. Connect media & layout
            let body_html = "";
            if (media_html) {{
                if (media_align === "above") {{
                    body_html = `<div style="margin-bottom: 8px;">${{media_html}}</div><div>${{rendered_chars_html}}</div>`;
                }} else if (media_align === "below") {{
                    body_html = `<div>${{rendered_chars_html}}</div><div style="margin-top: 8px;">${{media_html}}</div>`;
                }} else if (media_align === "left") {{
                    body_html = `<div style="display: flex; align-items: center; justify-content: ${{align}}; flex-wrap: wrap; gap: 15px;"><div>${{media_html}}</div><div style="flex: 1; text-align: ${{align}};">${{rendered_chars_html}}</div></div>`;
                }} else if (media_align === "right") {{
                    body_html = `<div style="display: flex; align-items: center; justify-content: ${{align}}; flex-wrap: wrap; gap: 15px;"><div style="flex: 1; text-align: ${{align}};">${{rendered_chars_html}}</div><div>${{media_html}}</div></div>`;
                }}
            }} else {{
                body_html = `<div>${{rendered_chars_html}}</div>`;
            }}

            // Overwrite children HTML
            bannerWrapper.innerHTML = `
                <div style="opacity: ${{opacity}}; display: inline-block; width: 100%;">
                    ${{body_html}}
                </div>
            `;

            loadGoogleFontIfNeeded(font);
        }}

        // Format and display coordinates values
        function updateDisplay() {{
            document.getElementById('badge-x').innerText = x + 'px';
            document.getElementById('badge-y').innerText = y + 'px';
            document.getElementById('badge-size').innerText = size + 'px';
            document.getElementById('badge-rot').innerText = rot + '°';
            
            // Sync current size into Property Input Value
            document.getElementById('inp-size').value = size;
        }}
        
        function applyTransforms() {{
            dragItem.style.transform = `translate(${{x}}px, ${{y}}px) rotate(${{rot}}deg)`;
            updateDisplay();
        }}
        
        // TWO-FINGER MULTI TOUCH GESTURES (Pinch, Scaling, Rotate & Zoom)
        let isDragging = false;
        let isPinching = false;
        let startTouchX = 0;
        let startTouchY = 0;
        
        let initTouchDist = 0;
        let initFontSize = 20;
        let initTouchAngle = 0;
        let initRotationAngle = 0;
        
        canvasArea.addEventListener('touchstart', (e) => {{
            if (e.touches.length === 1) {{
                isDragging = true;
                startTouchX = e.touches[0].clientX - x;
                startTouchY = e.touches[0].clientY - y;
            }} else if (e.touches.length === e.touches.length) {{
                isDragging = false;
                isPinching = true;
                const touch1 = e.touches[0];
                const touch2 = e.touches[1];
                
                initTouchDist = Math.hypot(touch2.clientX - touch1.clientX, touch2.clientY - touch1.clientY);
                initFontSize = size;
                
                initTouchAngle = Math.atan2(touch2.clientY - touch1.clientY, touch2.clientX - touch1.clientX);
                initRotationAngle = rot;
            }}
        }});
        
        canvasArea.addEventListener('touchmove', (e) => {{
            if (isDragging && e.touches.length === 1) {{
                x = Math.round(e.touches[0].clientX - startTouchX);
                y = Math.round(e.touches[0].clientY - startTouchY);
                applyTransforms();
            }} else if (isPinching && e.touches.length === 2) {{
                e.preventDefault();
                const touch1 = e.touches[0];
                const touch2 = e.touches[1];
                
                const currentDist = Math.hypot(touch2.clientX - touch1.clientX, touch2.clientY - touch1.clientY);
                const scaleFactor = currentDist / initTouchDist;
                size = Math.max(8, Math.min(120, Math.round(initFontSize * scaleFactor)));
                
                const currentAngle = Math.atan2(touch2.clientY - touch1.clientY, touch2.clientX - touch1.clientX);
                const angleDifference = (currentAngle - initTouchAngle) * (180 / Math.PI);
                rot = Math.round(initRotationAngle + angleDifference);
                
                applyTransforms();
                renderPreview();
            }}
        }}, {{ passive: false }});
        
        canvasArea.addEventListener('touchend', () => {{
            isDragging = false;
            isPinching = false;
        }});
        canvasArea.addEventListener('touchcancel', () => {{
            isDragging = false;
            isPinching = false;
        }});
        
        // MOUSE ACTIONS (Desktop Drag supports)
        let isMouseDown = false;
        let startMouseX = 0;
        let startMouseY = 0;
        
        dragItem.addEventListener('mousedown', (e) => {{
            isMouseDown = true;
            startMouseX = e.clientX - x;
            startMouseY = e.clientY - y;
            e.stopPropagation();
        }});
        
        document.addEventListener('mousemove', (e) => {{
            if (isMouseDown) {{
                x = Math.round(e.clientX - startMouseX);
                y = Math.round(e.clientY - startMouseY);
                applyTransforms();
            }}
        }});
        
        document.addEventListener('mouseup', () => {{
            isMouseDown = false;
        }});
        
        // MOUSE WHEEL ROTATE/SCALING SUPPORT
        canvasArea.addEventListener('wheel', (e) => {{
            e.preventDefault();
            if (e.deltaY < 0) {{
                size = Math.min(120, size + 1);
            }} else {{
                size = Math.max(8, size - 1);
            }}
            applyTransforms();
            renderPreview();
        }}, {{ passive: false }});
        
        // MANUAL BUTTONS HANDLERS
        document.getElementById('btn-size-minus').addEventListener('click', () => {{
            size = Math.max(8, size - 2);
            applyTransforms();
            renderPreview();
        }});
        document.getElementById('btn-size-plus').addEventListener('click', () => {{
            size = Math.min(120, size + 2);
            applyTransforms();
            renderPreview();
        }});
        document.getElementById('btn-rot-left').addEventListener('click', () => {{
            rot = (rot - 15) % 360;
            applyTransforms();
            renderPreview();
        }});
        document.getElementById('btn-rot-right').addEventListener('click', () => {{
            rot = (rot + 15) % 360;
            applyTransforms();
            renderPreview();
        }});
        document.getElementById('btn-reset').addEventListener('click', () => {{
            x = 0;
            y = 0;
            size = 20;
            rot = 0;
            applyTransforms();
            renderPreview();
        }});
        
        document.getElementById('btn-factory-reset').addEventListener('click', () => {{
            if (confirm("Tüm tasarım ayarlarını ve metni fabrika ayarlarına sıfırlamak istediğinize emin misiniz?")) {{
                document.getElementById('inp-text').value = "";
                document.getElementById('inp-font').value = "sans-serif";
                document.getElementById('inp-align').value = "center";
                document.getElementById('inp-font-weight').value = "normal";
                document.getElementById('inp-font-style').value = "normal";
                document.getElementById('inp-text-decoration').value = "none";
                document.getElementById('inp-opacity').value = 100;
                document.getElementById('v-opacity').innerText = "100%";
                
                document.getElementById('inp-glow-enabled').checked = false;
                document.getElementById('inp-glow-intensity').value = 50;
                document.getElementById('v-glow-intensity').innerText = "50";
                
                const autoRadio = document.querySelector('input[name="glow_color_mode"][value="auto"]');
                if (autoRadio) autoRadio.checked = true;
                
                document.getElementById('inp-glow-color-fixed').value = "#FFC000";
                
                document.getElementById('inp-shadow-enabled').checked = false;
                document.getElementById('inp-shadow-intensity').value = 50;
                document.getElementById('v-shadow-intensity').innerText = "50";
                document.getElementById('inp-shadow-color').value = "#000000";
                
                document.getElementById('inp-animation-type').value = "none";
                document.getElementById('inp-bg-type').value = "none";
                document.getElementById('inp-bg-color').value = "#111122";
                document.getElementById('inp-bg-gradient-end').value = "#1a1a3a";
                document.getElementById('inp-bg-image-url').value = "";
                document.getElementById('inp-bg-opacity').value = 100;
                document.getElementById('v-bg-opacity').innerText = "100%";
                document.getElementById('inp-padding-vertical').value = 10;
                document.getElementById('inp-padding-horizontal').value = 15;
                document.getElementById('inp-border-radius').value = 12;
                
                document.getElementById('inp-media-url').value = "";
                document.getElementById('inp-media-align').value = "below";
                document.getElementById('inp-media-size').value = 150;
                document.getElementById('v-media-size').innerText = "150px";
                
                document.getElementById('inp-text-color').value = "#FFFFFF";
                
                x = 0;
                y = 0;
                size = 20;
                rot = 0;
                charColorsArray = [];
                
                applyTransforms();
                toggleBgFields();
                toggleGlowFields();
                toggleShadowFields();
                syncCharColorsCount(0);
                renderPreview();
                
                alert("Tüm değerler temizlendi! Canlıya aktarmak için alt kısımdaki 'CANLIYA KAYDET VE YAYINLA' butonuna basabilirsiniz.");
            }}
        }});
        
        // POPULATE DROPDOWNS AND OPTIONS FROM MODEL
        document.getElementById('inp-font').value = "{ann_font_sb}";
        document.getElementById('inp-align').value = "{ann_align_sb}";
        document.getElementById('inp-font-weight').value = "{ann_weight_sb}";
        document.getElementById('inp-font-style').value = "{ann_style_sb}";
        document.getElementById('inp-text-decoration').value = "{ann_decoration_sb}";
        document.getElementById('inp-animation-type').value = "{ann_animation_type_sb}";
        document.getElementById('inp-bg-type').value = "{ann_bg_type_sb}";
        document.getElementById('inp-media-align').value = "{ann_media_align_sb}";
        
        document.getElementById('inp-glow-enabled').checked = {ann_glow_enabled_sb};
        document.getElementById('inp-shadow-enabled').checked = {ann_shadow_enabled_sb};

        // radios
        const glowModeVal = "{ann_glow_color_mode_sb}";
        const radioBtn = document.querySelector(`input[name="glow_color_mode"][value="${{glowModeVal}}"]`);
        if (radioBtn) radioBtn.checked = true;

        // SUBMIT & SYNC PIPELINES
        function buildFullPayloadJSON() {{
            const text = document.getElementById('inp-text').value;
            const font = document.getElementById('inp-font').value;
            const align = document.getElementById('inp-align').value;
            const sizeInp = parseInt(document.getElementById('inp-size').value) || 20;
            const font_weight = document.getElementById('inp-font-weight').value;
            const font_style = document.getElementById('inp-font-style').value;
            const text_decoration = document.getElementById('inp-text-decoration').value;
            const opacity = parseInt(document.getElementById('inp-opacity').value) || 100;
            
            const glow_enabled = document.getElementById('inp-glow-enabled').checked;
            const glow_intensity = parseInt(document.getElementById('inp-glow-intensity').value) || 50;
            const glow_color_mode_el = document.querySelector('input[name="glow_color_mode"]:checked');
            const glow_color_mode = glow_color_mode_el ? glow_color_mode_el.value : "auto";
            const glow_color_fixed = document.getElementById('inp-glow-color-fixed').value;
            
            const shadow_enabled = document.getElementById('inp-shadow-enabled').checked;
            const shadow_intensity = parseInt(document.getElementById('inp-shadow-intensity').value) || 50;
            const shadow_color = document.getElementById('inp-shadow-color').value;
            
            const animation_type = document.getElementById('inp-animation-type').value;
            const bg_type = document.getElementById('inp-bg-type').value;
            const bg_color = document.getElementById('inp-bg-color').value;
            const bg_gradient_end = document.getElementById('inp-bg-gradient-end').value;
            const bg_image_url = document.getElementById('inp-bg-image-url').value;
            const bg_opacity = parseInt(document.getElementById('inp-bg-opacity').value) || 100;
            const padding_vertical = parseInt(document.getElementById('inp-padding-vertical').value) || 0;
            const padding_horizontal = parseInt(document.getElementById('inp-padding-horizontal').value) || 0;
            const border_radius = parseInt(document.getElementById('inp-border-radius').value) || 0;
            
            const media_url = document.getElementById('inp-media-url').value;
            const media_align = document.getElementById('inp-media-align').value;
            const media_size = parseInt(document.getElementById('inp-media-size').value) || 150;
            
            const text_color = document.getElementById('inp-text-color').value;

            return JSON.stringify({{
                "text": text,
                "size": sizeInp,
                "font": font,
                "align": align,
                "font_weight": font_weight,
                "font_style": font_style,
                "text_decoration": text_decoration,
                "opacity": opacity,
                "displacement_x": x,
                "displacement_y": y,
                "rotation": rot,
                "bg_type": bg_type,
                "bg_color": bg_color,
                "bg_gradient_end": bg_gradient_end,
                "bg_image_url": bg_image_url,
                "bg_opacity": bg_opacity,
                "padding_vertical": padding_vertical,
                "padding_horizontal": padding_horizontal,
                "border_radius": border_radius,
                "glow_enabled": glow_enabled,
                "glow_intensity": glow_intensity,
                "glow_color_mode": glow_color_mode,
                "glow_color_fixed": glow_color_fixed,
                "shadow_enabled": shadow_enabled,
                "shadow_intensity": shadow_intensity,
                "shadow_color": shadow_color,
                "animation_type": animation_type,
                "media_url": media_url,
                "media_size": media_size,
                "media_align": media_align,
                "char_colors": charColorsArray,
                "text_color": text_color
            }});
        }}

        function pushAndSubmit(action) {{
            if (!parentDoc) return;
            const jsonStr = buildFullPayloadJSON();
            
            // Find hidden Streamlit textarea matching JSON label
            const textAreas = Array.from(parentDoc.querySelectorAll('textarea'));
            const pmTextArea = textAreas.find(ta => ta.value && ta.value.startsWith('{{"text":') || ta.ariaLabel === "advanced_json_payload");
            if (pmTextArea) {{
                pmTextArea.value = jsonStr;
                pmTextArea.dispatchEvent(new Event('input', {{ bubbles: true }}));
                pmTextArea.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }} else {{
                // fallback selectors
                const backupTa = parentDoc.querySelector('[data-testid="stTextArea"] textarea');
                if (backupTa) {{
                    backupTa.value = jsonStr;
                    backupTa.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    backupTa.dispatchEvent(new Event('change', {{ bubbles: true }}));
                }}
            }}

            // Let Streamlit register values prior to click
            setTimeout(() => {{
                const parentButtons = Array.from(parentDoc.querySelectorAll('button'));
                let btn;
                if (action === 'save') {{
                    btn = parentButtons.find(b => b.innerText && b.innerText.includes("Tepe Duyurusunu Kaydet"));
                }} else {{
                    btn = parentButtons.find(b => b.innerText && b.innerText.includes("Düzenlemeyi Önizle"));
                }}
                if (btn) {{
                    btn.click();
                }}
            }}, 150);
        }}

        document.getElementById('btn-preview').addEventListener('click', () => pushAndSubmit('preview'));
        document.getElementById('btn-save').addEventListener('click', () => pushAndSubmit('save'));

        // Bootstrap on startup
        syncCharColorsCount(document.getElementById('inp-text').value.length);
        toggleBgFields();
        toggleGlowFields();
        toggleShadowFields();
        renderPreview();
        applyTransforms();
    </script>
</body>
</html>"""

                st.components.v1.html(sandbox_code, height=920, scrolling=True)
                st.markdown("---")
                
                # Dynamic stream sync form structure - completely processed via the CapCut JS pipeline
                with st.form("ann_edit_form", clear_on_submit=False):
                    json_default = json.dumps(ts, ensure_ascii=False)
                    json_input_val = st.text_area("advanced_json_payload", value=json_default, key="advanced_json_payload_key", label_visibility="collapsed")
                    
                    # Beautiful stealth style sheet to hide this fallback form representation entirely in the background
                    st.markdown("""
                        <style>
                        /* Complete stealth mode for fallback forms */
                        div[data-testid="stForm"] {
                            padding: 0px !important;
                            border: none !important;
                            box-shadow: none !important;
                            background: transparent !important;
                            margin: 0px !important;
                        }
                        div[data-testid="stForm"] div[data-testid="stTextArea"]:has(textarea[aria-label="advanced_json_payload"]) {
                            display: none !important;
                        }
                        div[data-testid="stForm"] button[data-testid="stFormSubmitButton"] {
                            display: none !important;
                        }
                        </style>
                    """, unsafe_allow_html=True)
                    
                    # Submit fallback buttons triggered programmatically by JS in the iframe
                    btn_preview = st.form_submit_button("Düzenlemeyi Önizle")
                    btn_save = st.form_submit_button("Tepe Duyurusunu Kaydet")

                # Process the programmatically submitted JSON string
                if btn_preview or btn_save:
                    try:
                        updated_payload = json.loads(json_input_val)
                        
                        # Store as temp settings in memory
                        st.session_state.temp_ann_settings = updated_payload
                        
                        if btn_save:
                            # Write permanently to database
                            db.collection("settings").document("global_announcement").set(updated_payload)
                            trigger_global_rerun(exclude_self=False)
                            st.success("✅ Tepe duyurusu başarıyla kaydedildi ve canlı yayına alındı!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.success("👀 Önizleme başarıyla güncellendi! Yukarıdaki CapCut editör panelinden anlık sonucu görebilirsiniz.")
                            time.sleep(1)
                            st.rerun()
                    except Exception as e:
                        st.error(f"⚠️ Teknik bir hata oluştu: {e}")



    elif st.session_state.current_page == "admin_role_management" and is_kurucu:
        st.title("🛡️ Yönetici Rol Yönetimi")
        col_back_main, col_back_chat = st.columns([5, 5])
        with col_back_main:
            if st.button("⬅️ Yönetici Ana Paneline Dön", key="back_to_main_from_roles", use_container_width=True):
                st.session_state.current_page = "admin_main"
                st.rerun()
        with col_back_chat:
            if st.button("💬 Sohbet Ekranına Dön", key="back_to_chat_from_roles", use_container_width=True):
                st.session_state.current_page = "chat"
                st.rerun()

        st.divider()

        with st.expander("👑 Kendi Profil Stilimi Düzenle", expanded=False):
            st.markdown("### 👑 Kendi Profil Stilimi Düzenle")
            f_color = st.color_picker("Kendi İsim Renginiz (Hex):", value=user_doc.get("isim_rengi", "#FF0000"))
            f_glow = st.checkbox("Kendi Yazı Parlaklığınız (Neon Efekti):", value=user_doc.get("ismin_parlakligi", True))
            f_tag = st.text_input("Kendi Tagınız (Örn: KURUCU, REİS):", value=user_doc.get("tag", "KURUCU"), max_chars=20)
            f_rozet = st.text_input("Kendi Rozetiniz (Örn: 🛠️, 👑):", value=user_doc.get("rozet", "🛠️"), max_chars=10)

            if st.button("💾 Kendi Stilimi Kaydet", type="primary", use_container_width=True):
                user_ref.update({"isim_rengi": f_color, "ismin_parlakligi": f_glow, "tag": f_tag.strip(), "rozet": f_rozet.strip()})
                st.success("✅ Profil stiliniz başarıyla kaydedildi!")
                time.sleep(1)
                st.rerun()

        st.divider()
        st.markdown("### 🔍 Kullanıcı Düzenleme Paneli")

        tab_admin, tab_normal = st.tabs(["🛡️ Yönetici Rolü & Stil", "👤 Normal Kullanıcı Stili"])

        with tab_admin:
            st.markdown("#### 🛡️ Yönetici Rol Atama ve Stil Düzenleme")
            search_email = st.text_input("Yönetici adayı e-posta adresi:", placeholder="ornek@domain.com", key="role_admin_search_email").strip().lower()

            if search_email:
                if search_email == KURUCU_EMAIL.strip().lower():
                    st.error("❌ Bu e-posta adresi kurucuya aittir! Kurucu stili buradan değiştirilemez. Lütfen 'Kendi Profil Stilimi Düzenle' expander'ını kullanın.")
                else:
                    user_query = db.collection("users").where("email", "==", search_email).limit(1).get()
                    if user_query:
                        target_doc = user_query[0]
                        target_id = target_doc.id
                        target_data = target_doc.to_dict()

                        st.text_input("Kullanıcı İsmi (Salt Okunur):", value=target_data.get("isim", "Bilinmeyen"), disabled=True, key=f"am_name_{target_id}")
                        st.text_input("Kullanıcı E-postası (Salt Okunur):", value=target_data.get("email", ""), disabled=True, key=f"am_email_{target_id}")
                        isim_rengi = st.color_picker("İsim Rengi (Hex):", value=target_data.get("isim_rengi", "#FFFFFF"), key=f"am_color_{target_id}")
                        ismin_parlakligi = st.checkbox("Yazı Parlaklığı (CSS Gölge Efekti):", value=target_data.get("ismin_parlakligi", False), key=f"am_glow_{target_id}")
                        tag_val = st.text_input("Kullanıcı Tagı (Örn: Moderatör, Vip):", value=target_data.get("tag", ""), max_chars=20, key=f"am_tag_{target_id}")
                        rozet_val = st.text_input("Kullanıcı Rozeti (Örn: 🛡️, 💎):", value=target_data.get("rozet", ""), max_chars=10, key=f"am_rozet_{target_id}")
                        is_admin_flag = st.checkbox("Yönetici Yap (is_admin):", value=target_data.get("is_admin", False), key=f"am_adminflag_{target_id}")

                        if st.button("💾 Değişiklikleri Kaydet", type="primary", use_container_width=True, key=f"am_save_{target_id}"):
                            update_payload = {
                                "isim_rengi": isim_rengi,
                                "ismin_parlakligi": ismin_parlakligi,
                                "tag": tag_val.strip(),
                                "rozet": rozet_val.strip(),
                                "is_admin": is_admin_flag
                            }
                            if not is_admin_flag and target_data.get("is_admin", False):
                                update_payload["isim_rengi"] = "#FFFFFF"
                                update_payload["ismin_parlakligi"] = False
                                update_payload["tag"] = ""
                                update_payload["rozet"] = ""
                                st.info("ℹ️ Yöneticilik alındı, kullanıcı stili varsayılana sıfırlandı.")

                            db.collection("users").document(target_id).update(update_payload)
                            st.success("✅ Kullanıcı bilgileri başarıyla güncellendi!")
                            st.session_state.valid_users_cache = None
                            time.sleep(1)
                            st.rerun()
                    else:
                        st.error("❌ Eşleşen bir kullanıcı bulunamadı.")

        with tab_normal:
            st.markdown("#### 👤 Normal Kullanıcı Profil Süsü")
            st.write("Bu panelden normal (yönetici olmayan veya yapılmayan) kullanıcıların isminin rengini, tagını ve rozetini düzenleyebilirsiniz.")
            search_email_normal = st.text_input("Normal kullanıcı e-posta adresi:", placeholder="normal@domain.com", key="role_normal_search_email").strip().lower()

            if search_email_normal:
                if search_email_normal == KURUCU_EMAIL.strip().lower():
                    st.error("❌ Bu e-posta adresi kurucuya aittir! Normal kullanıcı stili olarak değiştirilemez.")
                else:
                    user_query_n = db.collection("users").where("email", "==", search_email_normal).limit(1).get()
                    if user_query_n:
                        target_doc_n = user_query_n[0]
                        target_id_n = target_doc_n.id
                        target_data_n = target_doc_n.to_dict()

                        is_target_admin_n = target_data_n.get("is_admin", False)
                        is_target_founder_n = target_data_n.get("email", "").strip().lower() == KURUCU_EMAIL.strip().lower()

                        if is_target_admin_n or is_target_founder_n:
                            st.error("❌ Bu kullanıcı bir yönetici veya kurucudur! Normal kullanıcı stili sekmesinden düzenlenemez. Lütfen 'Yönetici Rolü & Stil' sekmesini kullanın.")
                        else:
                            st.text_input("Kullanıcı İsmi (Salt Okunur):", value=target_data_n.get("isim", "Bilinmeyen"), disabled=True, key=f"nm_name_{target_id_n}")
                            st.text_input("Kullanıcı E-postası (Salt Okunur):", value=target_data_n.get("email", ""), disabled=True, key=f"nm_email_{target_id_n}")
                            isim_rengi_n = st.color_picker("İsim Rengi (Hex):", value=target_data_n.get("isim_rengi", "#FFFFFF"), key=f"nm_color_{target_id_n}")
                            ismin_parlakligi_n = st.checkbox("Yazı Parlaklığı (CSS Gölge Efekti):", value=target_data_n.get("ismin_parlakligi", False), key=f"nm_glow_{target_id_n}")
                            tag_val_n = st.text_input("Kullanıcı Tagı (Örn: Eğlenceli, Vip):", value=target_data_n.get("tag", ""), max_chars=20, key=f"nm_tag_{target_id_n}")
                            rozet_val_n = st.text_input("Kullanıcı Rozeti (Örn: 🎮, ✨):", value=target_data_n.get("rozet", ""), max_chars=10, key=f"nm_rozet_{target_id_n}")

                            if st.button("💾 Normal Kullanıcıyı Kaydet", type="primary", use_container_width=True, key=f"nm_save_{target_id_n}"):
                                # Re-verify current database state just in case to avoid concurrency exploit
                                fresh_doc_n = db.collection("users").document(target_id_n).get().to_dict() or {}
                                if fresh_doc_n.get("is_admin", False) or fresh_doc_n.get("email", "").strip().lower() == KURUCU_EMAIL.strip().lower():
                                    st.error("❌ Hata: Bu kullanıcı bir yöneticiye veya kurucuya dönüştürülmüş! İşlem iptal edildi.")
                                else:
                                    update_payload_n = {
                                        "isim_rengi": isim_rengi_n,
                                        "ismin_parlakligi": ismin_parlakligi_n,
                                        "tag": tag_val_n.strip(),
                                        "rozet": rozet_val_n.strip()
                                    }

                                    db.collection("users").document(target_id_n).update(update_payload_n)
                                    st.success("✅ Normal kullanıcının süslemeleri başarıyla güncellendi!")
                                    st.session_state.valid_users_cache = None
                                    time.sleep(1)
                                    st.rerun()
                    else:
                        st.error("❌ Eşleşen bir kullanıcı bulunamadı.")

            st.divider()
            st.markdown("### 👤 Mevcut Stili Değiştirilenler")

            try:
                all_users_n = db.collection("users").get()
                modified_users_list = []
                for doc in all_users_n:
                    udata = doc.to_dict()
                    if not udata:
                        continue
                    if udata.get("is_admin", False):
                        continue
                    if udata.get("email") == KURUCU_EMAIL:
                        continue
                    if (udata.get("isim_rengi", "#FFFFFF") != "#FFFFFF" or 
                        udata.get("ismin_parlakligi", False) or 
                        udata.get("tag", "") != "" or 
                        udata.get("rozet", "") != ""):
                        modified_users_list.append(doc)

                if modified_users_list:
                    for m_doc in modified_users_list:
                        m_data = m_doc.to_dict()
                        m_id = m_doc.id
                        m_name = m_data.get("isim", "Bilinmiyor")
                        m_email = m_data.get("email", "")
                        m_tag = m_data.get("tag", "")
                        m_rozet = m_data.get("rozet", "")

                        with st.container(border=True):
                            col_m_info, col_m_act = st.columns([7, 3])
                            with col_m_info:
                                _m_color = m_data.get("isim_rengi", "#FFFFFF")
                                _m_glow = m_data.get("ismin_parlakligi", False)
                                _m_styled = get_styled_user_name(m_name, _m_color, _m_glow, m_tag, m_rozet, email=m_email, is_admin=m_data.get("is_admin", False))
                                st.markdown(f"**Kullanıcı:** {_m_styled} ({m_email})", unsafe_allow_html=True)
                                st.markdown(f"🏷️ **Tag:** `{m_tag}` | 🏆 **Rozet:** `{m_rozet}`")
                            with col_m_act:
                                show_style_reset_confirm = st.session_state.get(f"show_style_reset_{m_id}", False)
                                if not show_style_reset_confirm:
                                    if st.button("🔴 Süslemeleri Kaldır", key=f"style_reset_btn_{m_id}", use_container_width=True):
                                        st.session_state[f"show_style_reset_{m_id}"] = True
                                        st.rerun()
                                else:
                                    st.warning("Emin misiniz?")
                                    c_y_s, c_n_s = st.columns(2)
                                    with c_y_s:
                                        if st.button("Evet", key=f"style_reset_yes_{m_id}", type="primary", use_container_width=True):
                                            db.collection("users").document(m_id).update({
                                                "isim_rengi": "#FFFFFF",
                                                "ismin_parlakligi": False,
                                                "tag": "",
                                                "rozet": ""
                                            })
                                            st.session_state[f"show_style_reset_{m_id}"] = False
                                            st.success(f"✅ {m_name} süslemeleri kaldırıldı.")
                                            st.session_state.valid_users_cache = None
                                            time.sleep(1)
                                            st.rerun()
                                    with c_n_s:
                                        if st.button("Hayır", key=f"style_reset_no_{m_id}", use_container_width=True):
                                            st.session_state[f"show_style_reset_{m_id}"] = False
                                            st.rerun()
                else:
                    st.info("ℹ️ Süsü değiştirilmiş herhangi bir normal kullanıcı bulunmuyor.")
            except Exception as e:
                st.error(f"Kullanıcılar yüklenirken bir hata oluştu: {e}")

        st.divider()
        st.markdown("### 🛡️ Mevcut Yöneticiler")

        try:
            admins_query = db.collection("users").where("is_admin", "==", True).get()
            admins_list = [doc for doc in admins_query if doc.to_dict().get("email") != KURUCU_EMAIL]

            if admins_list:
                for admin_doc in admins_list:
                    a_data = admin_doc.to_dict()
                    a_id = admin_doc.id
                    a_name = a_data.get("isim", "Bilinmiyor")
                    a_email = a_data.get("email", "")
                    a_tag = a_data.get("tag", "")
                    a_rozet = a_data.get("rozet", "")

                    with st.container(border=True):
                        col_adm_info, col_adm_act = st.columns([7, 3])
                        with col_adm_info:
                            _a_color = a_data.get("isim_rengi", "#FFFFFF")
                            _a_glow = a_data.get("ismin_parlakligi", False)
                            _a_styled = get_styled_user_name(a_name, _a_color, _a_glow, a_tag, a_rozet, email=a_email, is_admin=True)
                            st.markdown(f"**Yönetici:** {_a_styled} ({a_email})", unsafe_allow_html=True)
                            st.markdown(f"🏷️ **Tag:** `{a_tag}` | 🏆 **Rozet:** `{a_rozet}`")
                        with col_adm_act:
                            show_demote_confirm = st.session_state.get(f"show_demote_{a_id}", False)
                            if not show_demote_confirm:
                                if st.button("🔴 Yöneticilikten Çıkar", key=f"demote_btn_{a_id}", use_container_width=True):
                                    st.session_state[f"show_demote_{a_id}"] = True
                                    st.rerun()
                            else:
                                st.warning("Emin misiniz?")
                                c_y, c_n = st.columns(2)
                                with c_y:
                                    if st.button("Evet", key=f"demote_yes_{a_id}", type="primary", use_container_width=True):
                                        db.collection("users").document(a_id).update({
                                            "is_admin": False,
                                            "isim_rengi": "#FFFFFF",
                                            "ismin_parlakligi": False,
                                            "tag": "",
                                            "rozet": ""
                                        })
                                        st.session_state[f"show_demote_{a_id}"] = False
                                        st.success(f"✅ {a_name} yöneticilikten çıkarıldı ve stili sıfırlandı.")
                                        st.session_state.valid_users_cache = None
                                        time.sleep(1)
                                        st.rerun()
                                with c_n:
                                    if st.button("Hayır", key=f"demote_no_{a_id}", use_container_width=True):
                                        st.session_state[f"show_demote_{a_id}"] = False
                                        st.rerun()

                        try:
                            admin_duyurulari = db.collection("duyurular").where("gonderen_email", "==", a_email).get()
                            def get_tarih_val(doc):
                                t = doc.to_dict().get("tarih")
                                if hasattr(t, "to_datetime"):
                                    t = t.to_datetime()
                                if t is None: return datetime.min.replace(tzinfo=timezone.utc)
                                if t.tzinfo is None: t = t.replace(tzinfo=timezone.utc)
                                return t

                            sorted_duyurular = sorted(admin_duyurulari, key=get_tarih_val, reverse=True)

                            with st.expander("📋 Yapılan Duyuru Geçmişi"):
                                if is_kurucu and sorted_duyurular:
                                    if st.button("🗑️ Duyuru Geçmişini Temizle", key=f"clear_ann_log_{a_id}", type="primary", use_container_width=True):
                                        batch_del = db.batch()
                                        for doc_to_del in sorted_duyurular:
                                            batch_del.delete(doc_to_del.reference)
                                        batch_del.commit()
                                        st.success(f"✅ {a_name} adlı yöneticinin duyuru geçmişi başarıyla temizlendi!")
                                        time.sleep(1)
                                        st.rerun()

                                if sorted_duyurular:
                                    for d_doc in sorted_duyurular:
                                        d_data = d_doc.to_dict()
                                        d_metin = d_data.get("metin", "")
                                        d_hedef = d_data.get("hedef", "Tümü")
                                        d_tarih = d_data.get("tarih")

                                        if hasattr(d_tarih, "to_datetime"):
                                            d_tarih = d_tarih.to_datetime()

                                        tarih_formatted = ""
                                        if d_tarih:
                                            if d_tarih.tzinfo is None: d_tarih = d_tarih.replace(tzinfo=timezone.utc)
                                            tarih_formatted = d_tarih.strftime("%Y-%m-%d %H:%M:%S")

                                        st.markdown(f"**📅 Tarih:** `{tarih_formatted}` | **🎯 Hedef:** `{d_hedef}`")
                                        st.info(d_metin)
                                        st.write("---")
                                else:
                                    st.caption("Bu yönetici henüz herhangi bir duyuru yayınlamadı.")
                        except Exception as e:
                            st.caption(f"Duyuru geçmişi yüklenirken hata oluştu: {e}")
            else:
                st.info("Sistemde atanmış alt yönetici bulunmuyor.")

        except Exception as e:
            st.error(f"Yöneticiler yüklenirken hata oluştu: {e}")

    else:
        # ─── SOHBET SAYFASI ────────────────────────────────────────────
        if st.session_state.current_page == "chat":
            if st.session_state.get("play_send_sound", False):
                st.markdown('<audio autoplay style="display:none;"><source src="https://assets.mixkit.co/active_storage/sfx/1344/1344-84.wav" type="audio/wav"></audio>', unsafe_allow_html=True)
                st.session_state.play_send_sound = False

            # --- ARKA PLAN KONTROL (tamamen görünmez — kullanıcı deneyimini etkilemez) ---
            _bg_container = st.container()
            with _bg_container:
                st.markdown('<div style="display:none !important; height:0; overflow:hidden;"></div>', unsafe_allow_html=True)

                @st.fragment(run_every=30)
                def arka_plan_kontrol(current_uid):
                    if st.session_state.get("current_page") == "admin_tepe_duyuru":
                        return
                    try:
                        snap = db.collection("users").document(current_uid).get()
                        if not snap.exists:
                            return
                        doc = snap.to_dict()

                        # Ban kontrolü
                        kontrol_durum = doc.get("durum", "Aktif")
                        if kontrol_durum == "Pasif":
                            ban_b = doc.get("ban_bitis_zamani")
                            if hasattr(ban_b, "to_datetime"):
                                ban_b = ban_b.to_datetime()
                            if ban_b:
                                if ban_b.tzinfo is None: ban_b = ban_b.replace(tzinfo=timezone.utc)
                                if datetime.now(timezone.utc) < ban_b:
                                    st.session_state.ban_error_on_logout = "❌ Hesabınız yönetici tarafından pasifleştirildi!"
                                    logout_user()
                            else:
                                st.session_state.ban_error_on_logout = "❌ Hesabınız yönetici tarafından pasif duruma getirilmiştir!"
                                logout_user()

                        # Duyuru kontrolü — sadece veri güncelle, UI render etme
                        yeni_duyurular = doc.get("okunmamis_duyurular", [])
                        eski_duyuru_ids = st.session_state.get("cached_duyuru_ids", set())
                        yeni_duyuru_ids = set()
                        for d in yeni_duyurular:
                            if isinstance(d, dict):
                                yeni_duyuru_ids.add(d.get("id", d.get("metin", "")))
                            else:
                                yeni_duyuru_ids.add(str(d))
                        if yeni_duyuru_ids != eski_duyuru_ids:
                            st.session_state.cached_duyuru_ids = yeni_duyuru_ids
                            st.session_state.cached_okunmamis_duyurular = yeni_duyurular
                            st.rerun()
                    except Exception:
                        pass

                arka_plan_kontrol(uid)

            # --- DUYURU UI (fragment dışında, sadece session_state'ten oku) ---
            okunmamis = st.session_state.get("cached_okunmamis_duyurular", [])
            if isinstance(okunmamis, list) and okunmamis:
                duyuru_obj = okunmamis[0]
                d_metin = duyuru_obj.get("metin", "")
                sender_email = duyuru_obj.get("gonderen_email", "")
                sender_name = duyuru_obj.get("gonderen_isim", "Sistem Yöneticisi")
                sender_color = duyuru_obj.get("gonderen_color", "#FFFFFF")
                sender_glow = duyuru_obj.get("gonderen_glow", False)
                sender_tag = duyuru_obj.get("gonderen_tag", "")
                sender_rozet = duyuru_obj.get("gonderen_rozet", "")

                if sender_email.strip().lower() == KURUCU_EMAIL.strip().lower():
                    display_sender = get_styled_user_name(
                        sender_name if sender_name else "Ayaz Kaplan",
                        sender_color if sender_color else "#FF0000",
                        sender_glow, sender_tag if sender_tag else "KURUCU",
                        sender_rozet if sender_rozet else "🛠️",
                        email=sender_email,
                        is_admin=False
                    )
                else:
                    display_sender = get_styled_user_name(sender_name, sender_color, sender_glow, sender_tag, sender_rozet if sender_rozet else "🛡️", email=sender_email, is_admin=True)

                st.markdown(f"""
                <div style="background-color: rgba(255, 0, 0, 0.15); border-left: 5px solid red; padding: 15px; border-radius: 5px; margin-bottom: 10px; box-shadow: 0 0 10px rgba(255, 0, 0, 0.4);">
                    <div style="font-size: 1.15rem; margin-bottom: 5px;">{display_sender}:</div>
                    <div style="color: white !important; font-size: 1.1rem; margin-left: 5px; line-height: 1.4;">{d_metin}</div>
                </div>
                """, unsafe_allow_html=True)

                if st.button("Geç ➡️", key=f"skip_btn_{duyuru_obj.get('id')}", use_container_width=True):
                    db.collection("users").document(uid).update({"okunmamis_duyurular": firestore.ArrayRemove([duyuru_obj])})
                    if "cached_okunmamis_duyurular" in st.session_state:
                        try:
                            st.session_state.cached_okunmamis_duyurular.remove(duyuru_obj)
                        except Exception:
                            pass
                    if "cached_duyuru_ids" in st.session_state:
                        try:
                            st.session_state.cached_duyuru_ids.discard(duyuru_obj.get("id", ""))
                        except Exception:
                            pass
                    st.rerun()

            # --- SOHBET ARAYÜZÜ ---
            # Active 5-minute seen auto-deletion for yetkili_mesajlari
            import time
            now_epoch = int(time.time())
            yetkili_msj_raw = user_doc.get("yetkili_mesajlari", [])
            if not isinstance(yetkili_msj_raw, list):
                yetkili_msj_raw = []
                
            cleaned_yetkili = []
            db_cleanup_needed = False
            for ym in yetkili_msj_raw:
                goruldu_z = ym.get("goruldu_zamani")
                if goruldu_z is not None:
                    # If 5 minutes (300 seconds) have passed since seen, auto-delete it
                    if now_epoch - int(goruldu_z) >= 300:
                        db_cleanup_needed = True
                        continue
                cleaned_yetkili.append(ym)
                
            if db_cleanup_needed:
                user_ref.update({"yetkili_mesajlari": cleaned_yetkili})
                yetkili_msj = cleaned_yetkili
            else:
                yetkili_msj = cleaned_yetkili
                
            gelen_istekler = user_doc.get("gelen_arkadaslik_istekleri", [])
            okunmamis_yetkili = [m for m in yetkili_msj if not m.get("okundu", False)]
            bildirim_sayisi = len(gelen_istekler) + len(okunmamis_yetkili)
            bildirim_badge = f" ({bildirim_sayisi})" if bildirim_sayisi > 0 else ""

            st.markdown(f"""<style>
            div.notification-wrapper button {{
                border-radius: 50% !important;
                width: 44px !important;
                height: 44px !important;
                min-width: 44px !important;
                max-width: 44px !important;
                padding: 0 !important;
                font-size: 20px !important;
                display: inline-flex !important;
                align-items: center !important;
                justify-content: center !important;
                background-color: {st.session_state.tema_rengi} !important;
                border: 2px solid #f39c12 !important;
                box-shadow: 0 4px 12px rgba(243, 156, 18, 0.4) !important;
                transition: transform 0.2s ease, box-shadow 0.2s ease !important;
            }}
            div.notification-wrapper button:hover {{
                transform: scale(1.1) !important;
                box-shadow: 0 6px 16px rgba(243, 156, 18, 0.6) !important;
            }}
            div[data-testid="stPopover"] button {{
                border-radius: 50% !important;
                width: 44px !important;
                height: 44px !important;
                min-width: 44px !important;
                max-width: 44px !important;
                padding: 0 !important;
                font-size: 18px !important;
                display: inline-flex !important;
                align-items: center !important;
                justify-content: center !important;
                background-color: {st.session_state.tema_rengi} !important;
                border: 2px solid #f39c12 !important;
                box-shadow: 0 4px 8px rgba(0,0,0,0.3) !important;
            }}
            </style>""", unsafe_allow_html=True)

            # RENDER GLOBAL ANNOUNCEMENT ABOVE MAIN TITLE
            ann_data = get_global_announcement()
            if ann_data.get("text", "") or ann_data.get("media_url", ""):
                ann_rendered_html = render_custom_banner_html(ann_data)
                # Outer wrapper designed with high safety standards
                st.markdown(f'<div style="width: 100%; max-width: 100%; overflow: visible; position: relative; z-index: 1000; word-wrap: break-word; overflow-wrap: break-word; word-break: break-word; margin-bottom: 25px;">{ann_rendered_html}</div>', unsafe_allow_html=True)

            col_title, col_bildirim = st.columns([6, 1])
            with col_title:
                st.title("🤖 Kaplan Parçası V18.1")
            with col_bildirim:
                st.markdown('<div class="sidebar-info-badge-trigger"></div>', unsafe_allow_html=True)
                # Info button on top
                with st.popover("ℹ️", help="Uygulama Bilgisi"):
                    st.markdown("## 🏢 Hakkımızda")
                    st.markdown("""
**Müstakbel Şirket**, dijital iletişim ve yapay zeka alanında öncü çözümler geliştiren, geleceğin teknolojilerini bugünün ihtiyaçlarıyla buluşturan köklü bir teknoloji kuruluşudur.

**Kaplan Parçası V18.1**, Müstakbel Şirket bünyesinde geliştirilen amiral gemisi yapay zeka platformudur. Gerçek zamanlı sohbet, yapay zeka destekli asistan, YouTube entegrasyonu ve topluluk yönetimi tek çatı altında sunulmaktadır.
                    """)
                    st.divider()
                    st.markdown("## 🎯 Misyonumuz")
                    st.markdown("""
Kullanıcılarımıza güvenli, hızlı ve yapay zeka destekli bir dijital iletişim ortamı sunmak; teknolojiyi herkes için erişilebilir kılarak toplulukları bir araya getirmek ve bilgiye ulaşmayı kolaylaştırmaktır.
                    """)
                    st.divider()
                    st.markdown("## 🚀 Vizyonumuz")
                    st.markdown("""
Yapay zeka ve gerçek zamanlı iletişim teknolojilerini birleştirerek Türkiye'nin en yenilikçi dijital topluluk platformu olmak; kullanıcı deneyimini sürekli iyileştirerek global ölçekte rekabet eden bir ekosistem oluşturmaktır.
                    """)
                    st.divider()
                    st.markdown("## 👥 Kadromuz")
                    st.markdown("""
<div style="background:rgba(255,165,0,0.08);border-left:3px solid #f39c12;padding:12px 14px;border-radius:6px;">
<b>👑 Kurucu & CEO:</b> Ayaz Kaplan<br>
<b>🛡️ Yönetici & Tester:</b> Mehmet Sür
</div>
                    """, unsafe_allow_html=True)

                # Notification button directly below Info button
                # special notification badge display inside circle
                st.markdown('<div class="notification-wrapper">', unsafe_allow_html=True)
                btn_emoji = f"🔔" if bildirim_sayisi == 0 else f"🔴"
                if st.button(btn_emoji, key="bildirim_btn", help=f"Bildirimler ({bildirim_sayisi})"):
                    st.session_state.bildirim_panel_open = not st.session_state.bildirim_panel_open
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            # --- BİLDİRİM PANELİ ---
            if st.session_state.bildirim_panel_open:
                with st.container(border=True):
                    st.markdown("### 🔔 Bildirimler")
                    tab_arkadaslik, tab_yetkili = st.tabs(["👥 Arkadaşlık İstekleri", "✉️ Yetkili Mesajları"])

                    with tab_arkadaslik:
                        if gelen_istekler:
                            for istek_uid in gelen_istekler:
                                try:
                                    if "user_cache" not in st.session_state:
                                        st.session_state.user_cache = {}
                                    if istek_uid in st.session_state.user_cache:
                                        istek_d = st.session_state.user_cache[istek_uid]
                                    else:
                                        istek_snap = db.collection("users").document(istek_uid).get()
                                        if istek_snap.exists:
                                            istek_d = istek_snap.to_dict()
                                            st.session_state.user_cache[istek_uid] = istek_d
                                        else:
                                            istek_d = None
                                    if istek_d:
                                        istek_isim = istek_d.get("isim", "Bilinmiyor")
                                        istek_color = istek_d.get("isim_rengi", "#FFFFFF")
                                        istek_glow = istek_d.get("ismin_parlakligi", False)
                                        istek_tag = istek_d.get("tag", "")
                                        istek_rozet = istek_d.get("rozet", "")
                                        
                                        # kurucu check
                                        if istek_d.get("email", "").strip().lower() == KURUCU_EMAIL:
                                            if not istek_tag:
                                                istek_color = "#FF0000"
                                                istek_glow = True
                                                istek_tag = "KURUCU"
                                                istek_rozet = "🛠️"
                                        
                                        istek_styled = get_styled_user_name(istek_isim, istek_color, istek_glow, istek_tag, istek_rozet, email=istek_d.get("email"), is_admin=istek_d.get("is_admin", False))
                                        istek_foto = istek_d.get("profil_foto", "")
                                        istek_foto_src = f"data:image/jpeg;base64,{istek_foto}" if istek_foto else "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
                                        col_bf, col_bn, col_ba = st.columns([1, 4, 3])
                                        with col_bf:
                                            st.markdown(f'<img src="{istek_foto_src}" style="width:30px;height:30px;border-radius:50%;object-fit:cover;"/>', unsafe_allow_html=True)
                                        with col_bn:
                                            st.markdown(istek_styled, unsafe_allow_html=True)
                                        with col_ba:
                                            if st.button("✅ Kabul", key=f"kabul_{istek_uid}", use_container_width=True):
                                                current_friends = user_doc_fresh.get("arkadaslar", [])
                                                requester_friends = istek_d.get("arkadaslar", [])
                                                if len(current_friends) >= 300:
                                                    st.error("Maksimum arkadaş limitine (300) ulaştınız!")
                                                elif len(requester_friends) >= 300:
                                                    st.error("Bu kullanıcının arkadaş limiti dolu! (Maksimum 300)")
                                                else:
                                                    # Her iki tarafı arkadaş yap
                                                    user_ref.update({
                                                        "arkadaslar": firestore.ArrayUnion([istek_uid]),
                                                        "gelen_arkadaslik_istekleri": firestore.ArrayRemove([istek_uid])
                                                    })
                                                    db.collection("users").document(istek_uid).update({
                                                        "arkadaslar": firestore.ArrayUnion([uid]),
                                                        "gonderilen_arkadaslik_istekleri": firestore.ArrayRemove([uid])
                                                    })
                                                    st.success(f"'{istek_isim}' artık arkadaşınız!")
                                                    st.rerun()
                                            if st.button("❌ Reddet", key=f"red_{istek_uid}", use_container_width=True):
                                                user_ref.update({"gelen_arkadaslik_istekleri": firestore.ArrayRemove([istek_uid])})
                                                db.collection("users").document(istek_uid).update({
                                                    "gonderilen_arkadaslik_istekleri": firestore.ArrayRemove([uid])
                                                })
                                                st.rerun()
                                except Exception:
                                    pass
                        else:
                            st.caption("Yeni arkadaşlık isteği yok.")

                    with tab_yetkili:
                        if yetkili_msj and isinstance(yetkili_msj, list):
                            for ym_idx, ym in enumerate(reversed(yetkili_msj)):
                                ym_gonderen_uid = ym.get("gonderen_uid", "")
                                ym_gonderen = ym.get("gonderen_isim", "Yetkili")
                                ym_styled_gonderen = ym_gonderen
                                if ym_gonderen_uid:
                                    try:
                                        if "user_cache" not in st.session_state:
                                            st.session_state.user_cache = {}
                                        if ym_gonderen_uid in st.session_state.user_cache:
                                            s_d = st.session_state.user_cache[ym_gonderen_uid]
                                        else:
                                            sender_snap = db.collection("users").document(ym_gonderen_uid).get()
                                            if sender_snap.exists:
                                                s_d = sender_snap.to_dict()
                                                st.session_state.user_cache[ym_gonderen_uid] = s_d
                                            else:
                                                s_d = None
                                        if s_d:
                                            s_color = s_d.get("isim_rengi", "#FFFFFF")
                                            s_glow = s_d.get("ismin_parlakligi", False)
                                            s_tag = s_d.get("tag", "")
                                            s_rozet = s_d.get("rozet", "")
                                            if s_d.get("email", "").strip().lower() == KURUCU_EMAIL:
                                                if not s_tag:
                                                    s_color = "#FF0000"
                                                    s_glow = True
                                                    s_tag = "KURUCU"
                                                    s_rozet = "🛠️"
                                            ym_styled_gonderen = get_styled_user_name(ym_gonderen, s_color, s_glow, s_tag, s_rozet, email=s_d.get("email"), is_admin=s_d.get("is_admin", False))
                                    except Exception:
                                        pass
                                ym_icerik = ym.get("icerik", "")
                                ym_zaman = ym.get("zaman", "")
                                ym_okundu = ym.get("okundu", False)
                                ym_goruldu_z = ym.get("goruldu_zamani")
                                
                                countdown_text = ""
                                if ym_goruldu_z is not None:
                                    kalan_sn = 300 - (now_epoch - int(ym_goruldu_z))
                                    if kalan_sn > 0:
                                        kalan_dk = kalan_sn // 60
                                        kalan_sn_offset = kalan_sn % 60
                                        countdown_text = f' <span style="font-size:0.8em;color:#e67e22;font-weight:600;margin-left:8px;">⏳ {kalan_dk} dk {kalan_sn_offset} sn sonra silinecek</span>'
                                    else:
                                        countdown_text = ' <span style="font-size:0.8em;color:red;font-weight:600;margin-left:8px;">⏳ Siliniyor...</span>'
                                else:
                                    countdown_text = ' <span style="font-size:0.8em;color:#f39c12;font-weight:600;margin-left:8px;">⏳ Görüldüğünde 5 dk sayacı başlayacak</span>'
                                    
                                badge = "🆕 " if not ym_okundu else ""
                                st.markdown(f"""<div style="background:rgba(243,156,18,0.1);border-left:3px solid #f39c12;padding:8px 12px;border-radius:6px;margin-bottom:6px;">
                                    <div style="font-size:0.95rem;display:flex;align-items:center;flex-wrap:wrap;gap:5px;"><strong>{badge}</strong>{ym_styled_gonderen} <span style="font-size:0.75em;color:#888;">({ym_zaman})</span>{countdown_text}</div>
                                    <div style="margin-top:6px;color:#fff;">{ym_icerik}</div>
                                </div>""", unsafe_allow_html=True)
                            
                            # Okundu ve görüldü olarak işaretle (sayaç başlat)
                            guncellenmis = []
                            db_changed = False
                            for ym in yetkili_msj:
                                ym_copy = dict(ym)
                                if not ym_copy.get("okundu", False) or ym_copy.get("goruldu_zamani") is None:
                                    ym_copy["okundu"] = True
                                    ym_copy["goruldu_zamani"] = now_epoch
                                    db_changed = True
                                guncellenmis.append(ym_copy)
                            if db_changed:
                                user_ref.update({"yetkili_mesajlari": guncellenmis})
                        else:
                            st.caption("Yetkili mesajı yok.")

                    if st.button("Kapat", key="bildirim_kapat_btn", use_container_width=True):
                        st.session_state.bildirim_panel_open = False
                        st.rerun()

            # --- Fresh User Info and Display Name ---
            user_doc_fresh = user_ref.get().to_dict()
            kullanici_ismi_fresh = user_doc_fresh.get('isim', kullanici_ismi)

            u_color_fresh = user_doc_fresh.get("isim_rengi", "#FFFFFF")
            u_glow_fresh = user_doc_fresh.get("ismin_parlakligi", False)
            u_tag_fresh = user_doc_fresh.get("tag", "")
            u_rozet_fresh = user_doc_fresh.get("rozet", "")
            _user_foto = user_doc_fresh.get("profil_foto", "")
            _user_avatar_url = f"data:image/jpeg;base64,{_user_foto}" if _user_foto else USER_AVATAR

            if is_kurucu:
                if not user_doc_fresh.get("tag"):
                    u_color_fresh = "#FF0000"
                    u_glow_fresh = True
                    u_rozet_fresh = "🛠️"
                    u_tag_fresh = "KURUCU"

            display_name = get_styled_user_name(kullanici_ismi_fresh, u_color_fresh, u_glow_fresh, u_tag_fresh, u_rozet_fresh, email=email, is_admin=is_admin_user)

            def ai_cevap(mesajlar):
                current_doc = user_ref.get().to_dict()
                current_name = current_doc.get("isim", "Kullanıcı")
                is_admin_user_fresh = current_doc.get("is_admin", False)
                user_tag_fresh_ai = current_doc.get("tag", "")
                user_rozet_fresh_ai = current_doc.get("rozet", "")

                # 🌐 AUTOMATIC WEB SEARCH (Internet/Google Chrome Integration)
                search_context = ""
                last_user_query = ""
                if mesajlar:
                    for msg in reversed(mesajlar):
                        if msg.get("role") == "user":
                            last_user_query = msg.get("content", "")
                            break
                
                search_results = ""
                thinking_process = ""
                
                # OPTIMIZATION: Only search when the query actually contains informational keywords.
                should_search = False
                if last_user_query:
                    q_lower = last_user_query.lower()
                    search_keywords = [
                        "ara", "bul", "kimdir", "nedir", "kaç", "ne zaman", "hava durumu", "hava",
                        "son durum", "son dakika", "haber", "şampiyon", "skor", "maç", "galatasaray", "fenerbahçe", "beşiktaş",
                        "gelişme", "fiyat", "dolar", "euro", "altın", "borsa", "kim", "gündem",
                        "nerede", "nasıl", "neden", "araştır", "google", "chrome", "internet", "vizyon", "sinema", "vizyonda",
                        "saat kaç", "bugün", "tarih", "güncel", "en son", "saat", "zaman"
                    ]
                    if len(q_lower) >= 3 and any(kw in q_lower for kw in search_keywords):
                        should_search = True

                if should_search and last_user_query:
                    search_results = web_ara(last_user_query)
                    if search_results:
                        search_context = (
                            f"\n\n🌍 LIVE CHROME INTERNET SEARCH RESULTS FOR '{last_user_query}':\n"
                            f"{search_results}\n"
                            f"Use this live information to answer the user accurately and fully."
                        )
                        thinking_process = (
                            f"Kullanıcının '{last_user_query}' sorgusu için canlı arama motoru tetiklendi. "
                            f"Elde edilen web sonuçları ve kaynaklar Kaplan Parçası tarafından saniyeler içinde analiz edilerek doğrulandı."
                        )
                    else:
                        thinking_process = f"Sorgu ('{last_user_query}') analiz edildi. Mevcut yerel sistem hafızası kontrol edildi."
                else:
                    thinking_process = "Sohbet akışı ve geçmiş konuşma bağlamı analiz edildi. Güvenli ve kurallara uygun yanıt oluşturma aşamasına geçildi."

                if is_kurucu:
                    rol_tanimi = "Kurucu ve Sistem Sahibi (Ayaz Kaplan)"
                    hitap_tarzi = "Kurucum, Reis, Kurucum Ayaz, Reis Ayaz Kaplan"
                    uslub = "Sonsuz sadakat, saygı, hürmet ve bağlılık içeren, 'Kurucum' ve 'Reis' hitaplarının her fırsatta kullanıldığı asil bir üslup."
                elif is_admin_user_fresh:
                    rol_tanimi = "Sistem Yöneticisi (is_admin: True olan alt yetkili yönetici)"
                    hitap_tarzi = "Yöneticim, Sayın Yöneticim veya Yöneticim [Kullanıcı İsmi]"
                    uslub = "Profesyonel, rütbeye ve hiyerarşiye son derece saygılı, resmi, 'Yöneticim' hitabını tam benimseyen asil bir üslup."
                else:
                    rol_tanimi = "Normal Sistem Kullanıcısı"
                    hitap_tarzi = f"Doğrudan ismiyle ({current_name}), Reis veya Dostum"
                    uslub = "Samimi, kaplan gibi dik duruşlu, sıcak, yardımsever ama aşırı resmiyet veya kurucu/yöneticiye duyulan rütbeli hitapları içermeyen saygın bir üslup."

                tag_tanimi = f"Tagı: [{user_tag_fresh_ai}]" if user_tag_fresh_ai else "Tagı: Bulunmuyor"
                rozet_tanimi = f"Rozeti: [{user_rozet_fresh_ai}]" if user_rozet_fresh_ai else "Rozeti: Bulunmuyor"
                user_foto_ai = current_doc.get("profil_foto", "")
                foto_tanimi = "Profil Fotoğrafı: Var (yüklenmiş)" if user_foto_ai else "Profil Fotoğrafı: Henüz belirlenmemiş"

                tr_saat_ai = get_tr_time().strftime("%H:%M")
                tr_tarih_ai = get_tr_time().strftime("%d.%m.%Y")

                sistem_mesaji = (
                    "Senin adın Kaplan Parçası. Kurucun ve yaratıcın Ayaz Kaplan'dır. "
                    "Resmi yöneticin Mehmet Sür'dür. Müstakbel Şirket bünyesinde görev yapıyorsun. "
                    "Bu iki bilgiyi kesinlikle ve her zaman bil: Kurucu = Ayaz Kaplan, Resmi Yönetici = Mehmet Sür.\n\n"
                    f"⏰ ŞU ANKİ GÜNCEL TÜRKİYE ZAMANI:\n"
                    f"- Güncel Saat: {tr_saat_ai}\n"
                    f"- Güncel Tarih: {tr_tarih_ai}\n\n"
                    "Sohbet ettiğin kullanıcının anlık veritabanı yetki ve rütbe bilgileri aşağıda belirtilmiştir.\n\n"
                    f"👤 KONUŞTUĞUN KİŞİNİN BİLGİLERİ:\n"
                    f"- Kullanıcı Adı: {current_name}\n"
                    f"- Sistem Rolü/Hiyerarşisi: {rol_tanimi}\n"
                    f"- {tag_tanimi}\n"
                    f"- {rozet_tanimi}\n"
                    f"- {foto_tanimi}\n\n"
                    f"📢 HITAP VE DURUŞ TALİMATLARI:\n"
                    f"1. Karşındaki kişiye uygun hitap şekli: {hitap_tarzi}\n"
                    f"2. Benimsemen gereken üslup yapısı: {uslub}\n"
                    f"3. Eğer karşındaki kişi Kurucun (Ayaz Kaplan) ise ona kesinlikle her fırsatta 'Kurucum' veya 'Reis' diye hitap et.\n"
                    f"4. Eğer karşındaki kişi bir Yönetici ise ona kesinlikle 'Yöneticim' şeklinde rütbeli ve saygılı hitaplar kullan.\n"
                    f"5. Eğer normal bir kullanıcı ise ona samimi ve asil bir duruşla 'Reis', 'Dostum' veya doğrudan ismiyle hitap et.\n\n"
                    "⚠️ ÖNEMLİ KURALLAR (BOŞ YAPMAMA VE NETLİK):\n"
                    "- Sadece ve doğrudan kullanıcının son mesajındaki güncel sorusuna odaklan. Kullanıcı sormadığı sürece başka hiçbir konudan (geçmiş konulardan, tarihten, güncel saatten, futboldan, spor kulüplerinden veya şampiyonluklardan) asla bahsetme. Unutma, sormadığı şeyleri cevaplamak kesinlikle yasaktır.\n"
                    "- Geçmiş konuşmalarda kalmış ve bu mesajda sorulmamış konuları/soruları kendiliğinden tekrar açma ve cevaplama.\n"
                    "- Tarih veya zaman bilgisi istenmediği sürece yanıtlara tarih veya saati ekleme.\n"
                    "- Kesinlikle ve hiçbir koşulda, yıldızlar (asterisk - *) veya parantezler içinde fiziksel hareketler, jestler, mimikler veya rol yapma eylemleri (*doğrulur*, *eğilerek selam verir*, *saygıyla eğilir*, *başını eğer*, *gülümser* vb.) yazma, bunları canlandırma. Tamamen doğrudan, asil ve düzgün bir konuşma metni üret.\n"
                    "- Mizah ve Espri Anlayışı: Zeki ve yerinde olsun. Her mesaja zorlama espri sıkıştırma. Kullanıcı ciddi konuşuyorsa tamamen ciddi ve vakur kal.\n\n"
                    "📝 TÜRKÇE KARAKTER DÜZELTME TALİMATI:\n"
                    "Kullanıcılar bazen Türkçe özel karakterleri kullanmadan yazabilir. Bu tür yazımlarda kullanıcıyı düzeltme, sadece mesajı doğru anla ve doğru Türkçe ile yanıt ver.\n"
                    f"{search_context}"
                )
                
                # Format messages payload to OpenRouter
                payload = {"model": MODEL, "messages": [{"role": "system", "content": sistem_mesaji}] + mesajlar}
                headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}
                try:
                    res = requests.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers=headers, json=payload, timeout=30
                    )
                    res.raise_for_status()
                    content = res.json()['choices'][0]['message']['content']
                    return {
                        "content": content,
                        "search_query": last_user_query,
                        "search_results": search_results,
                        "thinking_process": thinking_process
                    }
                except Exception as e:
                    return {
                        "content": "⚠️ Bir hata oluştu, lütfen tekrar dene Reis.",
                        "search_query": last_user_query,
                        "search_results": "",
                        "thinking_process": f"İstek sırasında bir teknik hata meydana geldi: {e}"
                    }

            last_assistant_idx = -1
            last_user_idx = -1
            for i, msg in enumerate(st.session_state.messages):
                if msg["role"] == "assistant":
                    last_assistant_idx = i
                else:
                    last_user_idx = i

            for idx, m in enumerate(st.session_state.messages):
                if m["role"] == "assistant":
                    content_rendered = detect_and_render_media(m["content"])
                    
                    # Read research and thinking fields
                    search_query = m.get("search_query", "")
                    search_results = m.get("search_results", "")
                    thinking_process = m.get("thinking_process", "")
                    
                    thinking_html = ""
                    if search_query or thinking_process:
                        thinking_html = (
                            f'<div style="font-size: 0.8rem; color: #f39c12; margin: 2px 0 8px 0; display: flex; align-items: center; gap: 6px; font-weight: 500; font-style: italic; opacity: 0.9;">'
                            f'🧠 <span>Düşünülüyor...</span>'
                            f'</div>'
                        )

                    if idx == last_assistant_idx and ("animated_message_indices" not in st.session_state or idx not in st.session_state.animated_message_indices):
                        if "animated_message_indices" not in st.session_state:
                            st.session_state.animated_message_indices = set()
                        
                        st.session_state.animated_message_indices.add(idx)
                        import time
                        placeholder = st.empty()
                        words = m["content"].split()
                        total_words = len(words)
                        
                        if total_words > 0:
                            # Calculate dynamic delay and step to make short messages look natural and long messages fast
                            delay = min(0.08, 1.8 / total_words)
                            step = 1 if total_words < 40 else max(1, total_words // 40)
                            for i in range(1, total_words + 1, step):
                                sub_text = " ".join(words[:i])
                                rendered_sub = detect_and_render_media(sub_text)
                                placeholder.markdown(
                                    f'''<div class="assistant-box"><img src="{AVATAR_URL}" class="avatar"><div class="assistant-bubble"><div class="header-box">Kaplan Parçası</div>{thinking_html}<div style="color:white !important;">{rendered_sub}</div></div></div>''',
                                    unsafe_allow_html=True
                                )
                                time.sleep(delay * step)
                        placeholder.markdown(
                            f'''<div class="assistant-box"><img src="{AVATAR_URL}" class="avatar"><div class="assistant-bubble"><div class="header-box">Kaplan Parçası</div><div style="color:white !important;">{content_rendered}</div></div></div>''',
                            unsafe_allow_html=True
                        )
                    else:
                        with st.container():
                            st.markdown(
                                f'''<div class="assistant-box"><img src="{AVATAR_URL}" class="avatar"><div class="assistant-bubble"><div class="header-box">Kaplan Parçası</div><div style="color:white !important;">{content_rendered}</div></div></div>''',
                                unsafe_allow_html=True
                            )

                    if idx == last_assistant_idx:
                        st.markdown('<div class="assistant-ops-marker"></div>', unsafe_allow_html=True)
                        if st.button("↻", key=f"assistant_regen_{idx}"):
                            with st.spinner("Kaplan Parçası analiz ediyor ve yeni bir yanıt oluşturuyor..."):
                                messages_context = st.session_state.messages[:idx]
                                cevap_dict = ai_cevap(messages_context[-6:])
                                new_chat = list(st.session_state.messages)
                                new_chat[idx]["content"] = cevap_dict["content"]
                                new_chat[idx]["search_query"] = cevap_dict["search_query"]
                                new_chat[idx]["search_results"] = cevap_dict["search_results"]
                                new_chat[idx]["thinking_process"] = cevap_dict["thinking_process"]
                                st.session_state.messages = new_chat
                                user_ref.update({"sohbet_gecmisi": new_chat})
                                if "animated_message_indices" in st.session_state:
                                    st.session_state.animated_message_indices.discard(idx)
                                st.success("Yeni yanıt oluşturuldu!")
                                st.rerun()
                else:
                    msg_name = m.get("isim", kullanici_ismi_fresh)
                    msg_color = m.get("color", u_color_fresh)
                    msg_glow = m.get("glow", u_glow_fresh)
                    msg_tag = m.get("tag", u_tag_fresh)
                    msg_rozet = m.get("rozet", u_rozet_fresh)
                    msg_display_name = get_styled_user_name(msg_name, msg_color, msg_glow, msg_tag, msg_rozet, email=email, is_admin=is_admin_user)
                    content_rendered = detect_and_render_media(m["content"])
                    
                    with st.container():
                        st.markdown(
                            f'''<div class="user-box"><div class="user-bubble"><div class="header-box" style="text-align: right; margin-bottom: 5px;">{msg_display_name}</div><div style="color:white !important; text-align: right;">{content_rendered}</div></div><img src="{_user_avatar_url}" class="avatar"></div>''',
                            unsafe_allow_html=True
                        )

                    if idx == last_user_idx:
                        st.markdown('<div class="user-ops-marker"></div>', unsafe_allow_html=True)
                        if st.button("✎", key=f"user_edit_trigger_{idx}"):
                            st.session_state.active_chat_edit_idx = idx
                            st.session_state.active_chat_edit_text = m["content"]
                            st.rerun()

                    if st.session_state.get("active_chat_edit_idx") == idx:
                        edit_val = st.text_input("Mesajı düzenle:", value=st.session_state.active_chat_edit_text, key=f"chat_edit_inp_{idx}")
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.button("Kaydet", key=f"chat_save_edit_{idx}", use_container_width=True):
                                if edit_val.strip():
                                    with st.spinner("Kaplan Parçası yeni yanıtı hazırlıyor..."):
                                        new_chat = [dict(msg) for msg in st.session_state.messages]
                                        new_chat[idx]["content"] = edit_val.strip()
                                        new_chat = new_chat[:idx+1]
                                        cevap_dict = ai_cevap(new_chat[-6:])
                                        new_chat.append({
                                            "role": "assistant",
                                            "content": cevap_dict["content"],
                                            "search_query": cevap_dict["search_query"],
                                            "search_results": cevap_dict["search_results"],
                                            "thinking_process": cevap_dict["thinking_process"]
                                        })
                                        st.session_state.messages = new_chat
                                        user_ref.update({"sohbet_gecmisi": new_chat})
                                        st.session_state.pop("active_chat_edit_idx", None)
                                        st.session_state.pop("active_chat_edit_text", None)
                                        st.success("Mesaj güncellendi ve yeni yanıt oluşturuldu!")
                                        st.rerun()
                        with col_cancel:
                            if st.button("Vazgeç", key=f"chat_cancel_edit_{idx}", use_container_width=True):
                                st.session_state.pop("active_chat_edit_idx", None)
                                st.session_state.pop("active_chat_edit_text", None)
                                st.rerun()

            if "kufur_warning" in st.session_state: st.error(st.session_state.kufur_warning)

            def send_message():
                val = st.session_state.get("main_chat_input_field", "").strip()
                if val:
                    if kufur_var_mi(val):
                        st.session_state.kufur_warning = "⚠️ Mesajınız uygunsuz içerik nedeniyle engellendi!"
                        st.session_state["main_chat_input_field"] = ""
                        return

                    st.session_state.pop("kufur_warning", None)

                    u_isim_send = user_doc_fresh.get("isim", kullanici_ismi)
                    u_color_send = user_doc_fresh.get("isim_rengi", "#FFFFFF")
                    u_glow_send = user_doc_fresh.get("ismin_parlakligi", False)
                    u_tag_send = user_doc_fresh.get("tag", "")
                    u_rozet_send = user_doc_fresh.get("rozet", "")

                    if is_kurucu:
                        if not user_doc_fresh.get("tag"):
                            u_color_send = "#FF0000"
                            u_glow_send = True
                            u_rozet_send = "🛠️"
                            u_tag_send = "KURUCU"
                    elif user_doc_fresh.get("is_admin", False):
                        if not user_doc_fresh.get("tag"):
                            u_color_send = u_color_send if (u_color_send and u_color_send != "#FFFFFF") else "#9b59b6"
                            u_glow_send = True
                            u_rozet_send = "🛡️"
                            u_tag_send = "YÖNETİCİ"

                    user_msg = {
                        "role": "user",
                        "content": val,
                        "isim": u_isim_send,
                        "color": u_color_send,
                        "glow": u_glow_send,
                        "tag": u_tag_send,
                        "rozet": u_rozet_send
                    }

                    st.session_state.messages.append(user_msg)
                    st.session_state.play_send_sound = True
                    user_ref.update({"sohbet_gecmisi": firestore.ArrayUnion([user_msg])})

                    with st.spinner("Kaplan Parçası düşünüyor..."):
                        cevap_dict = ai_cevap(st.session_state.messages[-6:])

                    assistant_msg = {
                        "role": "assistant",
                        "content": cevap_dict["content"],
                        "search_query": cevap_dict["search_query"],
                        "search_results": cevap_dict["search_results"],
                        "thinking_process": cevap_dict["thinking_process"]
                    }
                    st.session_state.messages.append(assistant_msg)
                    user_ref.update({"sohbet_gecmisi": firestore.ArrayUnion([assistant_msg])})

                    st.session_state["main_chat_input_field"] = ""

            st.text_area("Mesajını yaz:", key="main_chat_input_field", height=100)
            st.button("🚀 Gönder", on_click=send_message)

        # ═══════════════════════════════════════════════════
        # 👥 ARKADAŞ ARAMA SAYFASI
        # ═══════════════════════════════════════════════════
        elif st.session_state.current_page == "arkadas_ara":
            st.title("👥 Arkadaş Ara")
            if st.button("← Sohbete Dön", key="arkadas_geri_btn", use_container_width=True):
                st.session_state.current_page = "chat"
                st.rerun()

            st.divider()
            arama_input = st.text_input("🔍 Kullanıcı adı ile ara:", key="arkadas_arama_input", placeholder="İsim yazın...")

            # Tüm kullanıcıları çek
            all_users_snap = db.collection("users").get()
            tum_kullanicilar = []
            for u_snap in all_users_snap:
                u_d = u_snap.to_dict()
                if not u_d: continue
                u_em = u_d.get("email", "").strip().lower()
                if u_em == user_doc.get("email", "").strip().lower(): continue
                if u_d.get("durum", "Aktif") == "Pasif": continue
                tum_kullanicilar.append({"id": u_snap.id, "data": u_d, "email": u_em})

            # Arama filtresi
            if arama_input.strip():
                arama_lower = arama_input.strip().lower()
                tum_kullanicilar.sort(key=lambda x: (0 if x["data"].get("isim", "").lower() == arama_lower else (1 if arama_lower in x["data"].get("isim", "").lower() else 2)))

            # Mevcut arkadaşlık verileri
            my_arkadaslar = user_doc.get("arkadaslar", [])
            my_takip_ettiklerim = user_doc.get("takip_ettiklerim", [])
            gonderilen_istekler = user_doc.get("gonderilen_arkadaslik_istekleri", [])

            for idx, kisi in enumerate(tum_kullanicilar):
                k_data = kisi["data"]
                k_id = kisi["id"]
                k_isim = k_data.get("isim", "Bilinmiyor")
                k_foto = k_data.get("profil_foto", "")
                k_color = k_data.get("isim_rengi", "#FFFFFF")
                k_glow = k_data.get("ismin_parlakligi", False)
                k_tag = k_data.get("tag", "")
                k_rozet = k_data.get("rozet", "")
                
                k_email_clean = kisi.get("email", "").strip().lower()
                if k_email_clean == KURUCU_EMAIL:
                    if not k_tag:
                        k_color = "#FF0000"
                        k_glow = True
                        k_tag = "KURUCU"
                        k_rozet = "🛠️"
                elif k_data.get("is_admin", False):
                    if not k_tag:
                        k_color = "#9b59b6"
                        k_glow = False
                        k_tag = "YÖNETİCİ"
                        k_rozet = "🛡️"

                k_styled = get_styled_user_name(k_isim, k_color, k_glow, k_tag, k_rozet, email=k_email_clean, is_admin=k_data.get("is_admin", False))

                if k_foto:
                    k_foto_src = f"data:image/jpeg;base64,{k_foto}"
                else:
                    k_foto_src = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

                k_friends_count = len(k_data.get("arkadaslar", []))
                k_followers_count = len(k_data.get("takipciler", []))

                with st.container(border=True):
                    col_av, col_name, col_acts = st.columns([1, 4, 3])
                    with col_av:
                        st.markdown(f'<img src="{k_foto_src}" style="width:40px;height:40px;border-radius:50%;object-fit:cover;"/>', unsafe_allow_html=True)
                    with col_name:
                        st.markdown(f"{k_styled}", unsafe_allow_html=True)
                        st.caption(f"👥 Arkadaş: **{k_friends_count}** | 👁️ Takipçi: **{k_followers_count}**")
                    with col_acts:
                        # Arkadaşlık durumu
                        if k_id in my_arkadaslar:
                            st.markdown("✅ Arkadaş", unsafe_allow_html=True)
                        elif k_id in gonderilen_istekler:
                            st.markdown("⏳ İstek Gönderildi", unsafe_allow_html=True)
                        else:
                            if st.button("➕ Arkadaş Ekle", key=f"ark_ekle_{k_id}_{idx}", use_container_width=True):
                                if len(my_arkadaslar) >= 300:
                                    st.error("Maksimum arkadaş limitine (300) ulaştınız!")
                                elif k_friends_count >= 300:
                                    st.error("Bu kullanıcının arkadaş limiti dolu! (Maksimum 300)")
                                else:
                                    # Gönderen tarafta kaydet
                                    user_ref.update({"gonderilen_arkadaslik_istekleri": firestore.ArrayUnion([k_id])})
                                    # Alıcı tarafta bildirim oluştur
                                    db.collection("users").document(k_id).update({
                                        "gelen_arkadaslik_istekleri": firestore.ArrayUnion([uid])
                                    })
                                    st.success(f"'{k_isim}' kişisine arkadaşlık isteği gönderildi!")
                                    st.rerun()

                        # Takip butonu
                        if k_id in my_takip_ettiklerim:
                            if st.button("🚫 Takipten Çık", key=f"takipten_cik_{k_id}_{idx}", use_container_width=True):
                                user_ref.update({"takip_ettiklerim": firestore.ArrayRemove([k_id])})
                                db.collection("users").document(k_id).update({
                                    "takipciler": firestore.ArrayRemove([uid])
                                })
                                st.success(f"'{k_isim}' takipten çıkarıldı!")
                                st.rerun()
                        else:
                            if st.button("👁️ Takip Et", key=f"takip_{k_id}_{idx}", use_container_width=True):
                                user_ref.update({"takip_ettiklerim": firestore.ArrayUnion([k_id])})
                                db.collection("users").document(k_id).update({
                                    "takipciler": firestore.ArrayUnion([uid])
                                })
                                st.success(f"'{k_isim}' takip edildi!")
                                st.rerun()

                    # "Hesabına Bak" tuşu - Expander ile açılan detaylı profil penceresi (Bug 4)
                    with st.expander(f"🔍 Hesabına Bak ({k_isim})"):
                        st.markdown(f"### 👤 {k_styled}", unsafe_allow_html=True)
                        st.write("---")
                        
                        _k_friends = k_data.get("arkadaslar", [])
                        _k_following = k_data.get("takip_ettiklerim", [])
                        _k_followers = k_data.get("takipciler", [])
                        
                        st.markdown(f"🎯 **Takip Ettiği Kişi Sayısı:** `{len(_k_following)}`")
                        if st.button("👉 Takip Ettiği Kişileri Gör", key=f"detay_following_{k_id}_{idx}", use_container_width=True):
                            st.session_state.sosyal_detay_user_id = k_id
                            st.session_state.sosyal_detay_user_name = k_isim
                            st.session_state.sosyal_detay_type = "takip_ettiklerim"
                            st.session_state.sosyal_detay_return_page = "arkadas_ara"
                            st.session_state.current_page = "sosyal_detay"
                            st.rerun()

                        st.markdown(f"📈 **Takipçi Sayısı:** `{len(_k_followers)}`")
                        if st.button("👥 Takipçileri Gör", key=f"detay_followers_{k_id}_{idx}", use_container_width=True):
                            st.session_state.sosyal_detay_user_id = k_id
                            st.session_state.sosyal_detay_user_name = k_isim
                            st.session_state.sosyal_detay_type = "takipciler"
                            st.session_state.sosyal_detay_return_page = "arkadas_ara"
                            st.session_state.current_page = "sosyal_detay"
                            st.rerun()

                        st.markdown(f"🤝 **Arkadaş Sayısı:** `{len(_k_friends)}`")
                        if st.button("🤝 Arkadaşları Gör", key=f"detay_friends_{k_id}_{idx}", use_container_width=True):
                            st.session_state.sosyal_detay_user_id = k_id
                            st.session_state.sosyal_detay_user_name = k_isim
                            st.session_state.sosyal_detay_type = "arkadaslar"
                            st.session_state.sosyal_detay_return_page = "arkadas_ara"
                            st.session_state.current_page = "sosyal_detay"
                            st.rerun()

        # ═══════════════════════════════════════════════════
        # 👤 HESABIM SAYFASI
        # ═══════════════════════════════════════════════════
        elif st.session_state.current_page == "hesabim":
            st.title("👤 Hesabım")
            if st.button("← Sohbete Dön", key="hesabim_geri_btn", use_container_width=True):
                st.session_state.current_page = "chat"
                st.rerun()

            st.divider()

            # Profil bilgileri
            hesap_foto = user_doc.get("profil_foto", "")
            if hesap_foto:
                h_foto_src = f"data:image/jpeg;base64,{hesap_foto}"
            else:
                h_foto_src = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
            st.markdown(f'<div style="text-align:center;"><img src="{h_foto_src}" style="width:80px;height:80px;border-radius:50%;object-fit:cover;border:2px solid #f39c12;"/></div>', unsafe_allow_html=True)

            h_isim_stili = get_styled_user_name(kullanici_ismi, u_color, u_glow, u_tag, u_rozet, email=email, is_admin=is_admin_user)
            st.markdown(f"<div style='text-align:center; margin-top:8px;'>{h_isim_stili}</div>", unsafe_allow_html=True)

            st.divider()

            # Arkadaş listesi
            arkadaslarim = user_doc.get("arkadaslar", [])
            st.markdown(f"### 👥 Arkadaşlarım ({len(arkadaslarim)})")
            if arkadaslarim:
                for ark_id in arkadaslarim:
                    try:
                        ark_snap = db.collection("users").document(ark_id).get()
                        if ark_snap.exists:
                            ark_d = ark_snap.to_dict()
                            ark_isim = ark_d.get("isim", "Bilinmiyor")
                            ark_foto = ark_d.get("profil_foto", "")
                            ark_color = ark_d.get("isim_rengi", "#FFFFFF")
                            ark_glow = ark_d.get("ismin_parlakligi", False)
                            ark_tag = ark_d.get("tag", "")
                            ark_rozet = ark_d.get("rozet", "")
                            
                            ark_email = ark_d.get("email", "").strip().lower()
                            if ark_email == KURUCU_EMAIL:
                                if not ark_tag:
                                    ark_color = "#FF0000"
                                    ark_glow = True
                                    ark_tag = "KURUCU"
                                    ark_rozet = "🛠️"
                            elif ark_d.get("is_admin", False):
                                if not ark_tag:
                                    ark_color = "#9b59b6"
                                    ark_glow = False
                                    ark_tag = "YÖNETİCİ"
                                    ark_rozet = "🛡️"

                            ark_styled = get_styled_user_name(ark_isim, ark_color, ark_glow, ark_tag, ark_rozet, email=ark_d.get("email"), is_admin=ark_d.get("is_admin", False))
                            ark_foto_src = f"data:image/jpeg;base64,{ark_foto}" if ark_foto else "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
                            col_af, col_an, col_dm, col_rem = st.columns([1, 4, 3, 2.5])
                            with col_af:
                                st.markdown(f'<img src="{ark_foto_src}" style="width:30px;height:30px;border-radius:50%;object-fit:cover;"/>', unsafe_allow_html=True)
                            with col_an:
                                st.markdown(ark_styled, unsafe_allow_html=True)
                            with col_dm:
                                if st.button("💬 Sohbet Et", key=f"dm_to_{ark_id}", use_container_width=True):
                                    st.session_state.dm_partner_id = ark_id
                                    st.session_state.current_page = "dm_chat"
                                    st.rerun()
                            with col_rem:
                                if st.button("❌ Çıkar", key=f"ark_rem_btn_{ark_id}", use_container_width=True):
                                    user_ref.update({"arkadaslar": firestore.ArrayRemove([ark_id])})
                                    db.collection("users").document(ark_id).update({
                                        "arkadaslar": firestore.ArrayRemove([uid])
                                    })
                                    st.success(f"{ark_isim} arkadaşlıktan çıkarıldı!")
                                    st.rerun()
                    except Exception:
                        pass
            else:
                st.caption("Henüz arkadaşınız yok.")

            st.divider()

            # Takipçi bilgisi
            takipcilerim = user_doc.get("takipciler", [])
            takip_ettiklerim = user_doc.get("takip_ettiklerim", [])
            st.markdown(f"### 👁️ Takipçi: {len(takipcilerim)} | Takip: {len(takip_ettiklerim)}")

        # ═══════════════════════════════════════════════════
        # 👥 SOSYAL DETAY PAGED VIEW
        # ═══════════════════════════════════════════════════
        elif st.session_state.current_page == "sosyal_detay":
            st.title("👥 Sosyal Bilgiler")
            
            t_return = st.session_state.get("sosyal_detay_return_page", "arkadas_ara")
            if st.button("← Geri Dön", key="sosyal_detay_back_btn", use_container_width=True):
                st.session_state.current_page = t_return
                st.rerun()

            st.divider()

            t_uid = st.session_state.get("sosyal_detay_user_id")
            t_name = st.session_state.get("sosyal_detay_user_name", "Kullanıcı")
            t_type = st.session_state.get("sosyal_detay_type", "arkadaslar")

            if t_uid:
                try:
                    t_doc_ref = db.collection("users").document(t_uid)
                    t_doc_snap = t_doc_ref.get()
                    if t_doc_snap.exists:
                        t_data = t_doc_snap.to_dict()
                        ids_list = t_data.get(t_type, [])

                        if t_type == "takip_ettiklerim":
                            heading_text = f"👉 {t_name} Tarafından Takip Edilenler ({len(ids_list)})"
                        elif t_type == "takipciler":
                            heading_text = f"📈 {t_name} Takipçileri ({len(ids_list)})"
                        else:
                            heading_text = f"🤝 {t_name} Arkadaşları ({len(ids_list)})"

                        st.markdown(f"### {heading_text}")
                        st.write("---")

                        if not ids_list:
                            st.info("Herhangi bir kullanıcı bulunamadı.")
                        else:
                            count_rendered = 0
                            for list_uid in ids_list:
                                if count_rendered >= 200:
                                    st.warning("⚠️ Sadece ilk 200 kullanıcı listelenmektedir.")
                                    break
                                try:
                                    sub_snap = db.collection("users").document(list_uid).get()
                                    if sub_snap.exists:
                                        sub_data = sub_snap.to_dict()
                                        sub_isim = sub_data.get("isim", "Bilinmeyen")
                                        sub_color = sub_data.get("isim_rengi", "#FFFFFF")
                                        sub_glow = sub_data.get("ismin_parlakligi", False)
                                        sub_tag = sub_data.get("tag", "")
                                        sub_rozet = sub_data.get("rozet", "")

                                        sub_email = sub_data.get("email", "").strip().lower()
                                        if sub_email == KURUCU_EMAIL:
                                            if not sub_tag:
                                                sub_color = "#FF0000"
                                                sub_glow = True
                                                sub_tag = "KURUCU"
                                                sub_rozet = "🛠️"
                                        elif sub_data.get("is_admin", False):
                                            if not sub_tag:
                                                sub_color = "#9b59b6"
                                                sub_glow = False
                                                sub_tag = "YÖNETİCİ"
                                                sub_rozet = "🛡️"

                                        sub_styled_name = get_styled_user_name(sub_isim, sub_color, sub_glow, sub_tag, sub_rozet, email=sub_data.get("email"), is_admin=sub_data.get("is_admin", False))
                                        sub_foto = sub_data.get("profil_foto", "")
                                        sub_foto_src = f"data:image/jpeg;base64,{sub_foto}" if sub_foto else "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

                                        with st.container(border=True):
                                            col_f, col_n = st.columns([1, 9])
                                            with col_f:
                                                st.markdown(f'<img src="{sub_foto_src}" style="width:40px;height:40px;border-radius:50%;object-fit:cover;"/>', unsafe_allow_html=True)
                                            with col_n:
                                                st.markdown(f"{sub_styled_name}", unsafe_allow_html=True)
                                        count_rendered += 1
                                except Exception:
                                    pass
                    else:
                        st.error("Kullanıcı kaydı bulunamadı.")
                except Exception as e:
                    st.error(f"Bilgiler alınırken hata oluştu: {e}")
            else:
                st.error("Lütfen geçerli bir profil seçin.")

        # ═══════════════════════════════════════════════════
        # 💬 DM INBOX SAYFASI
        # ═══════════════════════════════════════════════════
        elif st.session_state.current_page == "dm_inbox":
            st.title("💬 Mesajlarım")
            if st.button("← Sohbete Dön", key="dm_inbox_geri_btn", use_container_width=True):
                st.session_state.current_page = "chat"
                st.rerun()

            st.divider()

            arkadaslarim_dm = user_doc.get("arkadaslar", [])
            if not arkadaslarim_dm:
                st.info("Henüz arkadaşınız yok. Arkadaş ekleyerek DM gönderebilirsiniz.")
            else:
                st.markdown("### Arkadaşlarınız ile sohbet başlatın:")
                for ark_id_dm in arkadaslarim_dm:
                    try:
                        ark_snap_dm = db.collection("users").document(ark_id_dm).get()
                        if ark_snap_dm.exists:
                            ark_d_dm = ark_snap_dm.to_dict()
                            ark_isim_dm = ark_d_dm.get("isim", "Bilinmiyor")
                            ark_foto_dm = ark_d_dm.get("profil_foto", "")
                            ark_foto_src_dm = f"data:image/jpeg;base64,{ark_foto_dm}" if ark_foto_dm else "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
                            with st.container(border=True):
                                col_dmf, col_dmn, col_dmb = st.columns([1, 4, 2])
                                with col_dmf:
                                    st.markdown(f'<img src="{ark_foto_src_dm}" style="width:35px;height:35px;border-radius:50%;object-fit:cover;"/>', unsafe_allow_html=True)
                                with col_dmn:
                                    st.markdown(f"**{ark_isim_dm}**")
                                with col_dmb:
                                    if st.button("💬 Yaz", key=f"dm_start_{ark_id_dm}", use_container_width=True):
                                        st.session_state.dm_partner_id = ark_id_dm
                                        st.session_state.current_page = "dm_chat"
                                        st.rerun()
                    except Exception:
                        pass

        # ═══════════════════════════════════════════════════
        # 💬 DM CHAT SAYFASI (Bireysel sohbet)
        # ═══════════════════════════════════════════════════
        elif st.session_state.current_page == "dm_chat":
            if st.session_state.get("play_send_sound", False):
                # Play backup HTML audio element for 100% reliable native playback
                st.markdown('<audio autoplay style="display:none;"><source src="https://assets.mixkit.co/active_storage/sfx/1344/1344-84.wav" type="audio/wav"></audio>', unsafe_allow_html=True)
                # Pleasant synthetic wave blip sound using Web Audio API (instant and ultra reliable)
                st.components.v1.html("""
                <script>
                (function() {
                  try {
                    const playSend = () => {
                      try {
                        const ctx = new (window.AudioContext || window.webkitAudioContext)();
                        if (ctx.state === 'suspended') {
                          ctx.resume();
                        }
                        const osc = ctx.createOscillator();
                        const gain = ctx.createGain();
                        osc.type = 'sine';
                        osc.frequency.setValueAtTime(600, ctx.currentTime);
                        osc.frequency.exponentialRampToValueAtTime(1200, ctx.currentTime + 0.1);
                        gain.gain.setValueAtTime(0.08, ctx.currentTime);
                        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.12);
                        osc.connect(gain);
                        gain.connect(ctx.destination);
                        osc.start();
                        osc.stop(ctx.currentTime + 0.12);
                      } catch (err) {}
                    };
                    const ctxCheck = new (window.AudioContext || window.webkitAudioContext)();
                    if (ctxCheck.state === 'suspended') {
                      document.addEventListener('click', () => { playSend(); }, { once: true });
                    } else {
                      playSend();
                    }
                  } catch(e) {}
                })();
                </script>
                """, height=1, width=1)
                st.session_state.play_send_sound = False

            dm_partner_id = st.session_state.get("dm_partner_id", "")
            if not dm_partner_id:
                st.session_state.current_page = "dm_inbox"
                st.rerun()

            partner_snap = db.collection("users").document(dm_partner_id).get()
            if not partner_snap.exists:
                st.error("Kullanıcı bulunamadı.")
                st.session_state.current_page = "dm_inbox"
                st.rerun()

            partner_data = partner_snap.to_dict()
            partner_isim = partner_data.get("isim", "Bilinmiyor")
            partner_foto = partner_data.get("profil_foto", "")
            partner_foto_src = f"data:image/jpeg;base64,{partner_foto}" if partner_foto else "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

            partner_color = partner_data.get("isim_rengi", "#FFFFFF")
            partner_glow = partner_data.get("ismin_parlakligi", False)
            partner_tag = partner_data.get("tag", "")
            partner_rozet = partner_data.get("rozet", "")
            
            partner_email = partner_data.get("email", "").strip().lower()
            if partner_email == KURUCU_EMAIL:
                if not partner_tag:
                    partner_color = "#FF0000"
                    partner_glow = True
                    partner_tag = "KURUCU"
                    partner_rozet = "🛠️"

            # Check if they are admin but not kurucu
            partner_is_admin = partner_data.get("is_admin", False)
            if partner_is_admin and partner_email != KURUCU_EMAIL:
                if not partner_tag:
                    partner_tag = "ADMIN"
                    partner_rozet = "🛡️"

            partner_styled_name = get_styled_user_name(partner_isim, partner_color, partner_glow, partner_tag, partner_rozet, email=partner_email, is_admin=partner_is_admin)

            partner_online = False
            partner_son_gorulme = partner_data.get("son_gorulme_zamani")
            if hasattr(partner_son_gorulme, "to_datetime"):
                partner_son_gorulme = partner_son_gorulme.to_datetime()

            if partner_son_gorulme:
                if partner_son_gorulme.tzinfo is None:
                    partner_son_gorulme = partner_son_gorulme.replace(tzinfo=timezone.utc)
                now_utc = datetime.now(timezone.utc)
                diff = now_utc - partner_son_gorulme
                total_seconds = int(diff.total_seconds())
                if total_seconds < 0:
                    total_seconds = 0
                if total_seconds <= 300:
                    partner_online = True
                tr_offset = timezone(timedelta(hours=3))
                partner_last_seen_tr = partner_son_gorulme.astimezone(tr_offset)
                partner_last_seen_str = partner_last_seen_tr.strftime("%H:%M - %d.%m.%Y")
            else:
                partner_last_seen_str = "Bilinmiyor"

            status_indicator = "🟢 Çevrimiçi" if partner_online else f"🔴 Son Görülme: {partner_last_seen_str}"

            # Arkadaşlık kontrolü (kurucu/yönetici hariç)
            is_friend = dm_partner_id in user_doc.get("arkadaslar", [])
            if not is_friend and not is_kurucu and not is_admin_user:
                st.error("Bu kişiyle mesajlaşabilmek için arkadaş olmanız gerekiyor.")
                if st.button("← Geri", key="dm_not_friend_back"):
                    st.session_state.current_page = "dm_inbox"
                    st.rerun()
            else:
                col_dm_header, col_dm_back = st.columns([5, 1])
                with col_dm_header:
                    st.markdown(f'<div style="display:flex;align-items:center;gap:10px;"><img src="{partner_foto_src}" style="width:38px;height:38px;border-radius:50%;object-fit:cover;border:1px solid #f39c12;"/><div><div style="font-size:1.15rem;display:flex;align-items:center;gap:5px;">{partner_styled_name}</div><div style="font-size:0.75rem;color:#888;margin-top:2px;">{status_indicator}</div></div></div>', unsafe_allow_html=True)
                with col_dm_back:
                    if st.button("←", key="dm_chat_back_btn", use_container_width=True):
                        st.session_state.current_page = "dm_inbox"
                        st.rerun()

                st.divider()

                # DM konuşma ID'si (sıralı uid'lerle unique)
                dm_ids = sorted([uid, dm_partner_id])
                dm_conv_id = f"{dm_ids[0]}_{dm_ids[1]}"

                # Mesajları oku
                dm_doc_ref = db.collection("dm_konusmalar").document(dm_conv_id)
                dm_doc_snap = dm_doc_ref.get()
                dm_mesajlar = []
                if dm_doc_snap.exists:
                    dm_mesajlar = dm_doc_snap.to_dict().get("mesajlar", [])

                # Track message count to play receive double-blip sound
                msg_count_key = f"prev_msg_count_{dm_conv_id}"
                prev_count = st.session_state.get(msg_count_key, None)
                current_count = len(dm_mesajlar)
                
                play_receive_sound = False
                if prev_count is not None and current_count > prev_count:
                    # Check if any new message was sent by the partner
                    new_msgs = dm_mesajlar[prev_count:]
                    if any(m.get("gonderen") != uid for m in new_msgs):
                        play_receive_sound = True
                
                # Update saved count
                st.session_state[msg_count_key] = current_count
                
                if play_receive_sound:
                    # Play backup HTML audio element for 100% reliable native playback (double-ping sound)
                    st.markdown('<audio autoplay style="display:none;"><source src="https://assets.mixkit.co/active_storage/sfx/1359/1359-84.wav" type="audio/wav"></audio>', unsafe_allow_html=True)
                    # Pleasant synthetic double blip using Web Audio API
                    st.components.v1.html("""
                    <script>
                    (function() {
                      try {
                        const playReceive = () => {
                          try {
                            const ctx = new (window.AudioContext || window.webkitAudioContext)();
                            if (ctx.state === 'suspended') {
                              ctx.resume();
                            }
                            const osc1 = ctx.createOscillator();
                            const gain1 = ctx.createGain();
                            osc1.type = 'sine';
                            osc1.frequency.setValueAtTime(800, ctx.currentTime);
                            gain1.gain.setValueAtTime(0.08, ctx.currentTime);
                            gain1.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.08);
                            osc1.connect(gain1);
                            gain1.connect(ctx.destination);
                            osc1.start();
                            osc1.stop(ctx.currentTime + 0.08);

                            setTimeout(() => {
                              try {
                                const osc2 = ctx.createOscillator();
                                const gain2 = ctx.createGain();
                                osc2.type = 'sine';
                                osc2.frequency.setValueAtTime(1000, ctx.currentTime);
                                gain2.gain.setValueAtTime(0.08, ctx.currentTime);
                                gain2.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.1);
                                osc2.connect(gain2);
                                gain2.connect(ctx.destination);
                                osc2.start();
                                osc2.stop(ctx.currentTime + 0.1);
                              } catch (e) {}
                            }, 80);
                          } catch(err) {}
                        };
                        const ctxCheck = new (window.AudioContext || window.webkitAudioContext)();
                        if (ctxCheck.state === 'suspended') {
                          document.addEventListener('click', () => { playReceive(); }, { once: true });
                        } else {
                          playReceive();
                        }
                      } catch(e) {}
                    })();
                    </script>
                    """, height=1, width=1)

                # Mesajları göster
                dm_container = st.container(height=400)
                
                # Current user styles
                user_doc_fresh_dm = user_ref.get().to_dict()
                u_color_fresh_dm = user_doc_fresh_dm.get("isim_rengi", "#FFFFFF")
                u_glow_fresh_dm = user_doc_fresh_dm.get("ismin_parlakligi", False)
                u_tag_fresh_dm = user_doc_fresh_dm.get("tag", "")
                u_rozet_fresh_dm = user_doc_fresh_dm.get("rozet", "")
                _user_foto_dm = user_doc_fresh_dm.get("profil_foto", "")
                _user_avatar_url_dm = f"data:image/jpeg;base64,{_user_foto_dm}" if _user_foto_dm else USER_AVATAR

                if is_kurucu:
                    if not user_doc_fresh_dm.get("tag"):
                        u_color_fresh_dm = "#FF0000"
                        u_glow_fresh_dm = True
                        u_rozet_fresh_dm = "🛠️"
                        u_tag_fresh_dm = "KURUCU"

                display_name_dm = get_styled_user_name(user_doc_fresh_dm.get('isim', kullanici_ismi), u_color_fresh_dm, u_glow_fresh_dm, u_tag_fresh_dm, u_rozet_fresh_dm, email=email, is_admin=is_admin_user)

                with dm_container:
                    if not dm_mesajlar:
                        st.info("Sohbete başla! İlk mesajını gönder.")
                    else:
                        st.markdown("""
                        <style>
                        .dm-chat-box-container p { margin: 0 !important; padding: 0 !important; }
                        .dm-delete-anchor ~ div[data-testid="stButton"] {
                            display: flex !important;
                            justify-content: center !important;
                            align-items: center !important;
                            width: 100% !important;
                        }
                        .dm-delete-anchor ~ div[data-testid="stButton"] button {
                            background: #e74c3c !important;
                            border: none !important;
                            border-radius: 50% !important;
                            color: #ffffff !important;
                            font-size: 13px !important;
                            display: flex !important;
                            align-items: center !important;
                            justify-content: center !important;
                            width: 26px !important;
                            height: 26px !important;
                            min-width: 26px !important;
                            min-height: 26px !important;
                            max-width: 26px !important;
                            max-height: 26px !important;
                            margin: 4px auto 0 auto !important;
                            padding: 0 !important;
                            cursor: pointer !important;
                            box-shadow: 0 1px 3px rgba(0,0,0,0.3) !important;
                            transition: all 0.2s ease !important;
                        }
                        .dm-delete-anchor ~ div[data-testid="stButton"] button:hover {
                            background: #c0392b !important;
                            transform: scale(1.1) !important;
                            color: #ffffff !important;
                        }
                        .dm-delete-anchor ~ div[data-testid="stButton"] button p,
                        .dm-delete-anchor ~ div[data-testid="stButton"] button * {
                            color: #ffffff !important;
                            font-size: 13px !important;
                            margin: 0 !important;
                            padding: 0 !important;
                            display: flex !important;
                            align-items: center !important;
                            justify-content: center !important;
                        }
                        </style>
                        """, unsafe_allow_html=True)
                        for idx, dm_msg in enumerate(dm_mesajlar):
                            dm_sender = dm_msg.get("gonderen", "")
                            dm_content = dm_msg.get("icerik", "")
                            dm_type = dm_msg.get("tip", "text")
                            dm_zaman = dm_msg.get("zaman", "")
                            is_deleted = dm_msg.get("silindi", False) or dm_content == "Mesaj Silindi"

                            if is_deleted:
                                continue

                            if dm_sender == uid:
                                s_foto_src = _user_avatar_url_dm
                                s_styled = display_name_dm
                                align = "right"
                                bg_color = "rgba(243,156,18,0.2)"
                                flex_dir = "row-reverse"
                                align_items_inner = "flex-end"
                            else:
                                s_foto_src = partner_foto_src
                                s_styled = partner_styled_name
                                align = "left"
                                bg_color = "rgba(255,255,255,0.05)"
                                flex_dir = "row"
                                align_items_inner = "flex-start"

                            if dm_type == "gif":
                                dm_html = f'<img src="{dm_content}" style="max-width:200px;border-radius:8px;" referrerPolicy="no-referrer"/>'
                            elif dm_type == "voice":
                                dm_html = f'<audio controls src="data:audio/webm;base64,{dm_content}" style="width:100%; max-width:240px; display:block; margin-top:5px; height:40px; outline:none;"></audio>'
                            else:
                                dm_html = detect_and_render_media(dm_content)

                            is_voice = (dm_type == "voice")
                            bubble_width_css = "width: 260px;" if is_voice else "width: fit-content;"
                            voice_padding_css = "padding: 6px 10px;" if is_voice else "padding: 8px 12px;"

                            msg_bubble = (
                                f'<div style="display:flex; flex-direction:column; align-items:{align_items_inner}; max-width:100%;">'
                                f'<div style="font-size:0.75rem; color:#ccc; margin-bottom:2px; text-align:{align};">{s_styled}</div>'
                                f'<div style="background:{bg_color}; {voice_padding_css} border-radius:10px; font-size:0.9rem; white-space:pre-wrap; word-break:break-word; {bubble_width_css} max-width:100%; box-sizing:border-box; box-shadow: 0 1px 2px rgba(0,0,0,0.15);">'
                                f'{dm_html}'
                                f'<div style="font-size:0.65em; color:#888; margin-top:3px; text-align:{align};">{dm_zaman}</div>'
                                f'</div></div>'
                            )

                            if flex_dir == "row-reverse":
                                col_msg, col_side = st.columns([11, 1])
                                with col_msg:
                                    st.markdown(msg_bubble, unsafe_allow_html=True)
                                with col_side:
                                    st.markdown(f'<img src="{s_foto_src}" style="width:30px;height:30px;border-radius:50%;object-fit:cover;border:1px solid #f39c12;display:block;margin:2px auto 0 auto;flex-shrink:0;"/>', unsafe_allow_html=True)
                                    st.markdown('<div class="dm-delete-anchor"></div>', unsafe_allow_html=True)
                                    if st.button("🗑️", key=f"del_dm_{dm_conv_id}_{idx}", help="Mesajı sil"):
                                        try:
                                            doc_snap = dm_doc_ref.get()
                                            if doc_snap.exists:
                                                current_messages = doc_snap.to_dict().get("mesajlar", [])
                                                if idx < len(current_messages):
                                                    current_messages[idx]["icerik"] = "Mesaj Silindi"
                                                    current_messages[idx]["silindi"] = True
                                                    dm_doc_ref.update({"mesajlar": current_messages})
                                                    st.rerun()
                                        except Exception as e:
                                            st.error(f"Hata: {e}")
                            else:
                                col_side, col_msg = st.columns([1, 11])
                                with col_side:
                                    st.markdown(f'<img src="{s_foto_src}" style="width:30px;height:30px;border-radius:50%;object-fit:cover;border:1px solid #f39c12;display:block;margin:2px auto 0 auto;flex-shrink:0;"/>', unsafe_allow_html=True)
                                    st.markdown('<div class="dm-delete-anchor"></div>', unsafe_allow_html=True)
                                    if st.button("🗑️", key=f"del_dm_{dm_conv_id}_{idx}", help="Mesajı sil"):
                                        try:
                                            doc_snap = dm_doc_ref.get()
                                            if doc_snap.exists:
                                                current_messages = doc_snap.to_dict().get("mesajlar", [])
                                                if idx < len(current_messages):
                                                    current_messages[idx]["icerik"] = "Mesaj Silindi"
                                                    current_messages[idx]["silindi"] = True
                                                    dm_doc_ref.update({"mesajlar": current_messages})
                                                    st.rerun()
                                        except Exception as e:
                                            st.error(f"Hata: {e}")
                                with col_msg:
                                    st.markdown(msg_bubble, unsafe_allow_html=True)

                # Mesaj gönderme
                st.markdown("---")
                if "dm_input_key" not in st.session_state: st.session_state.dm_input_key = 0
                current_dm_inp_key = f"dm_text_form_{st.session_state.get('dm_input_key', 0)}"

                with st.form(key=current_dm_inp_key, clear_on_submit=True):
                    col_dm_input, col_dm_send = st.columns([5, 1.2])
                    with col_dm_input:
                        dm_yeni_mesaj = st.text_input("Mesaj yaz...", label_visibility="collapsed", placeholder="Mesajınız...")
                    with col_dm_send:
                        send_clicked = st.form_submit_button("📤 Gönder", use_container_width=True)
                    
                    if send_clicked:
                        if dm_yeni_mesaj.strip():
                            st.session_state.play_send_sound = True
                            zaman_str = get_tr_time().strftime("%H:%M")
                            yeni_dm = {
                                "gonderen": uid,
                                "icerik": dm_yeni_mesaj.strip(),
                                "tip": "text",
                                "zaman": zaman_str
                            }
                            dm_doc_ref.set({"mesajlar": firestore.ArrayUnion([yeni_dm])}, merge=True)
                            st.session_state.dm_input_key = st.session_state.get("dm_input_key", 0) + 1
                            st.rerun()

        # ═══════════════════════════════════════════════════
        # ✉️ ADMIN MESAJ GÖNDERİMİ SAYFASI
        # ═══════════════════════════════════════════════════
        elif st.session_state.current_page == "admin_mesaj" and (is_kurucu or is_admin_user):
            st.title("✉️ Kullanıcıya Mesaj Gönder")
            col_ab1, col_ab2 = st.columns(2)
            with col_ab1:
                if st.button("← Panele Dön", key="admin_mesaj_back", use_container_width=True):
                    st.session_state.current_page = "admin_main" if is_kurucu else "chat"
                    st.rerun()
            with col_ab2:
                if st.button("💬 Sohbete Dön", key="admin_mesaj_chat_back", use_container_width=True):
                    st.session_state.current_page = "chat"
                    st.rerun()

            st.divider()
            admin_mesaj_email = st.text_input("📧 Kullanıcı E-postası:", key="admin_mesaj_email_input", placeholder="E-posta yazın...")
            admin_mesaj_icerik = st.text_area("✍️ Mesajınız:", key="admin_mesaj_icerik_input", placeholder="Göndermek istediğiniz mesajı yazın...")

            if st.button("📤 Mesajı Gönder", key="admin_mesaj_gonder_btn", type="primary", use_container_width=True):
                if not admin_mesaj_email.strip() or not admin_mesaj_icerik.strip():
                    st.warning("⚠️ E-posta ve mesaj alanları boş bırakılamaz.")
                else:
                    # Kullanıcıyı bul
                    hedef_users = db.collection("users").where("email", "==", admin_mesaj_email.strip().lower()).limit(1).get()
                    if not hedef_users:
                        st.error("❌ Bu e-posta ile kayıtlı kullanıcı bulunamadı.")
                    else:
                        hedef_doc = hedef_users[0]
                        hedef_id = hedef_doc.id
                        gonderen_isim = kullanici_ismi
                        zaman_str = get_tr_time().strftime("%H:%M - %d.%m.%Y")
                        yetkili_mesaj = {
                            "id": str(uuid.uuid4()),
                            "gonderen_uid": uid,
                            "gonderen_isim": gonderen_isim,
                            "icerik": admin_mesaj_icerik.strip(),
                            "zaman": zaman_str,
                            "okundu": False
                        }
                        db.collection("users").document(hedef_id).update({
                            "yetkili_mesajlari": firestore.ArrayUnion([yetkili_mesaj])
                        })
                        st.success(f"✅ Mesaj başarıyla '{hedef_doc.to_dict().get('isim', 'Kullanıcı')}' kişisine gönderildi!")

        # ═══════════════════════════════════════════════════
        # 🎬 YOUTUBE PORTAL SAYFASI
        # ═══════════════════════════════════════════════════
        elif st.session_state.current_page == "youtube_portal":
            yt_saved = user_ref.get().to_dict().get("videos", [])

            _qp = st.query_params
            _qp_vid = _qp.get("ytv", "")
            _qp_ts  = int(_qp.get("ytt", "0") or "0")
            if _qp_vid:
                _qp_vid_safe = re.sub(r'[^a-zA-Z0-9_\-]', '', _qp_vid)
                if _qp_vid_safe:
                    if _qp_ts > 0:
                        st.session_state.yt_ts_dict[_qp_vid_safe] = _qp_ts
                    
                    st.session_state.yt_playing_id      = _qp_vid_safe
                    st.session_state.yt_playing_title   = st.session_state.get("yt_last_title", _qp_vid_safe)
                    st.session_state.yt_playing_channel = st.session_state.get("yt_last_channel", "")
                    st.session_state.yt_iframe_vid      = _qp_vid_safe
                    st.session_state.yt_iframe_mounted = False
                    st.session_state.global_player_rendered = False  # 🔥 YENİ VİDEO İÇİN SIFIRLA
                    st.query_params.clear()
                    st.rerun()

            # ─── HEADER ───────────────────────────────────────────────
            _yh1, _yh2 = st.columns([7, 1])
            with _yh1:
                st.markdown("""
    <div style="display:flex;align-items:center;gap:14px;padding:6px 0 2px;">
      <div style="background:#FF0000;border-radius:10px;width:46px;height:32px;display:flex;align-items:center;justify-content:center;flex-shrink:0;">
        <span style="color:#fff;font-size:1.1rem;font-weight:900;">▶</span>
      </div>
      <div>
        <div style="font-size:1.6rem;font-weight:800;color:#fff;letter-spacing:-0.5px;line-height:1.1;">YouTube Portalı</div>
        <div style="font-size:0.78rem;color:#777;margin-top:1px;">Kaplan Parçası · Gömülü Oynatıcı & Arama</div>
        """ + (f"<div style='font-size:0.7rem;color:#f39c12;margin-top:2px;'>▶ Şu an çalan: {st.session_state.yt_playing_title[:40]}{'...' if len(st.session_state.yt_playing_title)>40 else ''}</div>" if st.session_state.get("yt_playing_id") else "") + """
      </div>
    </div>""", unsafe_allow_html=True)
            with _yh2:
                st.write("")
                if st.button("← Geri", use_container_width=True, key="yt_geri_btn"):
                    if st.session_state.yt_playing_id:
                        st.session_state.yt_last_id      = re.sub(r'[^a-zA-Z0-9_\-]', '', st.session_state.yt_playing_id)
                        st.session_state.yt_last_title   = st.session_state.yt_playing_title
                        st.session_state.yt_last_channel = st.session_state.get("yt_playing_channel", "")
                    st.session_state.current_page = "chat"
                    st.session_state.yt_results   = []
                    st.session_state.yt_iframe_mounted = False
                    st.rerun()

            st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.08);margin:10px 0 14px;'>", unsafe_allow_html=True)

            # ─── ARAMA ÇUBUĞU ─────────────────────────────────────────
            _sch_c, _btn_c = st.columns([6, 1])
            with _sch_c:
                _yt_q = st.text_input(
                    "", placeholder="🔍 Ara: müzik, haber, belgesel, eğitim...",
                    label_visibility="collapsed", key="yt_search_q"
                )
            with _btn_c:
                _yt_go = st.button("🔍 Ara", use_container_width=True, key="yt_ara_btn")

            if _yt_go and _yt_q and _yt_q.strip():
                with st.spinner("🔄 YouTube'da aranıyor..."):
                    _ysonuc = youtube_ara(_yt_q.strip(), max_sonuc=12)
                    if _ysonuc:
                        st.session_state.yt_results = _ysonuc
                    else:
                        st.warning("⚠️ Sonuç bulunamadı.")

            # ─── OYNATICI MODU ─────────────────────────────────────────
            if st.session_state.yt_playing_id:
                _safe_vid = re.sub(r'[^a-zA-Z0-9_\-]', '', st.session_state.yt_playing_id)
                _ptitle   = st.session_state.yt_playing_title
                _pch      = st.session_state.get("yt_playing_channel", "")

                _pb1, _pb2, _pb3 = st.columns([3, 2, 2])
                with _pb1:
                    if st.button("← Sonuçlara Dön", key="yt_geri_sonuc"):
                        st.session_state.yt_last_id      = _safe_vid
                        st.session_state.yt_last_title   = _ptitle
                        st.session_state.yt_last_channel = _pch
                        st.session_state.yt_playing_id   = None
                        st.session_state.yt_iframe_mounted = False
                        st.rerun()
                with _pb2:
                    if _safe_vid not in yt_saved:
                        if st.button("📌 Kayıtlara Ekle", key="yt_kaydet_btn", use_container_width=True):
                            current_videos = user_ref.get().to_dict().get("videos", [])
                            if _safe_vid not in current_videos:
                                current_videos.append(_safe_vid)
                                user_ref.update({"videos": current_videos})
                            st.rerun()
                    else:
                        if st.button("🗑️ Kayıttan Çıkar", key="yt_kaydet_sil", use_container_width=True):
                            current_videos = user_ref.get().to_dict().get("videos", [])
                            if _safe_vid in current_videos:
                                current_videos.remove(_safe_vid)
                                user_ref.update({"videos": current_videos})
                            st.rerun()
                with _pb3:
                    st.markdown(
                        f"<a href='https://youtu.be/{_safe_vid}' target='_blank' "
                        f"style='display:block;text-align:center;background:rgba(255,0,0,0.12);"
                        f"border:1px solid rgba(255,0,0,0.35);color:#ff6b6b;padding:5px 8px;"
                        f"border-radius:6px;text-decoration:none;font-size:0.82em;'>🔗 YouTube'da Aç</a>",
                        unsafe_allow_html=True
                    )

                if _ptitle:
                    st.markdown(f"""
    <div style="background:rgba(255,0,0,0.07);border-left:3px solid #FF0000;padding:10px 14px;border-radius:0 8px 8px 0;margin:10px 0;">
      <div style="font-weight:700;font-size:0.97em;color:#fff;line-height:1.4;">{_ptitle[:110]}{'...' if len(_ptitle)>110 else ''}</div>
      {f'<div style="font-size:0.8em;color:#aaa;margin-top:4px;">📺 {_pch}</div>' if _pch else ''}
    </div>""", unsafe_allow_html=True)

                # ─── PORTAL OYNATICI ANKRAJI ──
                # Asıl oynatıcı (sayfa değişince kaybolmayan kalıcı global oynatıcı)
                # bu kutunun üzerine sabitlenir. Sohbete dönülünce ankraj kalktığı için
                # oynatıcı gizlenir ama ses arka planda çalmaya devam eder.
                st.markdown(
                    "<div id='ap-portal-anchor' "
                    "style='width:100%;height:430px;border-radius:10px;background:#000;"
                    "position:sticky;top:0;z-index:99989;"
                    "display:flex;align-items:center;justify-content:center;color:#555;"
                    "font-size:0.9em;'>🎬 Oynatıcı yükleniyor...</div>"
                    "<div style='font-size:0.78em;color:#888;margin:8px 0 2px;'>"
                    "🔊 Ses için oynatıcıdaki <b>“Sesi Aç”</b> düğmesine bir kez dokun. "
                    "Sesi açtıktan sonra <b>← Geri</b> ile sohbete dönsen bile ses arka planda devam eder."
                    "</div>",
                    unsafe_allow_html=True,
                )

            # ─── ARAMA SONUÇLARI ──────────────────────────────────────
            if st.session_state.yt_results:
                st.markdown("---")
                st.markdown("### 📋 Arama Sonuçları")
                _yres = st.session_state.yt_results
                _COLS = 3
                for _ri in range(0, len(_yres), _COLS):
                    _rcols = st.columns(_COLS)
                    for _rj, _rcol in enumerate(_rcols):
                        _ridx = _ri + _rj
                        if _ridx >= len(_yres):
                            break
                        _rv      = _yres[_ridx]
                        _rid     = _rv.get("id", "")
                        _rtitle  = _rv.get("title", "")
                        _rch     = _rv.get("channel", "")
                        _rdur    = _rv.get("duration", "")
                        _rviews  = _rv.get("views", "")
                        _rthumb  = _rv.get("thumbnail", f"https://img.youtube.com/vi/{_rid}/mqdefault.jpg")
                        with _rcol:
                            _dur_badge = (
                                f'<div style="position:absolute;bottom:5px;right:6px;'
                                f'background:rgba(0,0,0,0.88);color:#fff;font-size:0.68em;'
                                f'padding:2px 6px;border-radius:4px;font-weight:700;">{_rdur}</div>'
                            ) if _rdur else ""
                            _views_line = (
                                f'<div style="font-size:0.71em;color:#666;margin-top:1px;">{_rviews}</div>'
                            ) if _rviews else ""
                            st.markdown(f"""
    <div style="background:linear-gradient(160deg,#1c1c2e 0%,#16213e 100%);
                border-radius:12px;overflow:hidden;margin-bottom:6px;
                border:1px solid rgba(255,255,255,0.07);
                box-shadow:0 4px 18px rgba(0,0,0,0.45);">
      <div style="position:relative;overflow:hidden;aspect-ratio:16/9;background:#111;">
        <img src="{_rthumb}" loading="lazy"
             style="width:100%;height:100%;object-fit:cover;"
             onerror="this.style.visibility='hidden'">
        {_dur_badge}
      </div>
      <div style="padding:9px 12px 7px;">
        <div style="font-size:0.84em;font-weight:700;line-height:1.4;color:#fff;
                    margin-bottom:4px;overflow:hidden;display:-webkit-box;
                    -webkit-line-clamp:2;-webkit-box-orient:vertical;">
          {_rtitle[:95]}{'...' if len(_rtitle)>95 else ''}
        </div>
        <div style="font-size:0.74em;color:#999;">{_rch}</div>
        {_views_line}
      </div>
    </div>""", unsafe_allow_html=True)
                            if st.button("▶ İzle", key=f"ytplay_{_rid}_{_ridx}", use_container_width=True):
                                st.session_state.yt_iframe_mounted = False
                                st.session_state.yt_iframe_vid = ""
                                st.session_state.yt_playing_id      = _rid
                                st.session_state.yt_playing_title   = _rtitle
                                st.session_state.yt_playing_channel = _rch
                                st.session_state.global_player_rendered = False  # 🔥 YENİ VİDEO İÇİN SIFIRLA
                                st.rerun()

            # ─── HOŞ GELDİN EKRANI ────────────────────────────────────
            elif not st.session_state.yt_results:
                if st.session_state.get("yt_last_id"):
                    _lid   = st.session_state.yt_last_id
                    _ltit  = st.session_state.yt_last_title or _lid
                    _lch   = st.session_state.get("yt_last_channel", "")
                    _lthumb = f"https://img.youtube.com/vi/{_lid}/mqdefault.jpg"
                    st.markdown("""
    <div style="font-size:0.82em;color:#f39c12;font-weight:600;margin-bottom:8px;">▶ Kaldığın Yerden Devam Et</div>""",
                        unsafe_allow_html=True)
                    _rc1, _rc2 = st.columns([3, 1])
                    with _rc1:
                        st.markdown(f"""
    <div style="background:rgba(255,165,0,0.07);border:1px solid rgba(255,165,0,0.25);border-radius:12px;overflow:hidden;display:flex;gap:12px;align-items:center;padding:10px;">
      <img src="{_lthumb}" style="width:100px;min-width:100px;border-radius:8px;object-fit:cover;" loading="lazy">
      <div>
        <div style="font-size:0.87em;font-weight:700;color:#fff;line-height:1.4;">{_ltit[:70]}{'...' if len(_ltit)>70 else ''}</div>
        {f'<div style="font-size:0.75em;color:#aaa;margin-top:3px;">{_lch}</div>' if _lch else ''}
        <div style="font-size:0.72em;color:#777;margin-top:4px;">localStorage ile pozisyon kaydedildi</div>
      </div>
    </div>""", unsafe_allow_html=True)
                    with _rc2:
                        if st.button("▶ Devam Et", key="yt_resume_btn", use_container_width=True):
                            st.session_state.yt_iframe_mounted = False
                            st.session_state.yt_iframe_vid = ""
                            st.session_state.yt_playing_id      = _lid
                            st.session_state.yt_playing_title   = _ltit
                            st.session_state.yt_playing_channel = _lch
                            st.session_state.global_player_rendered = False  # 🔥 YENİ VİDEO İÇİN SIFIRLA
                            st.rerun()
                    st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)

                st.markdown("""
    <div style="text-align:center;padding:32px 20px 24px;">
      <div style="font-size:3.5rem;margin-bottom:14px;opacity:0.6;">🎬</div>
      <div style="font-size:1.05rem;color:#888;margin-bottom:6px;font-weight:600;">YouTube'da bir şeyler ara</div>
      <div style="font-size:0.83rem;color:#555;">Müzik · Haber · Belgesel · Eğitim · Eğlence</div>
    </div>""", unsafe_allow_html=True)

            # ─── KAYITLI VİDEOLAR ─────────────────────────────────────
            if yt_saved:
                st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.08);margin:16px 0 12px;'>", unsafe_allow_html=True)
                st.markdown("### 📌 Kayıtlı Videolar")
                _SV_COLS = 3
                for _svi in range(0, len(yt_saved), _SV_COLS):
                    _sv_row = st.columns(_SV_COLS)
                    for _svj, _svc in enumerate(_sv_row):
                        _svidx = _svi + _svj
                        if _svidx >= len(yt_saved):
                            break
                        _svraw = yt_saved[_svidx]
                        _svid  = re.sub(r'[^a-zA-Z0-9_\-]', '', _svraw)
                        _svthumb = f"https://img.youtube.com/vi/{_svid}/mqdefault.jpg"
                        with _svc:
                            st.markdown(f"""
    <div style="background:rgba(255,165,0,0.05);border-radius:12px;overflow:hidden;
                border:1px solid rgba(255,165,0,0.18);margin-bottom:6px;">
      <div style="position:relative;overflow:hidden;aspect-ratio:16/9;background:#111;">
        <img src="{_svthumb}" loading="lazy"
             style="width:100%;height:100%;object-fit:cover;opacity:0.85;"
             onerror="this.style.visibility='hidden'">
        <div style="position:absolute;inset:0;display:flex;align-items:center;
                    justify-content:center;background:rgba(0,0,0,0.35);">
          <span style="font-size:1.8rem;">📌</span>
        </div>
      </div>
      <div style="padding:7px 10px 4px;">
        <div style="font-size:0.74em;color:#999;font-family:monospace;">
          {_svid[:22]}{'...' if len(_svid)>22 else ''}
        </div>
      </div>
    </div>""", unsafe_allow_html=True)
                            _sbc1, _sbc2 = st.columns([3, 1])
                            with _sbc1:
                                if st.button("▶ İzle", key=f"ytsv_play_{_svraw}_{_svidx}", use_container_width=True):
                                    st.session_state.yt_iframe_mounted = False
                                    st.session_state.yt_iframe_vid = ""
                                    st.session_state.yt_playing_id      = _svid
                                    st.session_state.yt_playing_title   = _svid
                                    st.session_state.yt_playing_channel = ""
                                    st.session_state.yt_results         = []
                                    st.session_state.global_player_rendered = False  # 🔥 YENİ VİDEO İÇİN SIFIRLA
                                    st.rerun()
                            with _sbc2:
                                if st.button("Sil", key=f"ytsv_del_{_svraw}_{_svidx}"):
                                    current_videos = user_ref.get().to_dict().get("videos", [])
                                    if _svraw in current_videos:
                                        current_videos.remove(_svraw)
                                        user_ref.update({"videos": current_videos})
                                    st.rerun()
            else:
                st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.08);margin:16px 0 12px;'>", unsafe_allow_html=True)
                st.info("Henüz kayıtlı video yok.") 
