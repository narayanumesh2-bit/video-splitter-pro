import sys
import subprocess
import os

# Auto-install yt-dlp if missing
try:
    import yt_dlp
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
    import yt_dlp

import shutil
import zipfile
import streamlit as st

st.set_page_config(page_title="Universal Video Splitter Pro", page_icon="⚡", layout="wide")

# Modern Dark UI
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
    }
    .main-card {
        background: rgba(30, 41, 59, 0.75);
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
st.caption("हाई-स्पीड वीडियो स्प्लिटर, ऑटो-कटर इंजन और एंटी-कॉपीराइट इफ़ेक्ट्स")

TEMP_DIR = "temp_processing"
OUTPUT_DIR = "output_clips"
for folder in [TEMP_DIR, OUTPUT_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

st.markdown('<div class="main-card">', unsafe_allow_html=True)
input_choice = st.radio("सोर्स चुनें:", ["🌐 All Links / Websites / APKs", "📁 गैलरी से अपलोड करें"], horizontal=True)

if input_choice == "🌐 All Links / Websites / APKs":
    url = st.text_input("वीडियो लिंक पेस्ट करें (YouTube, Movie Apps, M3U8, Direct MP4, Web Links):", placeholder="https://...")
    if url and st.button("📥 लोड करें"):
        with st.spinner("वीडियो लोड हो रही है..."):
            for f in os.listdir(TEMP_DIR):
                try:
                    os.remove(os.path.join(TEMP_DIR, f))
                except Exception:
                    pass

            download_success = False
            output_template = f'{TEMP_DIR}/input_video.%(ext)s'

            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': output_template,
                'quiet': True,
                'no_warnings': True,
                'geo_bypass': True,
                'geo_bypass_country': 'IN',
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
            except Exception:
                try:
                    direct_out = os.path.join(TEMP_DIR, "input_video.mp4")
                    fallback_cmd = f'ffmpeg -y -headers "User-Agent: Mozilla/5.0" -i "{url}" -c copy -bsf:a aac_adtstoasc "{direct_out}"'
                    subprocess.run(fallback_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    if os.path.exists(direct_out) and os.path.getsize(direct_out) > 1000:
                        download_success = True
                    else:
                        raise Exception("FFMPEG fallback failed")
                except Exception:
                    st.error("डाउनलोड एरर: वीडियो लोड नहीं हो पाया। लिंक चेक करें।")

            files = [os.path.join(TEMP_DIR, f) for f in os.listdir(TEMP_DIR) if not f.endswith('.part')]
            if download_success and files:
                st.session_state['loaded_video'] = files[0]
                st.success("✅ वीडियो सफलतापूर्वक लोड हो गया!")

else:
    uploaded_file = st.file_uploader("फ़ाइल चुनें (MP4, MKV, MOV, TS, AVI - 10GB तक)", type=["mp4", "mkv", "mov", "ts", "avi"])
    if uploaded_file:
        save_path = os.path.join(TEMP_DIR, uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.read())
        st.session_state['loaded_video'] = save_path
        st.success("✅ फ़ाइल अपलोड हो गई!")
st.markdown('</div>', unsafe_allow_html=True)

# वीडियो प्रोसेसिंग और एंटी-कॉपीराइट सेटिंग्स
if 'loaded_video' in st.session_state and os.path.exists(st.session_state['loaded_video']):
    target_video = st.session_state['loaded_video']
    
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("⚙️ कस्टमाइज़ेशन, कटिंग और एंटी-कॉपीराइट इफ़ेक्ट्स")
    
    col1, col2 = st.columns(2)
    with col1:
        split_mode = st.selectbox(
            "पार्ट ड्यूरेशन चुनें:",
            ["50 Seconds (Shorts/Reels)", "1 Minute", "5 Minutes", "10 Minutes", "15 Minutes", "20 Minutes", "25 Minutes", "30 Minutes", "35 Minutes", "1 Hour"]
        )
        time_map = {
            "50 Seconds (Shorts/Reels)": 50, "1 Minute": 60, "5 Minutes": 300,
            "10 Minutes": 600, "15 Minutes": 900, "20 Minutes": 1200, 
            "25 Minutes": 1500, "30 Minutes": 1800, "35 Minutes": 2100, "1 Hour": 3600
        }
        chunk_seconds = time_map[split_mode]

    with col2:
        anti_audio = st.toggle("🎵 Sound Modulator & Pitch Shift (Anti-Copyright)", value=True)
        anti_video = st.toggle("🎨 Video Color Filter & Micro-Zoom (Anti-Copyright)", value=True)
        anti_flip = st.toggle("🔄 Horizontal Flip (Mirror Effect)", value=False)
        shorts_crop = st.toggle("📱 9:16 Shorts/Reels Crop Mode", value=False)

    if st.button("🚀 चॉपिंग और इफ़ेक्ट्स प्रोसेस शुरू करें"):
        with st.spinner("प्रोसेसिंग, इफ़ेक्ट्स अप्लाइ और कटिंग जारी है..."):
            for f in os.listdir(OUTPUT_DIR):
                try:
                    os.remove(os.path.join(OUTPUT_DIR, f))
                except Exception:
                    pass

            duration_cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{target_video}"'
            try:
                total_duration = float(subprocess.check_output(duration_cmd, shell=True).decode().strip())
            except Exception:
                total_duration = 0

            # Video Filters Setup
            v_filters = []
            if anti_video:
                # Slight zoom + Color adjustment + subtle vignette to break visual match
                v_filters.append("scale=1.02*iw:1.02*ih,crop=iw/1.02:ih/1.02")
                v_filters.append("eq=contrast=1.05:brightness=0.01:saturation=1.10:gamma=1.02")
            if anti_flip:
                v_filters.append("hflip")
            if shorts_crop:
                v_filters.append("crop=ih*(9/16):ih")

            # Audio Filters Setup
            a_filters = []
            if anti_audio:
                # 3% pitch shift + frequency re-balance to destroy audio fingerprint
                a_filters.append("asetrate=44100*1.03,aresample=44100,atempo=1/1.03,equalizer=f=120:width_type=h:width=50:g=2")

            vf_arg = f'-vf "{",".join(v_filters)}"' if v_filters else ""
            af_arg = f'-af "{",".join(a_filters)}"' if a_filters else ""

            start_time = 0
            part_num = 1
            clip_files = []
            progress_bar = st.progress(0)

            while start_time < total_duration or total_duration == 0:
                output_file = os.path.join(OUTPUT_DIR, f"part_{part_num:03d}.mp4")
                ffmpeg_cmd = (
                    f'ffmpeg -y -ss {start_time} -t {chunk_seconds} -i "{target_video}" '
                    f'{vf_arg} {af_arg} -map_metadata -1 -preset ultrafast -c:v libx264 -crf 23 -c:a aac -b:a 128k "{output_file}"'
                )
                subprocess.run(ffmpeg_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                if os.path.exists(output_file) and os.path.getsize(output_file) > 1000:
                    clip_files.append(output_file)
                else:
                    break

                start_time += chunk_seconds
                part_num += 1
                if total_duration > 0:
                    progress_bar.progress(min(start_time / total_duration, 1.0))

            if clip_files:
                zip_filename = "split_videos.zip"
                with zipfile.ZipFile(zip_filename, 'w') as zipf:
                    for file in clip_files:
                        zipf.write(file, os.path.basename(file))

                st.success(f"🎉 कुल {len(clip_files)} पार्ट्स एंटी-कॉपीराइट इफ़ेक्ट्स के साथ तैयार!")
                with open(zip_filename, "rb") as f:
                    st.download_button("📦 Download All (ZIP)", data=f, file_name="split_videos.zip", mime="application/zip")
            else:
                st.error("वीडियो कटिंग में समस्या आई।")
    st.markdown('</div>', unsafe_allow_html=True)
