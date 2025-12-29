const chatBody = document.getElementById("chat-body");
const textInput = document.getElementById("text-input");
const sendBtn = document.getElementById("send-btn");
const micBtn = document.getElementById("mic-btn");

/* ---------- STATE ---------- */
let phase = "intro"; // intro | tech

fetch("/chat-state")
  .then(r => r.json())
  .then(data => {
      if (!data.intro_done) {
          addBot("Tell me about yourself.");
          phase = "intro";
      } else {
          phase = "tech";
          askNextQuestion();
      }
  });


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

/* ---------- TEXT SUBMIT ---------- */
sendBtn.onclick = () => {
    const text = textInput.value.trim();
    if (!text) return;
    textInput.value = "";
    handleAnswer(text);
};

/* ---------- ANSWER ROUTER ---------- */
function handleAnswer(text) {
    addUser(text);

    if (phase === "intro") {
        submitIntro(text);
    } else {
        submitTechAnswer(text);
    }
}

/* ---------- INTRO ---------- */
async function submitIntro(text) {
    const res = await fetch("/evaluate-intro", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ intro: text })
    });

    const data = await res.json();

    if (!res.ok) {
        addBot("⚠️ " + (data.detail || data.error || "Intro failed"));
        return;
    }

    addBot("Feedback:");
    addBot(data.feedback);

    // ✅ ONLY HERE
    phase = "tech";
    askNextQuestion();
}
