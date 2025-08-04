import streamlit as st
import random
import base64
import tempfile
from gtts import gTTS

# ------------------- Sample Text -------------------
sample_sentences = {
    "PRE-KG": ["A B C D.", "Red, blue, green.", "One, two, three, four."],
    "UKG": ["Elephant has a trunk.", "Fish swims in water.", "Goat eats grass.", "House is big."],
    "PhD": ["Computational fluid dynamics governs complex flow behavior in turbulent regimes."]
}

# ------------------- Generate Text -------------------
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

# ------------------- Text-to-Speech -------------------
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

# ------------------- Compare -------------------
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

# ------------------- Streamlit UI -------------------
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

# ------------------- Live Speaking (JavaScript only) -------------------
st.subheader("🎤 Speak now (no upload needed)")

spoken_text = st.text_input("🗣️ Transcript will appear here:", key="spoken")

st.markdown("""
<button onclick="startRecognition()" style="font-size:18px; padding:10px 20px; background-color:#4CAF50; color:white; border:none; border-radius:8px;">
🎙️ Start Speaking
</button>
<p id="transcript" style="font-size:18px; color:blue; margin-top:15px;"></p>

<script>
    function startRecognition() {
        const transcriptEl = document.getElementById("transcript");
        window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!window.SpeechRecognition) {
            transcriptEl.innerHTML = "<span style='color:red'>❌ Speech Recognition not supported in this browser.</span>";
            return;
        }

        const recognition = new SpeechRecognition();
        recognition.lang = 'en-US';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        transcriptEl.innerHTML = "🎧 Listening... Please speak";

        recognition.start();

        recognition.onresult = function(event) {
            const spoken = event.results[0][0].transcript;
            transcriptEl.innerHTML = "✅ You said: <b>" + spoken + "</b>";
            const py_input = document.querySelector("input[data-baseweb='input']");
            if(py_input) {
                py_input.value = spoken;
                py_input.dispatchEvent(new Event("input", { bubbles: true }));
            }
        };

        recognition.onerror = function(event) {
            transcriptEl.innerHTML = "<span style='color:red'>❌ Error: " + event.error + "</span>";
        };
    }
</script>
""", unsafe_allow_html=True)

# ------------------- Comparison -------------------
if spoken_text:
    st.subheader("🧾 Word-by-Word Comparison:")
    st.markdown(f"<div style='font-size:18px;line-height:1.8'>{compare_text(generated_text, spoken_text)}</div>", unsafe_allow_html=True)

st.markdown("---")
st.caption("Developed by Dr. Raju Murugan 💡 | Streamlit + gTTS + JavaScript Speech Recognition")
