import streamlit as st
import random
import base64
import tempfile
from gtts import gTTS

# Sample database
sample_sentences = {
    "PRE-KG": ["A B C D.", "Red, blue, green.", "One, two, three, four."],
    "UKG": ["Elephant has a trunk.", "Fish swims in water.", "Goat eats grass.", "House is big."],
    "Class 1": ["I am playing outside.", "She is reading a book.", "He is running fast.", "The sun is bright."],
    "PhD": ["Computational fluid dynamics governs complex flow behavior in turbulent regimes."]
}

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

# Streamlit UI
st.set_page_config(page_title="🗣️ AI Reading App", layout="centered")
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

st.subheader("🎤 Speak into mic and get live transcription")
st.markdown("""
<button onclick="startRecognition()">🎙️ Start Speaking</button>
<p id="output" style="font-size:18px; padding-top:10px;"></p>

<script>
function startRecognition() {
    const output = document.getElementById("output");
    window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    output.innerHTML = "🎤 Listening...";

    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        output.innerHTML = "🗣️ You said: <b>" + transcript + "</b>";
        const url = new URL(window.location);
        url.searchParams.set("spoken", transcript);
        window.location.href = url.toString();
    };

    recognition.onerror = function(event) {
        output.innerHTML = "❌ Error: " + event.error;
    };

    recognition.start();
}
</script>
""", unsafe_allow_html=True)

# ✅ New API to get spoken words from URL
spoken = st.query_params.get("spoken", None)
if spoken:
    st.subheader("🧾 Word-by-Word Comparison:")
    st.markdown(f"<div style='font-size:18px;line-height:1.8'>{compare_text(generated_text, spoken)}</div>", unsafe_allow_html=True)

st.markdown("---")
st.caption("Made by Dr. Raju Murugan 💡 | Powered by Streamlit + JavaScript Web Speech API")
