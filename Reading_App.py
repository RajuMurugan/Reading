import streamlit as st
import random
import base64
import tempfile
import time
from gtts import gTTS
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import av
import queue
import speech_recognition as sr
import numpy as np

# Sample Text Database
sample_sentences = {
    "PRE-KG": ["A B C D.", "Red, blue, green.", "One, two, three, four."],
    "UKG": ["Elephant has a trunk.", "Fish swims in water.", "Goat eats grass.", "House is big."],
    "PhD": ["Computational fluid dynamics governs complex flow behavior in turbulent regimes."]
}

def generate_text(level, minutes):
    target = minutes * 20
    sentences = sample_sentences.get(level, [])
    paragraph, last = "", ""
    while len(paragraph.split()) < target:
        choice = random.choice(sentences)
        if choice != last:
            paragraph += (" " + choice)
            last = choice
    return paragraph.strip()

def speak_text(text):
    tts = gTTS(text)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        tts.save(f.name)
        path = f.name
    with open(path, "rb") as af:
        b64 = base64.b64encode(af.read()).decode()
        st.markdown(f"""
            <audio autoplay controls style="width:100%;">
              <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
        """, unsafe_allow_html=True)

def compare_text(expected, spoken):
    exp = expected.strip().lower().split()
    sp = spoken.strip().lower().split()
    result, correct = [], 0
    for i, w in enumerate(exp):
        if i < len(sp) and sp[i] == w:
            result.append(f"<span style='color:green'>{sp[i]}</span>")
            correct += 1
        elif i < len(sp):
            result.append(f"<span style='color:red'>{sp[i]}</span>")
        else:
            result.append(f"<span style='color:gray'>{w}</span>")
    return " ".join(result), correct, len(sp)

class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.buffer = queue.Queue()

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        pcm = frame.to_ndarray().flatten().astype(np.int16).tobytes()
        self.buffer.put(pcm)
        return frame

st.set_page_config("AI Reading App", layout="centered")
st.title("🧠 AI Reading App: Pronunciation + WPM")

level = st.selectbox("Choose level:", list(sample_sentences.keys()))
minutes = st.slider("Reading duration (minutes):", 1, 5, 1)
generated = generate_text(level, minutes)
st.subheader("Please read the following:")
st.markdown(f"<div style='background:#f0f8ff;padding:15px; border-radius:10px;'>{generated}</div>", unsafe_allow_html=True)

if st.button("🔊 Listen"):
    speak_text(generated)

st.subheader("🎤 Speak Now (Live mic):")
ctx = webrtc_streamer(
    key="mic",
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"video": False, "audio": True},
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    async_processing=True,
)

if ctx.audio_receiver:
    if st.button("🧪 Process Speech"):
        audio_bytes = b""
        proc = ctx.audio_processor
        with st.spinner("Processing speech..."):
            for _ in range(50):
                try:
                    audio_bytes += proc.buffer.get(timeout=0.2)
                except queue.Empty:
                    break

        if audio_bytes:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                f.write(audio_bytes)
                recognizer = sr.Recognizer()
                with sr.AudioFile(f.name) as src:
                    data = recognizer.record(src)
                try:
                    spoken = recognizer.recognize_google(data)
                    st.success("✅ Recognized: " + spoken)
                    comp_html, corr, total = compare_text(generated, spoken)
                    st.subheader("Word-by-Word Comparison:")
                    st.markdown(comp_html, unsafe_allow_html=True)

                    wpm = round((total / (minutes * 60)) * 60, 2)  # since audio length ~ minutes
                    accuracy = round((corr / len(generated.split())) * 100, 2)
                    st.info(f"WPM: **{wpm}**, Accuracy: **{accuracy}%**")
                except sr.RequestError:
                    st.error("Speech recognition failed.")
                except sr.UnknownValueError:
                    st.error("Couldn't understand audio.")
        else:
            st.error("No audio captured.")
                    
st.markdown("---")
st.caption("Built by Dr. Raju Murugan | Uses Streamlit‑WebRTC + Google SpeechRecognition")
