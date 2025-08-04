import streamlit as st
import time
import random
import base64
import numpy as np
from gtts import gTTS
import speech_recognition as sr
import tempfile

# --------------------------------------
# Sample sentences database
# --------------------------------------
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

# --------------------------------------
# Generate paragraph
# --------------------------------------
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

# --------------------------------------
# Text-to-Speech using gTTS
# --------------------------------------
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
            Your browser does not support the audio element.
        </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)

# --------------------------------------
# Compare expected vs spoken text
# --------------------------------------
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

# --------------------------------------
# Streamlit App
# --------------------------------------
st.set_page_config(page_title="🗣️ AI Reading App", layout="centered")
st.title("🧠 AI Reading App: PRE-KG to PhD")
st.markdown("📚 Select your class level and reading time. We'll generate text, let you hear it, and evaluate your pronunciation.")

level = st.selectbox("📘 Choose your class level:", list(sample_sentences.keys()))
minutes = st.slider("⏱️ Select reading duration (in minutes):", 1, 30, 2)

generated_text = generate_text(level, minutes)

st.subheader("📝 Please read the following:")
st.markdown(f"""
<div style='background-color:#f0f8ff; color:#000000; padding:15px; border-radius:10px; font-size:18px; line-height:1.7; overflow:auto; max-height:300px;'>
{generated_text}
</div>
""", unsafe_allow_html=True)

if st.button("🔊 Listen to correct pronunciation"):
    speak_text(generated_text)

# --------------------------------------
# File Upload (Recording)
# --------------------------------------
st.subheader("🎤 Upload your reading (WAV or MP3):")
uploaded_audio = st.file_uploader("Upload your recording", type=["wav", "mp3"])

if uploaded_audio is not None:
    st.audio(uploaded_audio, format='audio/wav')
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(uploaded_audio.read())
        audio_path = f.name

    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
            spoken_text = recognizer.recognize_google(audio_data)
            st.success("✅ Speech recognized successfully!")

            st.subheader("🧾 Word-by-Word Comparison:")
            st.markdown(f"<div style='font-size:18px;line-height:1.8'>{compare_text(generated_text, spoken_text)}</div>", unsafe_allow_html=True)

    except sr.UnknownValueError:
        st.error("❌ Could not understand the audio.")
    except sr.RequestError:
        st.error("❌ Speech recognition API error.")

st.markdown("---")
st.caption("Developed by Dr. Raju Murugan 💡 | Streamlit + gTTS + SpeechRecognition")
