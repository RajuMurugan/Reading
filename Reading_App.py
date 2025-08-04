import streamlit as st
import time
import speech_recognition as sr

# -----------------------------
# Text bank for different levels
# -----------------------------
text_database = {
    "PRE-KG": ["A", "B", "C", "D"],
    "LKG": ["Apple", "Ball", "Cat", "Dog"],
    "UKG": ["Elephant", "Fish", "Goat", "House"],
    "Class 1": ["I am playing", "She is reading", "He is running"],
    "Class 2": ["The sun rises in the east", "My father goes to work"],
    "PhD": ["Computational fluid dynamics governs complex flow behavior in turbulent regimes"]
}

# -----------------------------
# Recognize speech using microphone
# -----------------------------
def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Speak now")
        audio = r.listen(source, phrase_time_limit=5)
    try:
        return r.recognize_google(audio)
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        return "API unavailable"

# -----------------------------
# Calculate Words Per Minute
# -----------------------------
def calculate_wpm(sentence, start_time, end_time):
    words = sentence.split()
    num_words = len(words)
    time_taken = (end_time - start_time) / 60  # in minutes
    if time_taken == 0:
        return 0
    return round(num_words / time_taken, 2)

# -----------------------------
# Main Streamlit App
# -----------------------------
st.set_page_config(page_title="🗣️ Reading Trainer", layout="centered")

st.title("🧠 AI Reading App: PREKG to PhD")
st.markdown("Read the sentence below and we'll check your pronunciation and reading speed!")

# -----------------------------
# Level Selection
# -----------------------------
level = st.selectbox("Choose your class level:", list(text_database.keys()))
text_choices = text_database[level]

selected_text = st.selectbox("Select sentence/word to read:", text_choices)

if st.button("🎤 Start Reading"):
    start = time.time()
    spoken_text = recognize_speech()
    end = time.time()

    st.subheader("📝 Expected Text:")
    st.markdown(f"<span style='color:blue; font-size:20px'>{selected_text}</span>", unsafe_allow_html=True)

    st.subheader("🎧 You Said:")
    if spoken_text:
        correct = spoken_text.strip().lower() == selected_text.strip().lower()
        color = "green" if correct else "red"
        st.markdown(f"<span style='color:{color}; font-size:20px'>{spoken_text}</span>", unsafe_allow_html=True)

        wpm = calculate_wpm(spoken_text, start, end)
        st.success(f"🕒 Reading Speed: **{wpm} WPM**")
    else:
        st.error("❌ Could not recognize your speech. Please try again.")

st.markdown("---")
st.caption("Developed by Dr. Raju Murugan 💡 | Powered by Streamlit & SpeechRecognition")
