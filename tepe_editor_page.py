import streamlit as st
import json
import time

def render_tepe_editor_page(db, is_kurucu, get_global_announcement):
    st.markdown("""
    <style>
    /* Reset Streamlit default layout margins and overflow for an immersive editor page */
    div[data-testid="stAppViewBlockContainer"] {
        max-width: 100% !important;
        padding-left: 0px !important;
        padding-right: 0px !important;
        padding-top: 0px !important;
        padding-bottom: 0px !important;
        margin: 0px !important;
    }
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    div[data-testid="stHeader"] {display: none !important;}
    button[title="View source code"] {display: none !important;}
    iframe {
        width: 100% !important;
        border: none !important;
        border-radius: 0px !important;
        box-shadow: none !important;
        padding: 0px !important;
        margin: 0px !important;
    }
    </style>
    """, unsafe_allow_html=True)

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
            background: #0b0b14;
            color: #ffffff;
            overflow-x: hidden;
            overflow-y: auto;
            user-select: none;
            -webkit-user-select: none;
            padding: 6px;
            width: 100%;
            max-width: 100%;
            box-sizing: border-box;
        }}
        .stage-container {{
            background: #0f0f1e;
            border: 2px solid #e67e22;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.6), inset 0 0 20px rgba(230, 126, 34, 0.15);
            padding: 12px;
            overflow: hidden;
            width: 100%;
            max-width: 100%;
            box-sizing: border-box;
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
            grid-template-columns: 1fr 1fr;
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
            max-height: 480px;
            height: auto;
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
        .form-control {{
            width: 100%;
            background: #090914;
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 6px;
            padding: 7px 10px;
            color: white;
            font-size: 12px;
            outline: none;
            transition: all 0.2s ease;
        }}
        .form-control:focus {{
            border-color: #e67e22;
            box-shadow: 0 0 8px rgba(230,126,34,0.3);
        }}
        .flex-row {{
            display: flex;
            gap: 8px;
            width: 100%;
            box-sizing: border-box;
        }}
        .flex-item {{
            flex: 1;
            min-width: 0;
            box-sizing: border-box;
        }}
        .flex-row.no-stack {{
            flex-direction: row !important;
        }}
        .flex-row.no-stack .flex-item {{
            flex: 1 !important;
            width: auto !important;
        }}

        @media (max-width: 800px) {{
            .flex-row:not(.no-stack) {{
                flex-direction: column !important;
                gap: 8px;
            }}
            .flex-row:not(.no-stack) .flex-item {{
                width: 100% !important;
                flex: none !important;
            }}
            body {{
                padding: 4px;
            }}
            .stage-container {{
                padding: 8px;
                border-radius: 8px;
            }}
            .editor-panel-right {{
                padding: 8px;
            }}
            .form-group {{
                margin-bottom: 8px;
            }}
            .tabs-header {{
                flex-wrap: wrap !important;
                gap: 4px !important;
            }}
            .tab-btn {{
                padding: 6px 8px !important;
                font-size: 10px !important;
                flex: 1 1 30% !important;
                text-align: center !important;
                border-radius: 4px !important;
                white-space: normal !important;
            }}
            .top-nav-bar {{
                flex-direction: column !important;
                gap: 6px !important;
                padding: 6px !important;
            }}
            .nav-btn {{
                width: 100% !important;
                padding: 8px 6px !important;
                font-size: 11px !important;
                flex: none !important;
            }}
            .toolbar {{
                grid-template-columns: 1fr !important;
                gap: 6px !important;
            }}
            div[style*="gap:15px"] {{
                flex-direction: column !important;
                gap: 8px !important;
                align-items: flex-start !important;
            }}
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

        /* STATS INDICATORS ROW - SINGLE COLUMN BY DEFAULT FOR MOBILE */
        .indicators-row {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 6px;
        }}
        @media (min-width: 800px) {{
            .indicators-row {{
                grid-template-columns: repeat(4, 1fr);
            }}
        }}
        .indicator {{
            background: rgba(0,0,0,0.5);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 8px;
            padding: 8px 12px;
            text-align: center;
            font-size: 11px;
            color: #bdc3c7;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        @media (min-width: 800px) {{
            .indicator {{
                display: block;
                padding: 5px 3px;
            }}
        }}
        .indicator span {{
            color: #f39c12;
            font-weight: bold;
            font-size: 13px;
        }}
        @media (min-width: 800px) {{
            .indicator span {{
                display: block;
                font-size: 12px;
                margin-top: 1px;
            }}
        }}

        /* GRID-BASED TOOLBAR - SINGLE COLUMN BY DEFAULT FOR MOBILE */
        .toolbar {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 6px;
            margin-bottom: 10px;
        }}
        @media (min-width: 800px) {{
            .toolbar {{
                grid-template-columns: repeat(3, 1fr);
            }}
        }}
        .action-btn {{
            background: #252538;
            color: white;
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 6px;
            padding: 10px 12px;
            font-size: 12px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.15s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 4px;
            box-sizing: border-box;
            width: 100%;
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
            gap: 8px;
        }}
        @media (min-width: 800px) {{
            .bottom-action-bar {{
                flex-direction: row;
            }}
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

        /* IMMERSIVE HEADER DESTRUCT NAVIGATION BAR */
        .top-nav-bar {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-bottom: 12px;
            background: rgba(255, 255, 255, 0.03);
            padding: 8px;
            border-radius: 10px;
            border: 1px dashed rgba(230, 126, 34, 0.25);
        }}
        .nav-btn {{
            flex: 1 1 90px;
            background: #1c1c34;
            color: #bdc3c7;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 10px 6px;
            font-size: 11px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 4px;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
        }}
        .nav-btn:hover {{
            color: #ffffff;
            background: #e67e22;
            border-color: #e67e22;
            box-shadow: 0 0 10px rgba(230, 126, 34, 0.4);
        }}
        .nav-btn:active {{
            transform: scale(0.96);
        }}
    </style>
</head>
<body>
    <div class="top-nav-bar">
        <button class="nav-btn" onclick="pushAction('back_to_announcement')">🔔 Duyuru Sayfası</button>
        <button class="nav-btn" onclick="pushAction('back_to_main')">🏰 Yönetici Paneli</button>
        <button class="nav-btn" onclick="pushAction('back_to_chat')">💬 Sohbet Ekranı</button>
    </div>

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
                        <div class="flex-row no-stack" style="align-items: center;">
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
                            <div class="flex-row no-stack" style="align-items: center;">
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
                    <div class="form-group" style="background:rgba(230,126,34,0.06); padding:10px; border-radius:8px; border:1px solid rgba(230,126,34,0.15)">
                        <div class="toggle-container" onclick="toggleCheckbox('inp-glow-enabled')">
                            <input type="checkbox" id="inp-glow-enabled" class="hidden-checkbox" onchange="toggleGlowFields(); renderPreview();" />
                            <div class="toggle-switch"></div>
                            <span style="font-size:12px; font-weight:bold; color:white;">✨ NEON IŞILTI (GLOW) AKTİF</span>
                        </div>
                    </div>

                    <div id="glow-fields">
                        <div class="form-group">
                            <label>Işıltı Yoğunluğu (Neon Intensity)</label>
                            <div class="flex-row no-stack" style="align-items: center;">
                                <input type="range" id="inp-glow-intensity" min="10" max="100" value="{ann_glow_intensity_sb}" class="form-control" style="flex:3;" oninput="document.getElementById('v-glow-intensity').innerText=this.value; renderPreview()" />
                                <span id="v-glow-intensity" style="flex:1; text-align:right; font-size:11px; color:#e67e22; font-weight:bold;">{ann_glow_intensity_sb}</span>
                            </div>
                        </div>

                        <div class="form-group">
                            <label>Işıltı Renk Modu</label>
                            <div class="flex-row" style="gap:15px; margin-top:5px;">
                                <label style="display:flex; align-items:center; gap:5px; font-size:11px; text-transform:none; cursor:pointer;">
                                    <input type="radio" name="glow_color_mode" value="auto" checked onchange="toggleGlowFields(); renderPreview();" /> Otomatik (Harf Rengiyle Aynı)
                                </label>
                                <label style="display:flex; align-items:center; gap:5px; font-size:11px; text-transform:none; cursor:pointer;">
                                    <input type="radio" name="glow_color_mode" value="fixed" onchange="toggleGlowFields(); renderPreview();" /> Sabit Renk Seç
                                </label>
                            </div>
                        </div>

                        <div id="glow-color-field" class="form-group">
                            <label>Sabit Neon Işıma Rengi</label>
                            <input type="color" id="inp-glow-color-fixed" value="{ann_glow_color_fixed_sb}" class="form-control" style="height:35px; padding:2px;" oninput="renderPreview()" />
                        </div>
                    </div>

                    <hr style="border:none; border-top:1px solid rgba(255,255,255,0.06); margin:15px 0;" />

                    <div class="form-group" style="background:rgba(255,255,255,0.03); padding:10px; border-radius:8px; border:1px solid rgba(255,255,255,0.05)">
                        <div class="toggle-container" onclick="toggleCheckbox('inp-shadow-enabled')">
                            <input type="checkbox" id="inp-shadow-enabled" class="hidden-checkbox" onchange="toggleShadowFields(); renderPreview();" />
                            <div class="toggle-switch"></div>
                            <span style="font-size:12px; font-weight:bold; color:white;">👥 METİN SİYAH GÖLGESİ (3D) AKTİF</span>
                        </div>
                    </div>

                    <div id="shadow-fields">
                        <div class="form-group">
                            <label>Gölge Yoğunluğu (Shadow Intensity)</label>
                            <div class="flex-row no-stack" style="align-items: center;">
                                <input type="range" id="inp-shadow-intensity" min="10" max="100" value="{ann_shadow_intensity_sb}" class="form-control" style="flex:3;" oninput="document.getElementById('v-shadow-intensity').innerText=this.value; renderPreview()" />
                                <span id="v-shadow-intensity" style="flex:1; text-align:right; font-size:11px; color:#e67e22; font-weight:bold;">{ann_shadow_intensity_sb}</span>
                            </div>
                        </div>

                        <div class="form-group">
                            <label>Metin Gölge Rengi</label>
                            <input type="color" id="inp-shadow-color" value="{ann_shadow_color_sb}" class="form-control" style="height:35px; padding:2px;" oninput="renderPreview()" />
                        </div>
                    </div>

                    <hr style="border:none; border-top:1px solid rgba(255,255,255,0.06); margin:15px 0;" />

                    <div class="form-group">
                        <label>Hareket ve Giriş Canlandırması (Animation)</label>
                        <select id="inp-animation-type" class="form-control" onchange="renderPreview()">
                            <option value="none">Animasyon Yok (Sabit)</option>
                            <option value="neon_pulse">Parıltılı Sönme (Neon Pulse)</option>
                            <option value="neon_flicker">Retro Arızalı Lamba Flasör (Neon Flicker)</option>
                            <option value="rainbow">Gökkuşağı Renk Geçişleri (Rainbow Gradient)</option>
                            <option value="wiggle">Eğlenceli Dalgalanma (Wiggle Line)</option>
                            <option value="pulse">Büyüyüp Küçülme (Pulse)</option>
                            <option value="blur_fade">Fluluk Açılıp Kapanma (Blur Fade)</option>
                        </select>
                    </div>
                </div>

                <!-- TAB 5: Medya -->
                <div id="tab-gorsel" class="tab-content">
                    <div class="form-group">
                        <label>Sol/Sağ veya Alt/Üst Görsel Linki (PNG/GIF)</label>
                        <input type="text" id="inp-media-url" value="{ann_media_url_sb}" placeholder="https://... logo veya küçük resim" class="form-control" oninput="renderPreview()" />
                    </div>

                    <div class="flex-row">
                        <div class="form-group flex-item">
                            <label>Hizalama Konumu</label>
                            <select id="inp-media-align" class="form-control" onchange="renderPreview()">
                                <option value="below">Metnin Altında (Below)</option>
                                <option value="above">Metnin Üstünde (Above)</option>
                                <option value="left">Metnin Solunda (Left)</option>
                                <option value="right">Metnin Sağında (Right)</option>
                            </select>
                        </div>
                        <div class="form-group flex-item">
                            <label>Görsel Boyutu</label>
                            <div class="flex-row no-stack" style="align-items: center;">
                                <input type="range" id="inp-media-size" min="20" max="300" value="{ann_media_size_sb}" class="form-control" style="flex:3;" oninput="document.getElementById('v-media-size').innerText=this.value+'px'; renderPreview()" />
                                <span id="v-media-size" style="flex:1.2; text-align:right; font-size:11px; color:#e67e22; font-weight:bold;">{ann_media_size_sb}px</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- MAIN ENGINE CONTROLLERS EXECUTORS SCRIPT -->
    <script>
        // Variables setup
        const canvasArea = document.getElementById('canvas-area');
        const dragItem = document.getElementById('drag-item');
        
        let x = {disp_x_sb};
        let y = {disp_y_sb};
        let size = {disp_size_sb};
        let rot = {disp_rot_sb};
        
        // Single Character Color State Matrix (sync array representation)
        let charColorsArray = {char_colors_json};

        // Switch tab mechanism
        function switchTab(tabId) {{
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            const reqBtn = Array.from(document.querySelectorAll('.tab-btn')).find(b => b.getAttribute('onclick').includes(tabId));
            if (reqBtn) reqBtn.classList.add('active');
            
            const reqContent = document.getElementById(tabId);
            if (reqContent) reqContent.classList.add('active');
        }}

        // Sync and draw individual character selectors based on text length
        function syncCharColorsCount(length) {{
            const gridContainer = document.getElementById('char-colors-grid');
            gridContainer.innerHTML = "";
            
            // Adjust colors array to match length exactly
            while (charColorsArray.length < length) {{
                charColorsArray.push(document.getElementById('inp-text-color').value || "#FFFFFF");
            }}
            if (charColorsArray.length > length) {{
                charColorsArray = charColorsArray.slice(0, length);
            }}

            const textValue = document.getElementById('inp-text').value;
            for (let i = 0; i < length; i++) {{
                const char = textValue[i] || ' ';
                if (char.trim() === "") continue; // skip spaces in single color configurations
                
                const box = document.createElement('div');
                box.className = "char-color-box";
                
                const span = document.createElement('span');
                span.innerText = `Harf ${{i + 1}}: "${{char}}"`;
                
                const inp = document.createElement('input');
                inp.type = "color";
                inp.value = charColorsArray[i];
                inp.addEventListener('input', (e) => {{
                    charColorsArray[i] = e.target.value;
                    renderPreview();
                }});
                
                box.appendChild(span);
                box.appendChild(inp);
                gridContainer.appendChild(box);
            }}
        }}

        // Form conditional state triggers
        function toggleCheckbox(id) {{
            const ch = document.getElementById(id);
            if (ch) {{
                ch.checked = !ch.checked;
                ch.dispatchEvent(new Event('change'));
            }}
        }}

        function toggleBgFields() {{
            const typeVal = document.getElementById('inp-bg-type').value;
            const bgColRow = document.getElementById('bg-color-fields');
            const bgColGradientEnd = document.getElementById('bg-gradient-field');
            const bgImgFields = document.getElementById('bg-image-fields');
            
            if (typeVal === "none") {{
                bgColRow.style.display = "none";
                bgImgFields.style.display = "none";
            }} else if (typeVal === "flat") {{
                bgColRow.style.display = "flex";
                bgColGradientEnd.style.display = "none";
                bgImgFields.style.display = "none";
            }} else if (typeVal === "gradient") {{
                bgColRow.style.display = "flex";
                bgColGradientEnd.style.display = "block";
                bgImgFields.style.display = "none";
            }} else if (typeVal === "image") {{
                bgColRow.style.display = "none";
                bgImgFields.style.display = "block";
            }}
        }}

        function toggleGlowFields() {{
            const enabled = document.getElementById('inp-glow-enabled').checked;
            const fields = document.getElementById('glow-fields');
            fields.style.display = enabled ? "block" : "none";
            
            if (enabled) {{
                const isFixed = document.querySelector('input[name="glow_color_mode"]:checked').value === "fixed";
                document.getElementById('glow-color-field').style.display = isFixed ? "block" : "none";
            }}
        }}

        function toggleShadowFields() {{
            const enabled = document.getElementById('inp-shadow-enabled').checked;
            document.getElementById('shadow-fields').style.display = enabled ? "block" : "none";
        }}

        // Event listener for main text input changes
        function handleTextChange() {{
            const text = document.getElementById('inp-text').value;
            syncCharColorsCount(text.length);
            renderPreview();
        }}

        function handleTextGlobalColorChange(val) {{
            // Apply globall change to all individual characters
            for (let i = 0; i < charColorsArray.length; i++) {{
                charColorsArray[i] = val;
            }}
            syncCharColorsCount(charColorsArray.length);
            renderPreview();
        }}

        function applyBulkColor() {{
            const col = document.getElementById('bulk-color-pick').value;
            handleTextGlobalColorChange(col);
        }}

        function applyWordHighlight() {{
            const target = document.getElementById('paint-word-target').value;
            const color = document.getElementById('paint-word-color').value;
            const textVal = document.getElementById('inp-text').value;
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
            const glow_color_mode = document.querySelector('input[name="glow_color_mode"]:checked').value;
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
            bannerWrapper.style.cssText = bg_css + ` text-align: ${{align}}; font-family: '${{font}}', sans-serif; transition: all 0.15s ease; width: 100%;`;

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
                const char_color = charColorsArray[i] || "#FFFFFF";
                
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
                
                rendered_chars_html += `<span class="${{span_class}}" style="display: inline-block; white-space: pre-wrap; color: ${{char_color}}; ${{glow_val_style}} ${{shadow_style}} ${{italic_bold_style}} ${{anim_delay_style}}">${{char}}</span>`;
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
            }} else if (e.touches.length === 2) {{
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
            const glow_color_mode = document.querySelector('input[name="glow_color_mode"]:checked').value;
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

            const payload = {{
                displacement_x: x,
                displacement_y: y,
                rotation: rot,
                size: size,
                text: text,
                font: font,
                align: align,
                font_weight: font_weight,
                font_style: font_style,
                text_decoration: text_decoration,
                opacity: opacity,
                glow_enabled: glow_enabled,
                glow_intensity: glow_intensity,
                glow_color_mode: glow_color_mode,
                glow_color_fixed: glow_color_fixed,
                shadow_enabled: shadow_enabled,
                shadow_intensity: shadow_intensity,
                shadow_color: shadow_color,
                animation_type: animation_type,
                bg_type: bg_type,
                bg_color: bg_color,
                bg_gradient_end: bg_gradient_end,
                bg_image_url: bg_image_url,
                bg_opacity: bg_opacity,
                padding_vertical: padding_vertical,
                padding_horizontal: padding_horizontal,
                border_radius: border_radius,
                media_url: media_url,
                media_align: media_align,
                media_size: media_size,
                char_colors: charColorsArray
            }};
            
            return JSON.stringify(payload);
        }}

        function pushAndSubmit(targetAction) {{
            const jsonText = buildFullPayloadJSON();
            
            // Populate fallback hidden forms value
            const textareas = window.parent.document.querySelectorAll('textarea[aria-label="advanced_json_payload"]');
            textareas.forEach(t => {{
                t.value = jsonText;
                t.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }});
            
            // Programmatically click forms submit element
            setTimeout(() => {{
                let btn = null;
                if (targetAction === 'preview') {{
                    btn = Array.from(window.parent.document.querySelectorAll('button')).find(b => b.innerText.includes('Düzenlemeyi Önizle'));
                }} else {{
                    btn = Array.from(window.parent.document.querySelectorAll('button')).find(b => b.innerText.includes('Tepe Duyurusunu Kaydet'));
                }}
                if (btn) {{
                    btn.click();
                }}
            }}, 150);
        }}

        function pushAction(actionName) {{
            const jsonText = buildFullPayloadJSON();
            const payload = JSON.parse(jsonText);
            payload.action = actionName;
            
            const textareas = window.parent.document.querySelectorAll('textarea[aria-label="advanced_json_payload"]');
            textareas.forEach(t => {{
                t.value = JSON.stringify(payload);
                t.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }});
            
            setTimeout(() => {{
                const btn = Array.from(window.parent.document.querySelectorAll('button')).find(b => b.innerText.includes('Tepe Duyurusunu Kaydet'));
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
 
    st.components.v1.html(sandbox_code, height=1750, scrolling=True)
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
            action = updated_payload.get("action", "")
            
            if action == "back_to_announcement":
                st.session_state.current_page = "admin_announcement"
                st.rerun()
            elif action == "back_to_main":
                st.session_state.current_page = "admin_main"
                st.rerun()
            elif action == "back_to_chat":
                st.session_state.current_page = "chat"
                st.rerun()
                
            if "action" in updated_payload:
                del updated_payload["action"]
            
            # Store as temp settings in memory
            st.session_state.temp_ann_settings = updated_payload
            
            if btn_save:
                # Write permanently to database
                db.collection("settings").document("global_announcement").set(updated_payload)
                st.success("✅ Tepe duyurusu başarıyla kaydedildi ve canlı yayına alındı!")
                time.sleep(1)
                st.rerun()
            else:
                st.success("👀 Önizleme başarıyla güncellendi! Yukarıdaki CapCut editör panelinden anlık sonucu görebilirsiniz.")
                time.sleep(1)
                st.rerun()
        except Exception as e:
            st.error(f"⚠️ Teknik bir hata oluştu: {e}")
