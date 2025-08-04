import streamlit as st
import time
import sounddevice as sd
from scipy.io.wavfile import write
import speech_recognition as sr
import tempfile
import numpy as np
import random
import base64
import pyttsx3

# -----------------------------
# Extended sentence database
# -----------------------------
sample_sentences = {
    "PRE-KG": ["A B C D.", "Red, blue, green.", "One, two, three, four."],
    "LKG": ["Apple is red.", "Ball is round.", "Cat is cute.", "Dog barks loudly."],
    "UKG": ["Elephant has a trunk.", "Fish swims in water.", "Goat eats grass.", "House is big."],
    "Class 1": ["I am playing outside.", "She is reading a book.", "He is running fast.", "The sun is bright."],
    "Class 2": ["The sun rises in the east.", "My father goes to work.", "The teacher is kind.", "I like my school."],
    "Class 3": ["Birds fly in the sky.", "The dog chased the cat.", "We should help each other.", "I play football daily."],
    "Class 4": ["Trees give us oxygen.", "Water is essential for life.", "My school has a big library.", "Reading books improves knowledge."],
    "Class 5": ["India is a diverse country.", "Cleanliness is next to godliness.", "The Earth revolves around the Sun.", "Mathematics improves logic."],
    "Class 6": ["The human body has 206 bones.", "Plants prepare food by photosynthesis.", "A sentence expresses a complete thought.", "We must save water."],
    "Class 7": ["Gravity keeps us on the ground.", "A good citizen obeys the law.", "Air has weight and occupies space.", "History teaches us past events."],
    "Class 8": ["Sound travels in waves.", "Democracy is the best form of government.", "The periodic table has 118 elements.", "Adjectives describe nouns."],
    "Class 9": ["Photosynthesis requires sunlight.", "Newton's laws explain motion.", "Atoms are the building blocks of matter.", "Poetry conveys deep emotions."],
    "Class 10": ["Climate change is a global issue.", "The Constitution of India came into effect in 1950.", "Electricity flows through conductors.", "Trigonometry deals with triangles."],
    "Class 11": ["Cell is the basic unit of life.", "Vectors have both magnitude and direction.", "Kinetic energy is energy of motion.", "Economic growth leads to development."],
    "Class 12": ["Integration is the reverse process of differentiation.", "Genetics is the study of heredity.", "Indian economy is agriculture based.", "Optics deals with the behavior of light."],
    "UG": ["Machine learning models improve with data.", "Engineering design involves analysis and creativity.",
           "Cultural studies help us understand societies.", "Thermodynamics governs energy interactions."],
    "PG": ["Advanced algorithms solve complex problems efficiently.", "Neural networks mimic brain function for pattern recognition.",
           "Finite element analysis is used in structural simulations.", "Research methodology is key to academic inquiry."],
    "PhD": ["Computational fluid dynamics governs complex flow behavior in turbulent regimes.",
            "Turbulent combustion involves intricate coupling of chemistry and fluid flow.",
            "Multiphase reacting flows are often simulated using large eddy simulation models."]
}

# -----------------------------
# Generate formatted paragraph
# -----------------------------
def generate_text(level, minutes):
    total_words = minutes * 20
    sentences = sample_sentences.get(level, [])
    used = set()
    paragraph = ""
    last_sentence = ""
    while len(paragraph.split()) < total_words:
        choice = random.choice(sentences)
        if choice != last_sentence:
            paragraph += " " + choice
            last_sentence = choice
            used.add(choice)
    return paragraph.strip()

# -----------------------------
# Record user's speech
# -----------------------------
def recognize_speech(duration):
    fs = 44100
    st.info(f"🎙️ Recording for {duration} seconds. Please start speaking.")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        write(f.name, fs, recording)
        wav_path = f.name

    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio = recognizer.record(source)

    try:
        spoken_text = recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        spoken_text = ""
    except sr.RequestError:
        spoken_text = "API unavailable"

    return spoken_text, wav_path

# -----------------------------
# Word-by-word comparison
# -----------------------------
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

# -----------------------------
# Calculate WPM
# -----------------------------
def calculate_wpm(spoken_text, start, end):
    num_words = len(spoken_text.strip().split())
    time_taken = (end - start) / 60
    return round(num_words / time_taken, 2) if time_taken else 0

# -----------------------------
# Audio HTML for playback
# -----------------------------
def get_audio_html(wav_path):
    with open(wav_path, "rb") as f:
        audio_bytes = f.read()
        b64 = base64.b64encode(audio_bytes).decode()
        return f"""
        <audio controls style="width:100%;">
            <source src="data:audio/wav;base64,{b64}" type="audio/wav">
            Your browser does not support audio playback.
        </audio>
        """

# -----------------------------
# Text-to-Speech Playback
# -----------------------------
def speak_text(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.say(text)
    engine.runAndWait()

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="🗣️ AI Reading App", layout="centered")
st.title("🧠 AI Reading App: PRE-KG to PhD")
st.markdown("📚 Select your class level and reading time. We'll generate text, let you hear it, and evaluate your pronunciation.")

# Inputs
level = st.selectbox("📘 Choose your class level:", list(sample_sentences.keys()))
minutes = st.slider("⏱️ Select reading duration (in minutes):", 1, 30, 2)

# Generate paragraph
generated_text = generate_text(level, minutes)

# Show paragraph
st.subheader("📝 Please read the following:")
st.markdown(f"""
<div style='background-color:#f0f8ff; color:#000000; padding:15px; border-radius:10px; font-size:18px; line-height:1.7; overflow:auto; max-height:300px;'>
{generated_text}
</div>
""", unsafe_allow_html=True)

# TTS playback
if st.button("🔊 Listen to correct pronunciation"):
    speak_text(generated_text)

# Record & evaluate
if st.button("🎤 Start Reading"):
    duration_seconds = min(20 + minutes * 2, 120)
    start_time = time.time()
    spoken_text, audio_path = recognize_speech(duration_seconds)
    end_time = time.time()

    if spoken_text.strip():
        st.subheader("🧾 Word-by-Word Comparison:")
        st.markdown(f"<div style='font-size:18px;line-height:1.8'>{compare_text(generated_text, spoken_text)}</div>", unsafe_allow_html=True)

        wpm = calculate_wpm(spoken_text, start_time, end_time)
        st.success(f"🕒 Reading Speed: **{wpm} WPM**")

        st.subheader("🔁 Playback your recording:")
        st.markdown(get_audio_html(audio_path), unsafe_allow_html=True)
    else:
        st.error("❌ Could not recognize your speech. Please try again.")

st.markdown("---")
st.caption("Developed by Dr. Raju Murugan 💡 | Streamlit + SoundDevice + Google SpeechRecognition + pyttsx3")
