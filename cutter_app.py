import os
import shutil
import subprocess
import zipfile
import streamlit as st
import yt_dlp

st.set_page_config(page_title="Universal Video Splitter Pro", page_icon="⚡", layout="wide")

# Modern Dark & Glassmorphism UI
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
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder, exist_ok=True)

st.markdown('<div class="main-card">', unsafe_allow_html=True)
input_choice = st.radio("सोर्स चुनें:", ["🌐 All Links / Websites", "📁 गैलरी से अपलोड करें"], horizontal=True)

video_path = None

if input_choice == "🌐 All Links / Websites":
    url = st.text_input("वीडियो लिंक पेस्ट करें:", placeholder="https://...")
    if url and st.button("📥 लोड करें"):
        with st.spinner("वीडियो स्ट्रीम लोड हो रही है..."):
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': f'{TEMP_DIR}/input_video.%(ext)s',
                'quiet': True,
                'no_warnings': True,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'nocheckcertificate': True,
            }
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                files = [os.path.join(TEMP_DIR, f) for f in os.listdir(TEMP_DIR) if not f.endswith('.part')]
                if files:
                    st.session_state['loaded_video'] = files[0]
                    st.success("✅ वीडियो लोड हो गया!")
            except Exception as e:
                st.error(f"लिंक एरर: {e}")
else:
    uploaded_file = st.file_uploader("फ़ाइल चुनें (MP4, MKV, MOV, TS)", type=["mp4", "mkv", "mov", "ts", "avi"])
    if uploaded_file:
        save_path = os.path.join(TEMP_DIR, uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.read())
        st.session_state['loaded_video'] = save_path
        st.success("✅ फ़ाइल अपलोड हो गई!")
st.markdown('</div>', unsafe_allow_html=True)

if 'loaded_video' in st.session_state and os.path.exists(st.session_state['loaded_video']):
    target_video = st.session_state['loaded_video']
    
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("⚙️ कस्टमाइज़ेशन और स्प्लिट सेटिंग्स")
    
    col1, col2 = st.columns(2)
    with col1:
        split_mode = st.selectbox(
            "पार्ट ड्यूरेशन:",
            ["50 Seconds (Shorts/Reels)", "1 Minute", "5 Minutes", "15 Minutes", "20 Minutes", "25 Minutes", "30 Minutes", "35 Minutes", "1 Hour"]
        )
        time_map = {
            "50 Seconds (Shorts/Reels)": 50, "1 Minute": 60, "5 Minutes": 300, 
            "15 Minutes": 900, "20 Minutes": 1200, "25 Minutes": 1500, 
            "30 Minutes": 1800, "35 Minutes": 2100, "1 Hour": 3600
        }
        chunk_seconds = time_map[split_mode]

    with col2:
        anti_pitch = st.toggle("🛡️ Audio Pitch Shift", value=True)
        anti_color = st.toggle("🛡️ Visual Color Correction", value=True)
        anti_flip = st.toggle("🛡️ Horizontal Flip", value=False)
        shorts_crop = st.toggle("📱 9:16 Shorts Mode", value=False)

    if st.button("🚀 चॉपिंग शुरू करें"):
        with st.spinner("प्रोसेसिंग जारी है..."):
            duration_cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{target_video}"'
            try:
                total_duration = float(subprocess.check_output(duration_cmd, shell=True).decode().strip())
            except Exception:
                total_duration = 0

            v_filters, a_filters = [], []
            if anti_pitch:
                a_filters.append("asetrate=44100*1.03,aresample=44100,atempo=1/1.03,equalizer=f=60:width_type=h:width=50:g=3")
            if anti_color:
                v_filters.append("eq=contrast=1.06:brightness=0.01:saturation=1.12")
            if anti_flip:
                v_filters.append("hflip")
            if shorts_crop:
                v_filters.append("crop=ih*(9/16):ih")

            vf_arg = f'-vf "{",".join(v_filters)}"' if v_filters else ""
            af_arg = f'-af "{",".join(a_filters)}"' if a_filters else ""

            start_time, part_num, clip_files = 0, 1, []
            progress_bar = st.progress(0)

            while start_time < total_duration:
                output_file = os.path.join(OUTPUT_DIR, f"part_{part_num:03d}.mp4")
                ffmpeg_cmd = (
                    f'ffmpeg -y -ss {start_time} -t {chunk_seconds} -i "{target_video}" '
                    f'{vf_arg} {af_arg} -map_metadata -1 -preset ultrafast -c:v libx264 -crf 23 -c:a aac -b:a 128k "{output_file}"'
                )
                subprocess.run(ffmpeg_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if os.path.exists(output_file):
                    clip_files.append(output_file)
                start_time += chunk_seconds
                part_num += 1
                if total_duration > 0:
                    progress_bar.progress(min(start_time / total_duration, 1.0))

            zip_filename = "split_videos.zip"
            with zipfile.ZipFile(zip_filename, 'w') as zipf:
                for file in clip_files:
                    zipf.write(file, os.path.basename(file))

            st.success(f"🎉 कुल {len(clip_files)} पार्ट्स तैयार हो गए!")
            with open(zip_filename, "rb") as f:
                st.download_button("📦 Download All (ZIP)", data=f, file_name="split_videos.zip", mime="application/zip")
    st.markdown('</div>', unsafe_allow_html=True)
