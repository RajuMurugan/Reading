import streamlit as st
import random
import base64
import tempfile
from gtts import gTTS
import numpy as np
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import av
import queue
import speech_recognition as sr

# -------- Sample Sentences --------
sample_sentences = {
    "PRE-KG": ["A B C D.", "Red, blue, green.", "One, two, three, four."],
    "UKG": ["Elephant has a trunk.", "Fish swims in water.", "Goat eats grass.", "House is big."],
    "PhD": ["Computational fluid dynamics governs complex flow behavior in turbulent regimes."]
}

# -------- Generate Text --------
def generate_text(level, minutes):
    total_words = minutes * 20
    sentences = sample_sentences.get(level, [])
    paragraph = ""
    last_sentence = ""
    while len(paragraph.split()) < total_words:
        choice = random.choice(sentences)
        if choice != last_sentence:
            paragraph += " " + choice
            last_sentence = choice
    return paragraph.strip()

# -------- Text-to-Speech --------
def speak_text(text):
    tts = gTTS(text)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        tts.save(f.name)
        audio_path = f.name
    with open(audio_path, "rb") as audio_file:
        b64 = base64.b64encode(audio_file.read()).decode()
        audio_html = f"""
        <audio autoplay controls style="width: 100%;">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)

# -------- Compare Text --------
def compare_text(expected, spoken):
    expected_words = expected.strip().lower().split()
    spoken_words = spoken.strip().lower().split()
    result = []
    for i, word in enumerate(expected_words):
        if i < len(spoken_words) and word == spoken_words[i]:
            result.append(f"<span style='color:green'>{spoken_words[i]}</span>")
        elif i < len(spoken_words):
            result.append(f"<span style='color:red'>{spoken_words[i]}</span>")
        else:
            result.append(f"<span style='color:gray'>{word}</span>")
    return " ".join(result)

# -------- Audio Processor --------
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.buffer = queue.Queue()

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        pcm = frame.to_ndarray().flatten().astype(np.int16).tobytes()
        self.buffer.put(pcm)
        return frame

# -------- Streamlit UI --------
st.set_page_config(page_title="🎙️ AI Reading App", layout="centered")
st.title("🧠 AI Reading App: PRE-KG to PhD")

level = st.selectbox("📘 Choose class level:", list(sample_sentences.keys()))
minutes = st.slider("⏱️ Select reading duration (min):", 1, 5, 1)

generated_text = generate_text(level, minutes)

st.subheader("📝 Please read the following:")
st.markdown(f"""
<div style='background-color:#f0f8ff; padding:15px; border-radius:10px; font-size:18px; line-height:1.7; max-height:300px; overflow:auto;'>
{generated_text}
</div>
""", unsafe_allow_html=True)

if st.button("🔊 Listen to pronunciation"):
    speak_text(generated_text)

st.subheader("🎤 Speak Now")

ctx = webrtc_streamer(
    key="read-aloud",
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"video": False, "audio": True},
    async_processing=True,
)

if ctx.audio_receiver:
    audio_bytes = b""
    processor = ctx.audio_processor
    if processor:
        st.info("🎙️ Listening... Speak clearly.")
        if st.button("🧪 Analyze Speech"):
            with st.spinner("⏳ Processing your speech..."):
                for _ in range(50):
                    try:
                        audio_bytes += processor.buffer.get(timeout=0.2)
                    except queue.Empty:
                        break
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                    f.write(audio_bytes)
                    recognizer = sr.Recognizer()
                    with sr.AudioFile(f.name) as source:
                        audio_data = recognizer.record(source)
                        try:
                            spoken_text = recognizer.recognize_google(audio_data)
                            st.success("✅ Speech recognized successfully!")
                            st.markdown(f"**🗣️ You said:** _{spoken_text}_")
                            st.subheader("🧾 Word-by-Word Comparison:")
                            st.markdown(compare_text(generated_text, spoken_text), unsafe_allow_html=True)
                        except sr.UnknownValueError:
                            st.error("❌ Could not understand the audio.")
                        except sr.RequestError:
                            st.error("❌ Speech Recognition API Error.")

st.markdown("---")
st.caption("Built by Dr. Raju Murugan 💡 | Streamlit + WebRTC + Google Speech Recognition")
