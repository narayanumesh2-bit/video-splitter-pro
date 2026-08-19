import sys
import subprocess
import os

# Auto install yt-dlp if missing
try:
    import yt_dlp
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "yt-dlp"], check=False)
    import yt_dlp

import shutil
import zipfile
import streamlit as st

st.set_page_config(page_title="Universal Video Splitter Ultra Pro", page_icon="⚡", layout="wide")

# Modern UI Styling
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); color: #f8fafc; }
    .main-card { background: rgba(30, 41, 59, 0.75); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 16px; padding: 24px; margin-bottom: 20px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37); }
    .stButton>button { background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%); color: white; border: none; border-radius: 10px; padding: 12px 24px; font-weight: 600; width: 100%; }
    h1, h2, h3 { color: #ffffff !important; font-weight: 700 !important; }
</style>
""", unsafe_allow_html=True)

st.title("⚡ Universal Video Splitter Ultra Pro")
st.caption("हाई-स्पीड वीडियो स्प्लिटर और एंटी-कॉपीराइट इंजन")

TEMP_DIR, OUTPUT_DIR = "temp_processing", "output_clips"
for folder in [TEMP_DIR, OUTPUT_DIR]:
    if not os.path.exists(folder): os.makedirs(folder, exist_ok=True)

st.markdown('<div class="main-card">', unsafe_allow_html=True)
input_choice = st.radio("सोर्स चुनें:", ["🌐 All Links / Websites / APKs", "📁 गैलरी से अपलोड करें"], horizontal=True)

if input_choice == "🌐 All Links / Websites / APKs":
    url = st.text_input("वीडियो लिंक पेस्ट करें:", placeholder="https://...")
    if url and st.button("📥 लोड करें"):
        with st.spinner("वीडियो लोड हो रही है..."):
            for f in os.listdir(TEMP_DIR): 
                try: os.remove(os.path.join(TEMP_DIR, f))
                except: pass
            
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': f'{TEMP_DIR}/input_video.%(ext)s',
                'quiet': True, 'geo_bypass': True, 'geo_bypass_country': 'IN',
                'http_headers': {'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36'},
                'nocheckcertificate': True
            }
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl: ydl.download([url])
                st.session_state['loaded_video'] = os.path.join(TEMP_DIR, "input_video.mp4")
                st.success("✅ वीडियो लोड हो गया!")
            except: st.error("वीडियो लोड नहीं हो पाया।")

else:
    uploaded_file = st.file_uploader("फ़ाइल चुनें (10GB तक)", type=["mp4", "mkv", "mov", "ts", "avi"])
    if uploaded_file:
        save_path = os.path.join(TEMP_DIR, uploaded_file.name)
        with open(save_path, "wb") as f: f.write(uploaded_file.read())
        st.session_state['loaded_video'] = save_path
        st.success("✅ फ़ाइल अपलोड हो गई!")
st.markdown('</div>', unsafe_allow_html=True)

if 'loaded_video' in st.session_state and os.path.exists(st.session_state['loaded_video']):
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        options = ["50 Seconds", "1 Minute", "5 Minutes", "10 Minutes", "15 Minutes", "20 Minutes", "25 Minutes", "30 Minutes", "35 Minutes", "40 Minutes", "1 Hour"]
        time_map = {"50 Seconds": 50, "1 Minute": 60, "5 Minutes": 300, "10 Minutes": 600, "15 Minutes": 900, "20 Minutes": 1200, "25 Minutes": 1500, "30 Minutes": 1800, "35 Minutes": 2100, "40 Minutes": 2400, "1 Hour": 3600}
        split_mode = st.selectbox("पार्ट ड्यूरेशन चुनें:", options)
        chunk_seconds = time_map[split_mode]
    with col2:
        anti_audio = st.toggle("🎵 Anti-Copyright Audio", value=True)
        anti_video = st.toggle("🎨 Anti-Copyright Visuals", value=True)
        shorts_crop = st.toggle("📱 9:16 Crop Mode", value=False)

    if st.button("🚀 चॉपिंग शुरू करें"):
        with st.spinner("प्रोसेसिंग जारी है..."):
            for f in os.listdir(OUTPUT_DIR): 
                try: os.remove(os.path.join(OUTPUT_DIR, f))
                except: pass
            
            total_duration = float(subprocess.check_output(f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{st.session_state["loaded_video"]}"', shell=True).decode().strip())
            
            v_filters = ["scale=1.02*iw:1.02*ih,crop=iw/1.02:ih/1.02,eq=contrast=1.05:saturation=1.10"]
            if shorts_crop: v_filters.append("crop=ih*(9/16):ih")
            a_filters = ["asetrate=44100*1.03,aresample=44100,atempo=1/1.03"] if anti_audio else []
            
            vf_arg = f'-vf "{",".join(v_filters)}"'
            af_arg = f'-af "{",".join(a_filters)}"' if a_filters else ""

            start, part = 0, 1
            while start < total_duration:
                out = os.path.join(OUTPUT_DIR, f"part_{part:03d}.mp4")
                subprocess.run(f'ffmpeg -y -ss {start} -t {chunk_seconds} -i "{st.session_state["loaded_video"]}" {vf_arg} {af_arg} -map_metadata -1 -preset ultrafast -c:v libx264 -crf 23 -c:a aac -b:a 128k "{out}"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                start += chunk_seconds
                part += 1
            
            st.success(f"🎉 {part-1} पार्ट्स तैयार!")
            with zipfile.ZipFile("split.zip", 'w') as z:
                for f in os.listdir(OUTPUT_DIR): z.write(os.path.join(OUTPUT_DIR, f), f)
            with open("split.zip", "rb") as f: st.download_button("📦 Download All (ZIP)", data=f, file_name="split.zip")
    st.markdown('</div>', unsafe_allow_html=True)
