const chatBody = document.getElementById("chat-body");
const textInput = document.getElementById("text-input");
const sendBtn = document.getElementById("send-btn");
const micBtn = document.getElementById("mic-btn");
window.onload = () => {
  fetch("/reset-session", { credentials: "include" });
};


/* =====================
   STATE
===================== */
let phase = null;              // "intro" | "tech"
let questionLoading = false;
let awaitingAnswer = false;
let answerLocked = false;

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
   INITIAL SYNC (CRITICAL)
===================== */
fetch("/chat-state", { credentials: "include" })
    .then(res => res.json())
    .then(state => {
        if (!state.resume_uploaded) {
            addBot("⚠️ Please upload your resume first.");
            return;
        }

        if (!state.intro_done) {
            phase = "intro";
            addBot("Tell me about yourself.");
            return;
        }

        if (state.tech_done) {
            addBot("✅ Interview already completed.");
            return;
        }

        // intro done, tech ongoing
        phase = "tech";
        addBot("Resume received. Continuing interview.");
        askNextQuestion();
    })
    .catch(() => {
        addBot("⚠️ Failed to sync interview state.");
    });

/* =====================
   TEXT SUBMIT
===================== */
sendBtn.onclick = () => {
    const text = textInput.value.trim();
    if (!text || answerLocked) return;
    textInput.value = "";
    handleAnswer(text);
};

/* =====================
   ANSWER ROUTER
===================== */
function handleAnswer(text) {
    if (answerLocked) return;
    answerLocked = true;

    addUser(text);

    if (phase === "intro") {
        submitIntro(text);
    } else if (phase === "tech") {
        submitTechAnswer(text);
    }
}

/* =====================
   INTRO
===================== */
async function submitIntro(text) {
    try {
        const res = await fetch("/evaluate-intro", {
            method: "POST",
            credentials: "include",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ intro: text })
        });

        const data = await res.json();

        if (!res.ok) {
            addBot("⚠️ " + (data.detail || "Intro failed"));
            answerLocked = false;
            return;
        }

        addBot("📝 Intro Feedback:");
        addBot(data.feedback);

        phase = "tech";
        answerLocked = false;
        askNextQuestion();

    } catch {
        addBot("⚠️ Server error during intro.");
        answerLocked = false;
    }
}

/* =====================
   QUESTIONS
===================== */
async function askNextQuestion() {
    if (questionLoading || awaitingAnswer) return;

    questionLoading = true;
    awaitingAnswer = true;

    try {
        const res = await fetch("/generate-question", {
            method: "GET",
            credentials: "include"
        });

        const data = await res.json();

        if (!res.ok) {
            addBot("⚠️ Failed to load question.");
            awaitingAnswer = false;
            return;
        }

        if (data.done) {
            addBot("✅ Interview completed.");
            awaitingAnswer = false;
            return;
        }

        addBot(`Question ${data.question_no}:`);
        addBot(data.question);

    } catch {
        addBot("⚠️ Server error while fetching question.");
        awaitingAnswer = false;
    } finally {
        questionLoading = false;
    }
}

/* =====================
   TECH ANSWER
===================== */
async function submitTechAnswer(text) {
    if (!awaitingAnswer) {
        answerLocked = false;
        return;
    }

    awaitingAnswer = false;

    try {
        const res = await fetch("/submit-answer", {
            method: "POST",
            credentials: "include",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ answer: text })
        });

        const data = await res.json();

        if (!res.ok) {
            addBot("⚠️ " + (data.detail || "Evaluation failed"));
            awaitingAnswer = true;
            answerLocked = false;
            return;
        }

        addBot("📊 Feedback:");
        addBot(data.feedback);

        answerLocked = false;
        askNextQuestion();

    } catch {
        addBot("⚠️ Server error during evaluation.");
        awaitingAnswer = true;
        answerLocked = false;
    }
}

/* =====================
   MIC (SAFE)
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

    recognition.onresult = (e) => {
        let text = "";
        for (let i = 0; i < e.results.length; i++) {
            text += e.results[i][0].transcript + " ";
        }
        recognition.finalTranscript = text.trim();
    };

    recognition.onend = () => {
        if (recognition.finalTranscript && !answerLocked) {
            handleAnswer(recognition.finalTranscript);
        }
        recognition.finalTranscript = "";
        cleanupMic();
    };

    recognition.onerror = () => cleanupMic();
} else {
    micBtn.disabled = true;
}

micBtn.onclick = () => {
    if (!recognition || isRecording) {
        recognition?.stop();
        return;
    }

    recognition.finalTranscript = "";
    recognition.start();
    isRecording = true;
    micBtn.innerText = "⏹";

    stopTimer = setTimeout(() => recognition.stop(), 60000);
};

function cleanupMic() {
    isRecording = false;
    micBtn.innerText = "🎤";
    if (stopTimer) clearTimeout(stopTimer);
    stopTimer = null;
}
