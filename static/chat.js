const chatBody = document.getElementById("chat-body");
const textInput = document.getElementById("text-input");
const sendBtn = document.getElementById("send-btn");
const micBtn = document.getElementById("mic-btn");

/* =====================
   STATE
===================== */
let phase = "intro"; // intro | tech

/* =====================
   UI HELPERS
===================== */
function addBot(text) {
    const d = document.createElement("div");
    d.className = "bot-msg";
    d.innerText = text;
    chatBody.appendChild(d);
    chatBody.scrollTop = chatBody.scrollHeight;
}

function addUser(text) {
    const d = document.createElement("div");
    d.className = "user-msg";
    d.innerText = text;
    chatBody.appendChild(d);
    chatBody.scrollTop = chatBody.scrollHeight;
}

/* =====================
   INITIAL MESSAGE
   (NO /chat-state — backend doesn't have it)
===================== */
addBot("Tell me about yourself.");

/* =====================
   TEXT SUBMIT
===================== */
sendBtn.onclick = () => {
    const text = textInput.value.trim();
    if (!text) return;
    textInput.value = "";
    handleAnswer(text);
};

/* =====================
   ANSWER ROUTER
===================== */
function handleAnswer(text) {
    addUser(text);

    if (phase === "intro") {
        submitIntro(text);
    } else {
        submitTechAnswer(text);
    }
}

/* =====================
   INTRO SUBMISSION
===================== */
async function submitIntro(text) {
    try {
        const res = await fetch("/evaluate-intro", {
            method: "POST",
            credentials: "include", // 🔥 REQUIRED
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ intro: text })
        });

        const data = await res.json();

        if (!res.ok) {
            addBot("⚠️ " + (data.detail || data.error || "Intro failed"));
            return;
        }

        addBot("📝 Intro Feedback:");
        addBot(data.feedback);

        phase = "tech";
        askNextQuestion();

    } catch (err) {
        addBot("⚠️ Server error during intro.");
    }
}

/* =====================
   TECH QUESTIONS
===================== */
async function askNextQuestion() {
    try {
        const res = await fetch("/generate-question", {
            method: "GET",
            credentials: "include" // 🔥 REQUIRED
        });

        const data = await res.json();

        if (!res.ok) {
            addBot("⚠️ Failed to load question.");
            return;
        }

        if (data.done) {
            addBot("✅ Interview completed.");
            return;
        }

        addBot(`Question ${data.question_no}:`);
        addBot(data.question);

    } catch (err) {
        addBot("⚠️ Server error while fetching question.");
    }
}

async function submitTechAnswer(text) {
    try {
        const res = await fetch("/submit-answer", {
            method: "POST",
            credentials: "include", // 🔥 REQUIRED
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ answer: text })
        });

        const data = await res.json();

        if (!res.ok) {
            addBot("⚠️ " + (data.detail || data.error || "Evaluation failed"));
            return;
        }

        addBot("📊 Feedback:");
        addBot(data.feedback);

        askNextQuestion();

    } catch (err) {
        addBot("⚠️ Server error during answer evaluation.");
    }
}

/* =====================
   MIC SETUP
   - Max 60s
   - User can stop early
===================== */
let recognition;
let isRecording = false;
let stopTimer = null;

if ("SpeechRecognition" in window || "webkitSpeechRecognition" in window) {
    const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;

    recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.continuous = true;

    recognition.onresult = (event) => {
        let transcript = "";
        for (let i = 0; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript + " ";
        }
        recognition.finalTranscript = transcript.trim();
    };

    recognition.onerror = (e) => {
        addBot("🎤 Mic error: " + e.error);
        cleanupMic();
    };

    recognition.onend = () => {
        if (recognition.finalTranscript) {
            handleAnswer(recognition.finalTranscript);
            recognition.finalTranscript = "";
        }
        cleanupMic();
    };
} else {
    micBtn.disabled = true;
    micBtn.innerText = "❌";
}

/* =====================
   MIC BUTTON
===================== */
micBtn.onclick = () => {
    if (!recognition) return;

    if (!isRecording) {
        recognition.finalTranscript = "";
        recognition.start();
        isRecording = true;
        micBtn.innerText = "⏹";

        // ⏱️ MAX 60 seconds (not compulsory)
        stopTimer = setTimeout(() => {
            recognition.stop();
        }, 60000);

    } else {
        recognition.stop();
    }
};

function cleanupMic() {
    isRecording = false;
    micBtn.innerText = "🎤";
    if (stopTimer) {
        clearTimeout(stopTimer);
        stopTimer = null;
    }
}
