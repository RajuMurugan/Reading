import streamlit as st
import random
import tempfile
import time
from gtts import gTTS
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import av
import queue
import speech_recognition as sr

# Sample sentences
SENTENCES = {
    "PRE-KG": ["A B C D.", "Red, blue, green.", "One, two, three, four."],
    "UKG": ["Elephant has a trunk.", "Fish swims in water.", "Goat eats grass.", "House is big."],
    "PhD": ["Computational fluid dynamics governs complex flow behavior in turbulent regimes."]
}

def generate_text(level, minutes):
    total_words = minutes * 20
    sentences = SENTENCES.get(level, [])
    paragraph = ""
    last = ""
    while len(paragraph.split()) < total_words:
        choice = random.choice(sentences)
        if choice != last:
            paragraph += " " + choice
            last = choice
    return paragraph.strip()

def speak_text(text):
    tts = gTTS(text)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        tts.save(f.name)
    with open(f.name, "rb") as af:
        b64 = base64.b64encode(af.read()).decode()
    st.markdown(f"""
        <audio autoplay controls style="width:100%;">
          <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
    """, unsafe_allow_html=True)

def compare_text(expected, spoken):
    exp = expected.lower().split()
    sp = spoken.lower().split()
    correct = 0
    html = []
    for i, w in enumerate(exp):
        if i < len(sp) and sp[i] == w:
            html.append(f"<span style='color:green'>{sp[i]}</span>")
            correct += 1
        elif i < len(sp):
            html.append(f"<span style='color:red'>{sp[i]}</span>")
        else:
            html.append(f"<span style='color:gray'>{w}</span>")
    return " ".join(html), correct, len(sp)

class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.buffer = queue.Queue()
    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        pcm = frame.to_ndarray().flatten().astype('int16').tobytes()
        self.buffer.put(pcm)
        return frame

st.set_page_config("Live Reading Evaluation", layout="centered")
st.title("🗣️ AI Reading App — Live Pronunciation & WPM")

level = st.selectbox("Choose your level:", list(SENTENCES.keys()))
minutes = st.slider("Reading duration (minutes):", 1, 3, 1)
expected_text = generate_text(level, minutes)
st.subheader("Read This Paragraph:")
st.markdown(f"<div style='background:#f0f8ff; padding:15px'>{expected_text}</div>", unsafe_allow_html=True)

if st.button("🔊 Play Pronunciation"):
    speak_text(expected_text)

ctx = webrtc_streamer(
    key="live_stt",
    mode="SENDRECV",
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"audio": True, "video": False},
    rtc_configuration={"iceServers":[{"urls":["stun:stun.l.google.com:19302"]}]},
    async_processing=True,
)

if ctx.audio_receiver and st.button("✅ Evaluate Reading"):
    audio_data = b""
    for _ in range(60):
        try:
            audio_data += ctx.audio_processor.buffer.get(timeout=0.2)
        except queue.Empty:
            break
    if not audio_data:
        st.error("No audio captured. Try again.")
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            f.write(audio_data)
            path = f.name
        recognizer = sr.Recognizer()
        with sr.AudioFile(path) as source:
            audio = recognizer.record(source)
        start = time.time()
        try:
            spoken = recognizer.recognize_google(audio)
            duration = time.time() - start
            st.success(f"✅ Recognized speech: {spoken}")
            comp_html, corr, total = compare_text(expected_text, spoken)
            st.markdown("**Word-by-word comparison:**")
            st.markdown(comp_html, unsafe_allow_html=True)
            wpm = round((len(spoken.split()) / duration) * 60, 2)
            accuracy = round((corr / total) * 100, 2) if total else 0
            st.info(f"WPM: **{wpm}**, Accuracy: **{accuracy}%**")
        except Exception as e:
            st.error(f"Speech recognition failed: {e}")

st.caption("Built with Streamlit + streamlit-webrtc + Google Speech Recognition")
