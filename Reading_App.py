import streamlit as st
import random
import base64
import tempfile
import time
from gtts import gTTS
import speech_recognition as sr
from streamlit_audiorecorder import audiorecorder
from pydub import AudioSegment

# ---------------- Sample Sentences ----------------
sample_sentences = {
    "PRE-KG": ["A B C D.", "Red, blue, green.", "One, two, three, four."],
    "UKG": ["Elephant has a trunk.", "Fish swims in water.", "Goat eats grass.", "House is big."],
    "PhD": ["Computational fluid dynamics governs complex flow behavior in turbulent regimes."]
}

# ---------------- Generate Paragraph ----------------
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

# ---------------- Text-to-Speech ----------------
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

# ---------------- Compare Pronunciation ----------------
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

# ---------------- App Layout ----------------
st.set_page_config(page_title="🗣️ AI Reading App", layout="centered")
st.title("🧠 AI Reading App: PRE-KG to PhD")

level = st.selectbox("📘 Choose your class level:", list(sample_sentences.keys()))
minutes = st.slider("⏱️ Select reading duration (in minutes):", 1, 5, 1)

generated_text = generate_text(level, minutes)

st.subheader("📝 Please read the following:")
st.markdown(f"""
<div style='background-color:#f0f8ff; padding:15px; border-radius:10px; font-size:18px; line-height:1.7; max-height:300px; overflow:auto;'>
{generated_text}
</div>
""", unsafe_allow_html=True)

if st.button("🔊 Listen to pronunciation"):
    speak_text(generated_text)

# ---------------- Record User Reading ----------------
st.subheader("🎤 Record your reading")
audio = audiorecorder("Click to record", "Recording... Click again to stop")

if audio:
    st.audio(audio, format="audio/wav")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(audio)
        audio_path = f.name

    # Convert if needed (streamlit-audiorecorder returns mp3-like format sometimes)
    sound = AudioSegment.from_file(audio_path)
    wav_path = audio_path.replace(".wav", "_converted.wav")
    sound.export(wav_path, format="wav")

    # Speech Recognition
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        st.info("🔍 Analyzing your speech...")
        audio_data = recognizer.record(source)
        start_time = time.time()
        try:
            spoken_text = recognizer.recognize_google(audio_data)
            end_time = time.time()
            st.success("✅ Speech recognized successfully!")

            # Comparison
            st.subheader("🧾 Word-by-Word Comparison:")
            st.markdown(f"<div style='font-size:18px;line-height:1.8'>{compare_text(generated_text, spoken_text)}</div>", unsafe_allow_html=True)

            # WPM Calculation
            words_spoken = len(spoken_text.split())
            duration_minutes = (end_time - start_time) / 60
            wpm = words_spoken / duration_minutes if duration_minutes > 0 else 0
            st.info(f"📈 Words per minute (WPM): **{wpm:.2f}**")

        except sr.UnknownValueError:
            st.error("❌ Could not understand the audio.")
        except sr.RequestError as e:
            st.error(f"❌ API Error: {e}")

st.markdown("---")
st.caption("Developed by Dr. Raju Murugan 💡 | Streamlit + gTTS + streamlit-audiorecorder + SpeechRecognition")
