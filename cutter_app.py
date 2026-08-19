import os
import shutil
import subprocess
import zipfile
import urllib.request
import streamlit as st
import yt_dlp

st.set_page_config(page_title="Universal Video Splitter Pro", page_icon="⚡", layout="wide")

# Modern Dark UI
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
    }
    .main-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    .stButton>button {
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(168, 85, 247, 0.4);
    }
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚡ Universal Video Splitter Pro")
st.caption("हाई-स्पीड वीडियो स्प्लिटर और ऑटो-कटर इंजन")

TEMP_DIR = "temp_processing"
OUTPUT_DIR = "output_clips"
for folder in [TEMP_DIR, OUTPUT_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

st.markdown('<div class="main-card">', unsafe_allow_html=True)
input_choice = st.radio("सोर्स चुनें:", ["🌐 All Links / Websites", "📁 गैलरी से अपलोड करें"], horizontal=True)

if input_choice == "🌐 All Links / Websites":
    url = st.text_input("वीडियो लिंक पेस्ट करें (YouTube, Movie Apps, M3U8, Direct MP4, Web Links):", placeholder="https://...")
    if url and st.button("📥 लोड करें"):
        with st.spinner("वीडियो फेच और लोड हो रही है..."):
            # पुराना डेटा साफ़ करें
            for f in os.listdir(TEMP_DIR):
                try:
                    os.remove(os.path.join(TEMP_DIR, f))
                except Exception:
                    pass

            download_success = False
            output_template = f'{TEMP_DIR}/input_video.%(ext)s'

            # 1. Primary: yt-dlp with India Geo Bypass + Mobile Client Simulation
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': output_template,
                'quiet': True,
                'no_warnings': True,
                'geo_bypass': True,
                'geo_bypass_country': 'IN',
                'geo_verification_proxy': None,
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android', 'ios', 'mweb', 'web'],
                        'player_skip': ['webpage', 'configs']
                    }
                },
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36',
                    'Accept-Language': 'en-IN,en;q=0.9,hi;q=0.8',
                },
                'nocheckcertificate': True,
                'ignoreerrors': False,
            }

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                download_success = True
            except Exception as e1v
