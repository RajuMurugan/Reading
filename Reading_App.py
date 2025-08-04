import streamlit as st
import random
import tempfile
import base64
import time
from gtts import gTTS
import speech_recognition as sr
from pydub import AudioSegment

# Sample sentences
sample_sentences = {
    "PRE-KG": ["A B C D.", "Red, blue, green.", "One, two, three, four."],
    "UKG": ["Elephant has a trunk.", "Fish swims in water.", "Goat eats grass.", "House is big."],
    "PhD": ["Computational fluid dynamics governs complex flow behavior in turbulent regimes."]
}

# Generate text
def generate_text(level, minutes):
    total_words = minutes * 20
    sentences = sample_sentences.get(level, [])
    paragraph = ""
    last = ""
    while len(paragraph.split()) < total_words:
        choice = random.choice(sentences)
        if choice != last:
            paragraph += " " + choice
            last = choice
    return paragraph.strip()

# Speak text
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

# Compare words
def compare_text(expected, spoken):
    expected_words = expected.lower().split()
    spoken_words = spoken.lower().split()
    result = []
    correct = 0
    for i, word in enumerate(expected_words):
        if i < len(spoken_words) and spoken_words[i] == word:
            result.append(f"<span style='color:green'>{word}</span>")
            correct += 1
        elif i < len(spoken_words):
            result.append(f"<span style='color:red'>{spoken_words[i]}</span>")
        else:
            result.append(f"<span style='color:gray'>{word}</span>")
    return " ".join(result), correct, len(spoken_words)

# UI
st.set_page_config(page_title="🗣️ AI Reading App", layout="centered")
st.title("🧠 AI Reading App: PRE-KG to PhD")

level = st.selectbox("Select your level:", list(sample_sentences.keys()))
minutes = st.slider("Reading time (minutes):", 1, 5, 1)

target_text = generate_text(level, minutes)

st.subheader("Read the following:")
st.markdown(f"<div style='background:#f0f8ff;padding:15px'>{target_text}</div>", unsafe_allow_html=True)

if st.button("🔊 Listen"):
    speak_text(target_text)

st.subheader("🎤 Upload your recording")
uploaded_audio = st.file_uploader("Upload WAV/MP3 audio", type=["wav", "mp3"])

if uploaded_audio:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        f.write(uploaded_audio.read())
        temp_path = f.name

    audio = AudioSegment.from_file(temp_path)
    wav_path = temp_path.replace(".mp3", ".wav")
    audio.export(wav_path, format="wav")

    st.audio(wav_path, format="audio/wav")

    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)
        start = time.time()
        try:
            spoken = recognizer.recognize_google(audio_data)
            end = time.time()
            st.success(f"Recognized Speech: {spoken}")
            diff_html, correct, total = compare_text(target_text, spoken)
            st.markdown("### 🧾 Word Comparison:")
            st.markdown(diff_html, unsafe_allow_html=True)
            wpm = (len(spoken.split()) / (end - start)) * 60
            st.info(f"📈 Words Per Minute: **{wpm:.2f}**")
            accuracy = (correct / total) * 100 if total else 0
            st.info(f"✅ Accuracy: **{accuracy:.2f}%**")
        except sr.UnknownValueError:
            st.error("Could not understand the audio.")
        except sr.RequestError as e:
            st.error(f"API error: {e}")

st.markdown("---")
st.caption("Developed by Dr. Raju Murugan 💡 | Streamlit + gTTS + SpeechRecognition")
