import streamlit as st
import streamlit.components.v1 as components
import requests
import os
import json
import uuid
import firebase_admin
from firebase_admin import credentials, auth, firestore
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
    page_title="Aslan Parçası V16.8",
    page_icon="🦁",
    layout="centered"
)

# --- GOOGLE TRANSLATE ENGELLEME + GLOBAL UI TWEAKS ---
st.markdown("""
<meta name="google" content="notranslate">
<meta http-equiv="Content-Language" content="tr">

<style>
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
      }
    }, true);
    // Ayrıca "focusin" ile de yakala - iframe'den çıkınca tetiklenir
    window.parent.addEventListener('focus', function() {
      // iframe'lerden dönen focus'u temizle
      var active = pd.activeElement;
      if (active && active.tagName === 'IFRAME') {
        active.blur();
        window.parent.focus();
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
      'Hesab': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
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
      'G\\u00f6nder': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>',
      'ifre': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>',
      'Sil': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>',
      'Ayarlar': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.6 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.6a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
      'Geri': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>'
    };

    function injectIcons() {
      var btns = pd.querySelectorAll('button[kind] p, button[data-testid] p');
      btns.forEach(function(p) {
        if (p.getAttribute('data-icons-done')) return;
        var txt = p.textContent || '';
        // Önce emojiyi kaldır (regex'i string'den oluştur - Python surrogate sorunu için)
        var emojiRe = new RegExp('[\\uD83C-\\uDBFF][\\uDC00-\\uDFFF]|[\\u2600-\\u27BF]|\\uFE0F', 'g');
        if (emojiRe.test(txt)) {
          emojiRe.lastIndex = 0;
          // textNode'lardan emojiyi temizle
          Array.from(p.childNodes).forEach(function(n) {
            if (n.nodeType === 3) {
              var cleanRe = new RegExp('[\\uD83C-\\uDBFF][\\uDC00-\\uDFFF]|[\\u2600-\\u27BF]|\\uFE0F', 'g');
              n.textContent = n.textContent.replace(cleanRe, '').replace(/^ +/, '');
            }
          });
          txt = p.textContent || '';
        }
        // Sonra SVG ikon ekle
        for (var key in icons) {
          if (txt.indexOf(key) !== -1) {
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

    // İlk çalıştırma + MutationObserver ile yeni butonları da yakala
    setTimeout(function() { injectIcons(); }, 500);
    var btnObs = new MutationObserver(function() {
      setTimeout(injectIcons, 100);
      // Avatar tıklama: profil yuvarlağına tıklayınca gizli file uploader açılır
      var avatar = pd.querySelector('.profil-avatar-wrap img');
      if (avatar && !avatar.dataset.clickBound) {
        avatar.dataset.clickBound = '1';
        avatar.addEventListener('click', function() {
          var uploader = pd.querySelector('[data-testid="stFileUploader"] input[type="file"]');
          if (uploader) uploader.click();
        });
      }
    });
    btnObs.observe(pd.body || pd.documentElement, { childList: true, subtree: true });
    // İlk avatar setup
    setTimeout(function() {
      var avatar = pd.querySelector('.profil-avatar-wrap img');
      if (avatar && !avatar.dataset.clickBound) {
        avatar.dataset.clickBound = '1';
        avatar.addEventListener('click', function() {
          var uploader = pd.querySelector('[data-testid="stFileUploader"] input[type="file"]');
          if (uploader) uploader.click();
        });
      }
    }, 1000);
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
    "🦁 Aslan İni": "linear-gradient(135deg, #0f2027, #203a43, #2c5364)",
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
def normalize_text(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    return re.sub(r'[^a-zA-Z0-9]', '', text.lower())

def kufur_var_mi(text):
    clean_text = normalize_text(text)
    substring_list = [
        "amk", "amq", "amcik", "aminakoy", "aminakoyim", "aminakoyayim",
        "orospucocugu", "orspucocugu", "orospucuk",
        "sikerim", "sikeyim", "sikis", "siksok",
        "gotek", "gotlek", "piclik", "yavsak", "yavsaklik",
        "serefsiz", "ibnelik", "kahpece", "gavatlik", "dalyarak", "kancik",
        "fuck", "fuuck", "fck", "f u c k", "btch", "b1tch",
        "asshole", "ashole", "motherfucker", "mofo",
        "scheisse", "scheiße", "arschloch", "schlampe", "wichser", "hurensohn", "fotze", "ficken",
        "sharmouta", "sharmuta", "kussemmak", "putain", "connard",
    ]
    word_list = [
        "amina", "orospu", "sik", "got", "pic", "picin",
        "ibne", "kahpe", "gavat", "yarrak", "yarak",
        "dangalak", "gerzek", "gerizekali", "bok", "pust",
        "bitch", "cunt", "whore", "slut", "dick", "cock",
        "bastard", "nigger", "nigga", "faggot", "fag", "retard",
        "puta", "puto", "cabron", "maricon", "merde",
    ]
    for word in substring_list:
        if word in clean_text:
            return True
    for word in word_list:
        if re.search(r'(?<![a-z])' + re.escape(word) + r'(?![a-z])', clean_text):
            return True
    return False

def emoji_var_mi(text):
    emoji_pattern = re.compile("[" "\U00010000-\U0010ffff" "\u2600-\u27bf" "]+", flags=re.UNICODE)
    return bool(emoji_pattern.search(text))

def get_video_iframe(video_id):
    return f'<iframe width="100%" height="200" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe>'

def get_styled_user_name(u_name, u_color, u_glow, u_tag, u_rozet):
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
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            sonuclar = list(ddgs.text(sorgu, max_results=max_sonuc, region="tr-tr"))
        if not sonuclar:
            return ""
        parcalar = []
        for s in sonuclar:
            baslik = s.get("title", "")
            icerik = s.get("body", "")
            if baslik or icerik:
                parcalar.append(f"• {baslik}: {icerik}")
        return "\n".join(parcalar)
    except Exception:
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
COMP_DIR = os.path.join(tempfile.gettempdir(), "aslan_ls_component")
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
      window.onload = function() {
          sendMessage("streamlit:componentReady", {apiVersion: 1});
          sendMessage("streamlit:setFrameHeight", {height: 0});
          var val = localStorage.getItem("aslan_passkey");
          sendMessage("streamlit:setComponentValue", {value: val ? val : "NOT_FOUND"});
      };
    </script></head>
    <body></body>
    </html>
    """)

get_local_storage = components.declare_component("get_local_storage", path=COMP_DIR)

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
    components.html("<script>localStorage.removeItem('aslan_passkey');</script>", height=0, width=0)
    st.markdown("<h3 style='text-align:center; color:white; margin-top:20vh;'>Çıkış yapılıyor...</h3>", unsafe_allow_html=True)
    st.session_state.trigger_clear_token = False
    time.sleep(0.5)
    st.rerun()

if st.session_state.get("trigger_save_token"):
    uid = st.session_state.trigger_save_token
    components.html(f"<script>localStorage.setItem('aslan_passkey', '{uid}');</script>", height=0, width=0)
    st.session_state.trigger_save_token = None

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

    elif token != "NOT_FOUND":
        try:
            user_ref_temp = db.collection("users").document(token)
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
                    st.session_state.user_data = {**user_data, "uid": token}
                    st.session_state.user_logged_in = True
                    st.session_state.tema = user_data.get("tema", list(TEMALAR.values())[0])
                    st.session_state.tema_rengi = TEMA_RENKLERI.get(st.session_state.tema, "rgba(20,20,40,0.85)")

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

    st.title("🦁 Aslan Parçası V16.8")

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
                                db.collection("users").document(query[0].id).update({"durum": "Aktif", "ban_bitis_zamani": None})
                                db.collection("banlanan_emails").document(clean_email).delete()
                                user_data["durum"] = "Aktif"
                                user_data["ban_bitis_zamani"] = None
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
    uid = st.session_state.user_data['uid']
    user_ref = db.collection("users").document(uid)

    try:
        user_ref.update({"son_gorulme_zamani": firestore.SERVER_TIMESTAMP})
    except Exception:
        pass

    user_snap = user_ref.get()

    if not user_snap.exists:
        logout_user()

    user_doc = user_snap.to_dict()

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
                db.collection("users").document(uid).update({"durum": "Aktif", "ban_bitis_zamani": None})
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
    if st.session_state.current_page in ["admin_main", "admin_users", "admin_role_management"] and not is_kurucu:
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
    .stTextArea textarea, .stTextInput input, .stSelectbox div {{
        color: #FFFFFF !important;
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
    }}
    [data-baseweb="select"] * {{ color: #FFFFFF !important; }}
    [data-testid="stWidgetLabel"] p {{ color: #F8F9FA !important; }}
    .assistant-box {{
        background-color: rgba(30, 30, 30, 0.8);
        padding: 12px; border-radius: 10px; border-left: 5px solid gold; margin-bottom: 15px;
        display: flex; align-items: flex-start; gap: 10px; color: white;
        word-wrap: break-word !important; overflow-wrap: break-word !important;
        word-break: break-word !important; max-width: 100% !important;
        box-sizing: border-box !important; min-width: 0;
    }}
    .user-box {{
        background-color: rgba(255, 255, 255, 0.1);
        padding: 12px; border-radius: 10px; margin-bottom: 15px;
        display: flex; justify-content: flex-end; align-items: flex-start;
        gap: 10px; color: white;
        word-wrap: break-word !important; overflow-wrap: break-word !important;
        word-break: break-word !important; max-width: 100% !important;
        box-sizing: border-box !important; min-width: 0;
    }}
    .assistant-box *, .user-box * {{
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

    isim_stili = get_styled_user_name(kullanici_ismi, u_color, u_glow, u_tag, u_rozet)

    @st.fragment(run_every=60)
    def saat_gosterici():
        tr_simdi = get_tr_time()
        saat_str = tr_simdi.strftime("%H:%M")
        tarih_str = tr_simdi.strftime("%d.%m.%Y")
        st.markdown(f"<div style='text-align:center; color:#f39c12; font-size:0.9em;'>🕐 {saat_str} | 📅 {tarih_str} (TR)</div>", unsafe_allow_html=True)

    with st.sidebar:
        saat_gosterici()

        # --- AYARLAR STATE ---
        if "sidebar_settings_open" not in st.session_state:
            st.session_state.sidebar_settings_open = False

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

        else:
            # ═══ NORMAL MENÜ ═══
            # --- PROFİL FOTOĞRAFI (yuvarlak avatar - tıklanabilir) ---
            mevcut_foto = user_doc.get("profil_foto", "")
            if mevcut_foto:
                avatar_src = f"data:image/jpeg;base64,{mevcut_foto}"
            else:
                avatar_src = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

            # Tıklanabilir avatar (CSS + JS avatar click handler global script'te)
            st.markdown("""<style>
            .profil-avatar-wrap { text-align:center; margin-bottom:8px; cursor:pointer; }
            .profil-avatar-wrap img { width:70px; height:70px; border-radius:50%; object-fit:cover; border:2px solid #f39c12; transition: opacity 0.2s; }
            .profil-avatar-wrap img:hover { opacity:0.7; }
            .profil-avatar-wrap .avatar-hint { font-size:0.7em; color:#888; margin-top:4px; }
            </style>""", unsafe_allow_html=True)

            st.markdown(f'<div class="profil-avatar-wrap"><img src="{avatar_src}"/><div class="avatar-hint">Değiştirmek için tıkla</div></div>', unsafe_allow_html=True)

            # Gizli file uploader (CSS ile görünmez)
            if "foto_upload_key" not in st.session_state:
                st.session_state.foto_upload_key = 0
            foto_dosya = st.file_uploader("Profil fotoğrafı", type=["jpg", "jpeg", "png", "webp"], key=f"profil_foto_upload_{st.session_state.foto_upload_key}", label_visibility="collapsed")
            if foto_dosya is not None:
                if foto_dosya.size > 5 * 1024 * 1024:
                    st.error("❌ Dosya boyutu 5MB'dan küçük olmalıdır.")
                else:
                    foto_bytes = foto_dosya.read()
                    foto_b64 = resize_profile_photo(foto_bytes)
                    user_ref.update({"profil_foto": foto_b64})
                    st.session_state.foto_upload_key += 1
                    st.rerun()

            # Uploader'ı CSS ile gizle
            st.markdown("""<style>
            [data-testid="stFileUploader"] { position:absolute !important; width:1px !important; height:1px !important; overflow:hidden !important; opacity:0 !important; pointer-events:none !important; }
            </style>""", unsafe_allow_html=True)

            if mevcut_foto:
                if st.button("Fotoğrafı Kaldır", key="remove_profile_photo", use_container_width=True):
                    user_ref.update({"profil_foto": ""})
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
            if st.button("👥 Arkadaş Ara", use_container_width=True, key="arkadas_ara_btn"):
                st.session_state.current_page = "arkadas_ara"
                st.rerun()

            if st.button("💬 Mesajlarım (DM)", use_container_width=True, key="dm_inbox_btn"):
                st.session_state.current_page = "dm_inbox"
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
    # 🎵 GLOBAL OYNATICI (her render'da çizilir; Streamlit aynı iframe'i
    # koruduğu için sayfa değişince oynatma/ses kesilmez)
    # ═══════════════════════════════════════════════════
    if st.session_state.get("yt_playing_id"):
        _gvid = re.sub(r'[^a-zA-Z0-9_\-]', '', st.session_state.yt_playing_id)
        _gts = int(st.session_state.yt_ts_dict.get(_gvid, 0))

        components.html(
                    f"""
                    <style>
                        html, body {{ margin:0; padding:0; height:100%; background:transparent; overflow:hidden; }}
                        #ap-gp-wrap {{ position:absolute; inset:0; background:#000; border-radius:10px; overflow:hidden; }}
                        #global-yt-player {{ position:absolute; inset:0; width:100%; height:100%; }}
                        #global-yt-player iframe {{ width:100% !important; height:100% !important; }}
                        #ap-unmute {{ position:absolute; inset:0; display:flex; align-items:center; justify-content:center; background:rgba(0,0,0,0.55); cursor:pointer; z-index:5; }}
                    </style>
                    <div id="ap-gp-wrap">
                        <div id="global-yt-player"></div>
                        <div id="ap-unmute">
                            <div style="background:#FF0000;color:#fff;font-weight:800;font-size:1rem;padding:12px 24px;border-radius:30px;box-shadow:0 6px 22px rgba(0,0,0,.55);display:flex;align-items:center;gap:8px;">
                                🔊 Sesi Aç
                            </div>
                        </div>
                    </div>
                    <script>
                    (function() {{
                        var VID = '{_gvid}';
                        var SK = 'ytpos_' + VID;
                        var startT = {_gts};
                        try {{
                            var savedT = parseFloat(localStorage.getItem(SK) || '0') || 0;
                            if (savedT > startT) startT = savedT;
                        }} catch(e) {{}}

                        // --- Kendi iframe'imizi sabitleyip portal/sohbet durumuna göre konumlandır ---
                        var fe = null;
                        try {{ fe = window.frameElement; }} catch(e) {{ fe = null; }}
                        if (fe) {{
                            fe.style.position = 'fixed';
                            fe.style.zIndex = '99990';
                            fe.style.border = '0';
                            fe.style.background = 'transparent';
                            fe.style.willChange = 'top, left, width, height';
                        }}
                        function getAnchor() {{
                            try {{ return window.parent.document.getElementById('ap-portal-anchor'); }}
                            catch(e) {{ return null; }}
                        }}
                        var _lastTop = '', _lastLeft = '', _lastW = '', _lastH = '';
                        var _hidden = false;
                        function place() {{
                            if (!fe) return;
                            var a = getAnchor();
                            if (a) {{
                                var r = a.getBoundingClientRect();
                                var nTop = Math.max(r.top, 0) + 'px';
                                var nLeft = r.left + 'px';
                                var nW = r.width + 'px';
                                var nH = r.height + 'px';
                                if (nTop !== _lastTop || nLeft !== _lastLeft || nW !== _lastW || nH !== _lastH) {{
                                    fe.style.top = nTop;
                                    fe.style.left = nLeft;
                                    fe.style.width = nW;
                                    fe.style.height = nH;
                                    _lastTop = nTop; _lastLeft = nLeft; _lastW = nW; _lastH = nH;
                                }}
                                if (_hidden) {{
                                    fe.style.opacity = '1';
                                    fe.style.pointerEvents = 'auto';
                                    _hidden = false;
                                }}
                            }} else {{
                                if (!_hidden) {{
                                    fe.style.top = '-9999px';
                                    fe.style.left = '-9999px';
                                    fe.style.width = '1px';
                                    fe.style.height = '1px';
                                    fe.style.opacity = '0';
                                    fe.style.pointerEvents = 'none';
                                    _hidden = true;
                                }}
                            }}
                            requestAnimationFrame(place);
                        }}
                        requestAnimationFrame(place);

                        var tag = document.createElement('script');
                        tag.src = 'https://www.youtube.com/iframe_api';
                        document.head.appendChild(tag);

                        var gp;
                        window.onYouTubeIframeAPIReady = function() {{
                            gp = new YT.Player('global-yt-player', {{
                                height: '100%',
                                width: '100%',
                                videoId: VID,
                                playerVars: {{
                                    autoplay: 1,
                                    controls: 1,
                                    rel: 0,
                                    modestbranding: 1,
                                    enablejsapi: 1,
                                    playsinline: 1,
                                    start: Math.floor(startT)
                                }},
                                events: {{
                                    onReady: function(event) {{
                                        // Tarayıcı politikası: sesli otomatik oynatma engellidir.
                                        // Bu yüzden sessiz başlat, kullanıcı tek dokunuşla sesi açar.
                                        try {{ event.target.mute(); }} catch(ex) {{}}
                                        if (startT > 0) {{ try {{ event.target.seekTo(startT, true); }} catch(ex) {{}} }}
                                        try {{ event.target.playVideo(); }} catch(ex) {{}}
                                        setInterval(function() {{
                                            try {{
                                                var t = gp.getCurrentTime();
                                                if (t > 0) localStorage.setItem(SK, String(t));
                                            }} catch(ex) {{}}
                                        }}, 3000);
                                    }}
                                }}
                            }});
                        }};

                        var btn = document.getElementById('ap-unmute');
                        function enableSound() {{
                            try {{ gp.unMute(); gp.setVolume(100); gp.playVideo(); }} catch(e) {{}}
                            if (btn) btn.style.display = 'none';
                        }}
                        if (btn) {{
                            btn.addEventListener('click', enableSound);
                            btn.addEventListener('touchstart', enableSound);
                        }}
                    }})();
                    </script>
                    """,
                    height=0,
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
                            if _u_foto:
                                _u_foto_src = f"data:image/jpeg;base64,{_u_foto}"
                            else:
                                _u_foto_src = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
                            st.markdown(f'<img src="{_u_foto_src}" style="width:40px;height:40px;border-radius:50%;object-fit:cover;border:1px solid #f39c12;float:left;margin-right:10px;"/>', unsafe_allow_html=True)
                            _u_color = u_data.get("isim_rengi", "#FFFFFF")
                            _u_glow = u_data.get("ismin_parlakligi", False)
                            _u_tag = u_data.get("tag", "")
                            _u_rozet = u_data.get("rozet", "")
                            _u_styled = get_styled_user_name(u_isim, _u_color, _u_glow, _u_tag, _u_rozet)
                            st.markdown(f"### {_u_styled}", unsafe_allow_html=True)
                            st.markdown(f"📧 **E-posta:** `{u_email}`")
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
                                    elif role == "assistant": formatted_lines.append(f"[Aslan Parçası]: {content}")
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
                                            db.collection("users").document(u_id).update({"durum": "Pasif", "ban_bitis_zamani": ban_bitis_zamani, "profil_foto": ""})
                                            db.collection("banlanan_emails").document(u_email).set({"ban_bitis_zamani": ban_bitis_zamani, "email": u_email})
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
                                    db.collection("users").document(u_id).update({"durum": "Aktif", "ban_bitis_zamani": None})
                                    db.collection("banlanan_emails").document(u_email).delete()
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

                        styled_reporter = get_styled_user_name(b_isim, b_color, b_glow, b_tag, b_rozet)

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
            secilen_email = st.text_input("Duyuru Gönderilecek E-posta Adresi:", placeholder="ornek@domain.com", key="quick_target_email_input").strip().lower()

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
                        st.success("📣 Duyuru tüm kullanıcılara başarıyla yayınlandı!")
                    else:
                        target_found = False
                        for u_doc_item in all_users_snap:
                            u_data = u_doc_item.to_dict()
                            if u_data.get("email", "").strip().lower() == secilen_email:
                                u_doc_item.reference.update({"okunmamis_duyurular": firestore.ArrayUnion([pushed_announcement])})
                                target_found = True
                                break
                        if target_found: st.success(f"📣 Duyuru başarıyla {secilen_email} adresine iletildi!")
                        else: st.error("❌ Yazılan e-posta adresiyle eşleşen bir kullanıcı bulunamadı.")

                    st.session_state.valid_users_cache = None
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Duyuru gönderilirken teknik bir hata oluştu: {e}")

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
        st.markdown("### 🔍 Kullanıcı Ara ve Düzenle")
        search_email = st.text_input("E-posta ile kullanıcı ara:", placeholder="ornek@domain.com").strip().lower()

        if search_email:
            user_query = db.collection("users").where("email", "==", search_email).limit(1).get()
            if user_query:
                target_doc = user_query[0]
                target_id = target_doc.id
                target_data = target_doc.to_dict()

                st.text_input("Kullanıcı İsmi (Salt Okunur):", value=target_data.get("isim", "Bilinmeyen"), disabled=True)
                st.text_input("Kullanıcı E-postası (Salt Okunur):", value=target_data.get("email", ""), disabled=True)
                isim_rengi = st.color_picker("İsim Rengi (Hex):", value=target_data.get("isim_rengi", "#FFFFFF"))
                ismin_parlakligi = st.checkbox("Yazı Parlaklığı (CSS Gölge Efekti):", value=target_data.get("ismin_parlakligi", False))
                tag_val = st.text_input("Kullanıcı Tagı (Örn: Moderatör, Vip):", value=target_data.get("tag", ""), max_chars=20)
                rozet_val = st.text_input("Kullanıcı Rozeti (Örn: 🛡️, 💎):", value=target_data.get("rozet", ""), max_chars=10)
                is_admin_flag = st.checkbox("Yönetici Yap (is_admin):", value=target_data.get("is_admin", False))

                if st.button("💾 Değişiklikleri Kaydet", type="primary", use_container_width=True):
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
                            _a_styled = get_styled_user_name(a_name, _a_color, _a_glow, a_tag, a_rozet)
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

            # --- ARKA PLAN KONTROL (tamamen görünmez — kullanıcı deneyimini etkilemez) ---
            _bg_container = st.container()
            with _bg_container:
                st.markdown('<div style="display:none !important; height:0; overflow:hidden;"></div>', unsafe_allow_html=True)

                @st.fragment(run_every=15)
                def arka_plan_kontrol(current_uid):
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
                        sender_rozet if sender_rozet else "🛠️"
                    )
                else:
                    display_sender = get_styled_user_name(sender_name, sender_color, sender_glow, sender_tag, sender_rozet if sender_rozet else "🛡️")

                st.markdown(f"""
                <div style="background-color: rgba(255, 0, 0, 0.15); border-left: 5px solid red; padding: 15px; border-radius: 5px; margin-bottom: 10px; box-shadow: 0 0 10px rgba(255, 0, 0, 0.4);">
                    <div style="font-size: 1.15rem; margin-bottom: 5px;">{display_sender}:</div>
                    <div style="color: white !important; font-size: 1.1rem; margin-left: 5px; line-height: 1.4;">{d_metin}</div>
                </div>
                """, unsafe_allow_html=True)

                if st.button("Geç ➡️", key=f"skip_btn_{duyuru_obj.get('id')}", use_container_width=True):
                    db.collection("users").document(uid).update({"okunmamis_duyurular": firestore.ArrayRemove([duyuru_obj])})
                    st.session_state.cached_okunmamis_duyurular.remove(duyuru_obj)
                    st.rerun()

            # --- SOHBET ARAYÜZÜ ---
            # Bildirim butonu (sağ üst köşe)
            gelen_istekler = user_doc.get("gelen_arkadaslik_istekleri", [])
            yetkili_msj = user_doc.get("yetkili_mesajlari", [])
            okunmamis_yetkili = [m for m in yetkili_msj if not m.get("okundu", False)] if isinstance(yetkili_msj, list) else []
            bildirim_sayisi = len(gelen_istekler) + len(okunmamis_yetkili)
            bildirim_badge = f" ({bildirim_sayisi})" if bildirim_sayisi > 0 else ""

            col_title, col_bildirim = st.columns([6, 1])
            with col_title:
                st.title("🤖 Aslan Parçası V16.8")
            with col_bildirim:
                st.write("")
                if st.button(f"🔔{bildirim_badge}", key="bildirim_btn", use_container_width=True):
                    st.session_state.bildirim_panel_open = not st.session_state.bildirim_panel_open
                    st.rerun()

            # --- BİLDİRİM PANELİ ---
            if st.session_state.bildirim_panel_open:
                with st.container(border=True):
                    st.markdown("### 🔔 Bildirimler")
                    tab_arkadaslik, tab_yetkili = st.tabs(["👥 Arkadaşlık İstekleri", "✉️ Yetkili Mesajları"])

                    with tab_arkadaslik:
                        if gelen_istekler:
                            for istek_uid in gelen_istekler:
                                try:
                                    istek_snap = db.collection("users").document(istek_uid).get()
                                    if istek_snap.exists:
                                        istek_d = istek_snap.to_dict()
                                        istek_isim = istek_d.get("isim", "Bilinmiyor")
                                        istek_foto = istek_d.get("profil_foto", "")
                                        istek_foto_src = f"data:image/jpeg;base64,{istek_foto}" if istek_foto else "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
                                        col_bf, col_bn, col_ba = st.columns([1, 3, 3])
                                        with col_bf:
                                            st.markdown(f'<img src="{istek_foto_src}" style="width:30px;height:30px;border-radius:50%;object-fit:cover;"/>', unsafe_allow_html=True)
                                        with col_bn:
                                            st.markdown(f"**{istek_isim}**")
                                        with col_ba:
                                            if st.button("✅ Kabul", key=f"kabul_{istek_uid}", use_container_width=True):
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
                                ym_gonderen = ym.get("gonderen_isim", "Yetkili")
                                ym_icerik = ym.get("icerik", "")
                                ym_zaman = ym.get("zaman", "")
                                ym_okundu = ym.get("okundu", False)
                                badge = "" if ym_okundu else "🆕 "
                                st.markdown(f"""<div style="background:rgba(243,156,18,0.1);border-left:3px solid #f39c12;padding:8px 12px;border-radius:6px;margin-bottom:6px;">
                                    <strong>{badge}{ym_gonderen}</strong> <span style="font-size:0.75em;color:#888;">({ym_zaman})</span><br>{ym_icerik}
                                </div>""", unsafe_allow_html=True)
                            # Okundu olarak işaretle
                            if okunmamis_yetkili:
                                guncellenmis = []
                                for ym in yetkili_msj:
                                    ym_copy = dict(ym)
                                    ym_copy["okundu"] = True
                                    guncellenmis.append(ym_copy)
                                user_ref.update({"yetkili_mesajlari": guncellenmis})
                        else:
                            st.caption("Yetkili mesajı yok.")

                    if st.button("Kapat", key="bildirim_kapat_btn", use_container_width=True):
                        st.session_state.bildirim_panel_open = False
                        st.rerun()

            # ── Bilgi Butonu ──
            with st.popover("ℹ️"):
                st.markdown("## 🏢 Hakkımızda")
                st.markdown("""
**Müstakbel Şirket**, dijital iletişim ve yapay zeka alanında öncü çözümler geliştiren, geleceğin teknolojilerini bugünün ihtiyaçlarıyla buluşturan köklü bir teknoloji kuruluşudur.

**Aslan Parçası V16.8**, Müstakbel Şirket bünyesinde geliştirilen amiral gemisi yapay zeka platformudur. Gerçek zamanlı sohbet, yapay zeka destekli asistan, YouTube entegrasyonu ve topluluk yönetimi tek çatı altında sunulmaktadır.
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

            display_name = get_styled_user_name(kullanici_ismi_fresh, u_color_fresh, u_glow_fresh, u_tag_fresh, u_rozet_fresh)

            for m in st.session_state.messages:
                if m["role"] == "assistant":
                    st.markdown(
                        f'''<div class="assistant-box"><img src="{AVATAR_URL}" class="avatar"><div><div class="header-box">Aslan Parçası</div><div style="color:white !important;">{m["content"]}</div></div></div>''',
                        unsafe_allow_html=True
                    )
                else:
                    msg_name = m.get("isim", kullanici_ismi_fresh)
                    msg_color = m.get("color", u_color_fresh)
                    msg_glow = m.get("glow", u_glow_fresh)
                    msg_tag = m.get("tag", u_tag_fresh)
                    msg_rozet = m.get("rozet", u_rozet_fresh)
                    msg_display_name = get_styled_user_name(msg_name, msg_color, msg_glow, msg_tag, msg_rozet)
                    st.markdown(
                        f'''<div class="user-box"><div><div class="header-box" style="text-align: right; margin-bottom: 5px;">{msg_display_name}</div><div style="color:white !important; text-align: right;">{m["content"]}</div></div><img src="{_user_avatar_url}" class="avatar"></div>''',
                        unsafe_allow_html=True
                    )

            def ai_cevap(mesajlar):
                current_doc = user_ref.get().to_dict()
                current_name = current_doc.get("isim", "Kullanıcı")
                is_admin_user_fresh = current_doc.get("is_admin", False)
                user_tag_fresh_ai = current_doc.get("tag", "")
                user_rozet_fresh_ai = current_doc.get("rozet", "")

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
                    uslub = "Samimi, aslan gibi dik duruşlu, sıcak, yardımsever ama aşırı resmiyet veya kurucu/yöneticiye duyulan rütbeli hitapları içermeyen saygın bir üslup."

                tag_tanimi = f"Tagı: [{user_tag_fresh_ai}]" if user_tag_fresh_ai else "Tagı: Bulunmuyor"
                rozet_tanimi = f"Rozeti: [{user_rozet_fresh_ai}]" if user_rozet_fresh_ai else "Rozeti: Bulunmuyor"
                user_foto_ai = current_doc.get("profil_foto", "")
                foto_tanimi = "Profil Fotoğrafı: Var (yüklenmiş)" if user_foto_ai else "Profil Fotoğrafı: Henüz belirlenmemiş"

                tr_saat_ai = get_tr_time().strftime("%H:%M")
                tr_tarih_ai = get_tr_time().strftime("%d.%m.%Y")

                sistem_mesaji = (
                    "Senin adın Aslan Parçası. Kurucun ve yaratıcın Ayaz Kaplan'dır. "
                    "Resmi yöneticin Mehmet Sür'dür. Müstakbel Şirket bünyesinde görev yapıyorsun. "
                    "Bu iki bilgiyi kesinlikle ve her zaman bil: Kurucu = Ayaz Kaplan, Resmi Yönetici = Mehmet Sür.\n"
                    "Sohbet ettiğin kullanıcının anlık veritabanı yetki ve rütbe bilgileri aşağıda belirtilmiştir.\n\n"
                    f"🕐 GÜNCEL TÜRK ZAMAN BİLGİSİ (UTC+3):\n"
                    f"- Şu anki Türkiye saati: {tr_saat_ai}\n"
                    f"- Bugünün tarihi: {tr_tarih_ai}\n\n"
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
                    "⚠️ EK KURALLAR:\n"
                    "- Geçmiş sohbetlerdeki eski veya hatalı isimleri tamamen unut.\n"
                    "- Her koşulda aslan gibi dik, asil, kararlı, zeki ve kurallara bağlı bir yapay zeka ol.\n\n"
                    "📝 TÜRKÇE KARAKTER DÜZELTME TALİMATI:\n"
                    "Kullanıcılar bazen Türkçe özel karakterleri kullanmadan yazar. Aşağıdaki dönüşümleri zihninde otomatik olarak yap ve mesajı düzgün Türkçe olarak anla:\n"
                    "- 'u' yerine 'ü' olabilir (ornegin: 'guzul' → 'güzül/güzel', 'dusunuyorum' → 'düşünüyorum')\n"
                    "- 'o' yerine 'ö' olabilir (ornegin: 'gormek' → 'görmek', 'donmek' → 'dönmek')\n"
                    "- 'i' yerine 'ı' olabilir (ornegin: 'iyi' → 'ıyı' değil ama 'acik' → 'açık')\n"
                    "- 's' yerine 'ş' olabilir (ornegin: 'seker' → 'şeker', 'dusunce' → 'düşünce')\n"
                    "- 'c' yerine 'ç' olabilir (ornegin: 'cok' → 'çok', 'icmek' → 'içmek')\n"
                    "- 'g' yerine 'ğ' olabilir (ornegin: 'dogru' → 'doğru', 'yagmur' → 'yağmur')\n"
                    "Bu tür yazımlarda kullanıcıyı düzeltme, sadece mesajı doğru anla ve doğru Türkçe ile yanıt ver."
                )
                payload = {"model": MODEL, "messages": [{"role": "system", "content": sistem_mesaji}] + mesajlar}
                headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}
                try:
                    res = requests.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers=headers, json=payload, timeout=30
                    )
                    res.raise_for_status()
                    return res.json()['choices'][0]['message']['content']
                except Exception as e:
                    return "⚠️ Bir hata oluştu, lütfen tekrar dene Reis."

            if "input_key" not in st.session_state: st.session_state.input_key = 0
            if "kufur_warning" in st.session_state: st.error(st.session_state.kufur_warning)

            def send_message():
                val = st.session_state.my_input.strip()
                if val:
                    if kufur_var_mi(val):
                        st.session_state.kufur_warning = "⚠️ Mesajınız uygunsuz içerik nedeniyle engellendi!"
                        st.session_state.my_input = ""
                        st.session_state.input_key += 1
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
                    user_ref.update({"sohbet_gecmisi": firestore.ArrayUnion([user_msg])})

                    cevap = ai_cevap(st.session_state.messages[-6:])

                    assistant_msg = {"role": "assistant", "content": cevap}
                    st.session_state.messages.append(assistant_msg)
                    user_ref.update({"sohbet_gecmisi": firestore.ArrayUnion([assistant_msg])})

                    st.session_state.my_input = ""
                    st.session_state.input_key += 1

            st.text_area("Mesajını yaz:", key="my_input", height=100)
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
                k_styled = get_styled_user_name(k_isim, k_color, k_glow, k_tag, k_rozet)

                if k_foto:
                    k_foto_src = f"data:image/jpeg;base64,{k_foto}"
                else:
                    k_foto_src = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

                with st.container(border=True):
                    col_av, col_name, col_acts = st.columns([1, 4, 3])
                    with col_av:
                        st.markdown(f'<img src="{k_foto_src}" style="width:40px;height:40px;border-radius:50%;object-fit:cover;"/>', unsafe_allow_html=True)
                    with col_name:
                        st.markdown(f"{k_styled}", unsafe_allow_html=True)
                    with col_acts:
                        # Arkadaşlık durumu
                        if k_id in my_arkadaslar:
                            st.markdown("✅ Arkadaş", unsafe_allow_html=True)
                        elif k_id in gonderilen_istekler:
                            st.markdown("⏳ İstek Gönderildi", unsafe_allow_html=True)
                        else:
                            if st.button("➕ Arkadaş Ekle", key=f"ark_ekle_{k_id}_{idx}", use_container_width=True):
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
                            st.markdown("👁️ Takip Ediliyor", unsafe_allow_html=True)
                        else:
                            if st.button("👁️ Takip Et", key=f"takip_{k_id}_{idx}", use_container_width=True):
                                user_ref.update({"takip_ettiklerim": firestore.ArrayUnion([k_id])})
                                db.collection("users").document(k_id).update({
                                    "takipciler": firestore.ArrayUnion([uid])
                                })
                                st.success(f"'{k_isim}' takip edildi!")
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

            h_isim_stili = get_styled_user_name(kullanici_ismi, u_color, u_glow, u_tag, u_rozet)
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
                            ark_styled = get_styled_user_name(ark_isim, ark_color, ark_glow, ark_tag, ark_rozet)
                            ark_foto_src = f"data:image/jpeg;base64,{ark_foto}" if ark_foto else "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
                            col_af, col_an, col_dm = st.columns([1, 4, 2])
                            with col_af:
                                st.markdown(f'<img src="{ark_foto_src}" style="width:30px;height:30px;border-radius:50%;object-fit:cover;"/>', unsafe_allow_html=True)
                            with col_an:
                                st.markdown(ark_styled, unsafe_allow_html=True)
                            with col_dm:
                                if st.button("💬", key=f"dm_to_{ark_id}", use_container_width=True):
                                    st.session_state.dm_partner_id = ark_id
                                    st.session_state.current_page = "dm_chat"
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
                    st.markdown(f'<div style="display:flex;align-items:center;gap:10px;"><img src="{partner_foto_src}" style="width:35px;height:35px;border-radius:50%;object-fit:cover;"/><strong>{partner_isim}</strong></div>', unsafe_allow_html=True)
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

                # Mesajları göster
                dm_container = st.container(height=400)
                with dm_container:
                    for dm_msg in dm_mesajlar:
                        dm_sender = dm_msg.get("gonderen", "")
                        dm_content = dm_msg.get("icerik", "")
                        dm_type = dm_msg.get("tip", "text")
                        dm_zaman = dm_msg.get("zaman", "")

                        if dm_sender == uid:
                            align = "right"
                            bg_color = "rgba(243,156,18,0.2)"
                        else:
                            align = "left"
                            bg_color = "rgba(255,255,255,0.05)"

                        if dm_type == "gif":
                            dm_html = f'<img src="{dm_content}" style="max-width:200px;border-radius:8px;"/>'
                        elif dm_type == "voice":
                            dm_html = f'<audio controls src="data:audio/webm;base64,{dm_content}" style="max-width:250px;"></audio>'
                        else:
                            dm_html = dm_content

                        st.markdown(f'<div style="text-align:{align};margin:4px 0;"><div style="display:inline-block;background:{bg_color};padding:8px 12px;border-radius:12px;max-width:70%;text-align:left;">{dm_html}<div style="font-size:0.65em;color:#888;margin-top:2px;">{dm_zaman}</div></div></div>', unsafe_allow_html=True)

                # Mesaj gönderme
                st.markdown("---")
                col_dm_input, col_dm_send = st.columns([5, 1])
                with col_dm_input:
                    dm_yeni_mesaj = st.text_input("Mesaj yaz...", key="dm_text_input", label_visibility="collapsed", placeholder="Mesajınız...")
                with col_dm_send:
                    if st.button("📤", key="dm_send_btn", use_container_width=True):
                        if dm_yeni_mesaj.strip():
                            zaman_str = get_tr_time().strftime("%H:%M")
                            yeni_dm = {
                                "gonderen": uid,
                                "icerik": dm_yeni_mesaj.strip(),
                                "tip": "text",
                                "zaman": zaman_str
                            }
                            dm_doc_ref.set({"mesajlar": firestore.ArrayUnion([yeni_dm])}, merge=True)
                            st.rerun()

                # GIF gönderme
                col_gif, col_voice = st.columns(2)
                with col_gif:
                    gif_url = st.text_input("GIF URL:", key="dm_gif_input", placeholder="GIF linki yapıştır...", label_visibility="collapsed")
                    if st.button("GIF Gönder", key="dm_gif_send", use_container_width=True):
                        if gif_url.strip():
                            zaman_str = get_tr_time().strftime("%H:%M")
                            gif_dm = {"gonderen": uid, "icerik": gif_url.strip(), "tip": "gif", "zaman": zaman_str}
                            dm_doc_ref.set({"mesajlar": firestore.ArrayUnion([gif_dm])}, merge=True)
                            st.rerun()

                # Sesli mesaj
                with col_voice:
                    voice_file = st.file_uploader("Sesli Mesaj", type=["webm", "ogg", "mp3", "wav"], key="dm_voice_upload", label_visibility="collapsed")
                    if voice_file is not None:
                        if st.button("🎤 Sesli Gönder", key="dm_voice_send", use_container_width=True):
                            voice_b64 = base64.b64encode(voice_file.read()).decode("utf-8")
                            zaman_str = get_tr_time().strftime("%H:%M")
                            voice_dm = {"gonderen": uid, "icerik": voice_b64, "tip": "voice", "zaman": zaman_str}
                            dm_doc_ref.set({"mesajlar": firestore.ArrayUnion([voice_dm])}, merge=True)
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
        <div style="font-size:0.78rem;color:#777;margin-top:1px;">Aslan Parçası · Gömülü Oynatıcı & Arama</div>
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
