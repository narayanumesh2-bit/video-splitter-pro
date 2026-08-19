import os
import shutil
import subprocess
import zipfile
import streamlit as st
import yt_dlp

st.set_page_config(page_title="Universal Video Splitter & Anti-Copyright Engine", layout="wide")

st.title("🎬 Universal Video Splitter & Anti-Copyright Engine")
st.markdown("किसी भी ऐप/वेबसाइट (YouTube, Facebook, Insta, Picasso, MovieBox, Direct Links) का वीडियो लिंक डालें, टाइमर चुनें और अपने आप कटे हुए पार्ट्स डाउनलोड करें।")

# डायरेक्टरी मैनेजमेंट
TEMP_DIR = "temp_processing"
OUTPUT_DIR = "output_clips"
for folder in [TEMP_DIR, OUTPUT_DIR]:
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder, exist_ok=True)

# इनपुट सोर्स
input_choice = st.radio(
    "वीडियो का सोर्स चुनें:", 
    ["🌐 ऑनलाइन लिंक (YouTube, Facebook, Insta, Picasso, MovieBox, Direct Link)", "📁 डिवाइस से वीडियो अपलोड करें"]
)

video_path = None

if input_choice == "🌐 ऑनलाइन लिंक (YouTube, Facebook, Insta, Picasso, MovieBox, Direct Link)":
    url = st.text_input("यहाँ वीडियो का URL / लिंक पेस्ट करें:")
    if url and st.button("📥 वीडियो लोड करें"):
        with st.spinner("वीडियो स्ट्रीम फ़ेच हो रही है (यह वीडियो की लंबाई पर निर्भर करता है)..."):
            # यूनिवर्सल डाउनलोडर सेटिंग्स (सभी ऐप्स और थर्ड पार्टी लिंक्स के लिए)
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': f'{TEMP_DIR}/input_video.%(ext)s',
                'quiet': True,
                'no_warnings': True,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'nocheckcertificate': True,
                'ignoreerrors': False,
            }
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                files = [os.path.join(TEMP_DIR, f) for f in os.listdir(TEMP_DIR) if not f.endswith('.part')]
                if files:
                    st.session_state['loaded_video'] = files[0]
                    st.success("✅ वीडियो सफलतापूर्वक लोड हो गया!")
            except Exception as e:
                st.error(f"❌ वीडियो डाउनलोड नहीं हो पाया: {e} (यदि लिंक में DRM प्रोटेक्शन है तो वीडियो सीधे अपलोड करें)")
else:
    uploaded_file = st.file_uploader("फ़ाइल चुनें (.mp4, .mkv, .mov)", type=["mp4", "mkv", "mov"])
    if uploaded_file:
        save_path = os.path.join(TEMP_DIR, uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.read())
        st.session_state['loaded_video'] = save_path
        st.success("✅ फ़ाइल सफलतापूर्वक अपलोड हो गई!")

# वीडियो सेटिंग्स और चॉपिंग इंजन
if 'loaded_video' in st.session_state and os.path.exists(st.session_state['loaded_video']):
    target_video = st.session_state['loaded_video']
    st.divider()
    
    st.subheader("⚙️ स्प्लिट सेटिंग्स और एंटी-कॉपीराइट इंजन")
    
    col1, col2 = st.columns(2)
    
    with col1:
        split_mode = st.selectbox(
            "हर पार्ट की समय सीमा (Duration):",
            [
                "50 Seconds (Shorts/Reels)",
                "1 Minute",
                "5 Minutes",
                "15 Minutes",
                "20 Minutes",
                "25 Minutes",
                "30 Minutes",
                "35 Minutes",
                "1 Hour"
            ]
        )
        time_map = {
            "50 Seconds (Shorts/Reels)": 50,
            "1 Minute": 60,
            "5 Minutes": 300,
            "15 Minutes": 900,
            "20 Minutes": 1200,
            "25 Minutes": 1500,
            "30 Minutes": 1800,
            "35 Minutes": 2100,
            "1 Hour": 3600
        }
        chunk_seconds = time_map[split_mode]

    with col2:
        anti_pitch = st.toggle("🛡️ Audio Pitch & Tempo Shift (1.03x + EQ Boost)", value=True)
        anti_color = st.toggle("🛡️ Visual Color & Contrast Shift", value=True)
        anti_flip = st.toggle("🛡️ Horizontal Flip (Mirror Image)", value=False)
        shorts_crop = st.toggle("📱 9:16 Shorts/Reels Crop Mode", value=False)

    if st.button("🚀 चॉपिंग शुरू करें (Start Auto-Split)"):
        with st.spinner("वीडियो के पार्ट्स कट रहे हैं और एंटी-कॉपीराइट फिल्टर्स लग रहे हैं..."):
            
            # वीडियो की कुल अवधि (Total Duration) प्राप्त करना
            duration_cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{target_video}"'
            try:
                total_duration = float(subprocess.check_output(duration_cmd, shell=True).decode().strip())
            except Exception:
                total_duration = 0

            # फ़िल्टर्स तैयार करना
            v_filters = []
            a_filters = []

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

            # ऑटो स्प्लिट लूप (पूरे वीडियो को चुने हुए समय के अनुसार टुकड़ों में बांटना)
            start_time = 0
            part_num = 1
            clip_files = []

            while start_time < total_duration:
                output_file = os.path.join(OUTPUT_DIR, f"part_{part_num:03d}.mp4")
                
                # -map_metadata -1 ओरिजिनल फाइल की डिजिटल पहचान हटा देता है
                ffmpeg_cmd = (
                    f'ffmpeg -y -ss {start_time} -t {chunk_seconds} -i "{target_video}" '
                    f'{vf_arg} {af_arg} -map_metadata -1 -preset ultrafast -c:v libx264 -crf 23 -c:a aac -b:a 128k "{output_file}"'
                )
                
                subprocess.run(ffmpeg_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                if os.path.exists(output_file):
                    clip_files.append(output_file)
                
                start_time += chunk_seconds
                part_num += 1

            # सभी क्लिप्स की एक ज़िप फ़ाइल बनाना
            zip_filename = "all_split_clips.zip"
            with zipfile.ZipFile(zip_filename, 'w') as zipf:
                for file in clip_files:
                    zipf.write(file, os.path.basename(file))

            st.success(f"🎉 काम पूरा हुआ! कुल {len(clip_files)} पार्ट्स तैयार किए गए हैं।")
            
            with open(zip_filename, "rb") as f:
                st.download_button(
                    label="📦 Download All Clips (ZIP)",
                    data=f,
                    file_name="split_videos.zip",
                    mime="application/zip"
                )