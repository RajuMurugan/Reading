import streamlit as st
import random
import tempfile
import time
from gtts import gTTS
import speech_recognition as sr
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import av
import queue

# ---------------- Sample Sentences ----------------
sentences_db = {
    "PRE-KG": ["A B C D.", "Red, blue, green.", "One, two, three, four."],
    "UKG": ["Elephant has a trunk.", "Fish swims in water.", "Goat eats grass.", "House is big."],
    "PhD": ["Computational fluid dynamics governs complex flow behavior in turbulent regimes."]
}

# ---------------- Text Generation ----------------
def generate_text(level, minutes):
    total_words = minutes * 20
    sentences = sentences_db.get(level, [])
    paragraph = ""
    last = ""
    while len(paragraph.split()) < total_words:
        choice = random.choice(sentences)
        if choice != last:
            paragraph += " " + choice
            last = choice
    return paragraph.strip()

# ---------------- TTS Playback ----------------
def speak_text(text):
    tts = gTTS(text)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        tts.save(f.name)
    with open(f.name, "rb") as af:
        b64 = af.read().encode("base64").decode()
        st.markdown(f"""
        <audio autoplay controls style="width:100%;">
          <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>""", unsafe_allow_html=True)

# ---------------- Pronunciation Comparison ----------------
def compare_text(expected, spoken):
    exp = expected.lower().split()
    sp = spoken.lower().split()
    html, correct = [], 0
    for i, w in enumerate(exp):
        if i < len(sp) and sp[i] == w:
            html.append(f"<span style='color:green'>{sp[i]}</span>")
            correct += 1
        elif i < len(sp):
            html.append(f"<span style='color:red'>{sp[i]}</span>")
        else:
            html.append(f"<span style='color:gray'>{w}</span>")
    return " ".join(html), correct, len(exp)

class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.buff = queue.Queue()
    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        pcm = frame.to_ndarray().flatten().astype('int16').tobytes()
        self.buff.put(pcm)
        return frame

# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="AI Reading Live", layout="centered")
st.title("🗣️ AI Reading App — Live Mode")

level = st.selectbox("Class Level:", list(sentences_db.keys()))
minutes = st.slider("Reading Duration (min):", 1, 3, 1)
target_text = generate_text(level, minutes)
st.markdown(f"### Please read:\n> {target_text}")

if st.button("🔊 Hear Text"):
    speak_text(target_text)

st.subheader("🎤 Speak: Your Reading")

ctx = webrtc_streamer(
    key="live_audio",
    mode="SENDRECV",
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"audio": True, "video": False},
    rtc_configuration={
        "iceServers": [
            {"urls": ["stun:stun.l.google.com:19302"]},
            # Add a TURN server below if needed:
            # {"urls": ["turn:your.turn.server:3478"], "username":"<user>","credential":"<pass>"}
        ]
    },
    async_processing=True,
)

if ctx.audio_receiver and st.button("✅ Evaluate"):
    with st.spinner("Analyzing audio..."):
        raw = b""
        proc = ctx.audio_processor
        for _ in range(100):  # ~10 seconds capture
            try:
                raw += proc.buff.get(timeout=0.2)
            except queue.Empty:
                break
        if raw:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                f.write(raw)
                path = f.name
            recognizer = sr.Recognizer()
            with sr.AudioFile(path) as src:
                data = recognizer.record(src)
            try:
                start = time.time()
                spoken = recognizer.recognize_google(data)
                duration = time.time() - start
                st.success("✅ Recognized: " + spoken)
                comp_html, corr, total = compare_text(target_text, spoken)
                st.markdown("**Word-by-word comparison:**")
                st.markdown(comp_html, unsafe_allow_html=True)

                wpm = round((len(spoken.split()) / duration) * 60, 2)
                accuracy = round((corr / total) * 100, 2)
                st.info(f"WPM: **{wpm}**, Accuracy: **{accuracy}%**")
            except Exception as e:
                st.error(f"Recognition error: {e}")
        else:
            st.error("🔇 No audio captured. Try again.")

st.caption("Developed with Streamlit + WebRTC + Google Recognize")
