// ========== PARAGRAPH BANK ==========
const paragraphBank = {
  Easy: [
    `The sun rises early in summer. Birds begin to sing before most people wake up. A quiet morning walk can clear the mind and set a calm tone for the day ahead.`,
    `Cooking at home saves money and improves health. Even simple meals made with fresh ingredients can taste better than fast food. The habit of cooking regularly builds confidence in the kitchen.`,
    `Libraries are peaceful places to study and read. They offer free books, internet access, and a quiet environment. Many people find it easier to focus when they are away from home distractions.`,
    `Plants need sunlight, water, and good soil to grow well. Indoor plants can improve air quality and make a room feel more alive. Taking care of plants is a relaxing and rewarding daily routine.`,
    `Regular sleep improves memory, mood, and physical health. Most adults need between seven and nine hours each night. Going to bed at the same time every day helps the body maintain a steady rhythm.`,
    `Walking is one of the easiest forms of exercise. It requires no equipment and can be done almost anywhere. Even a short walk after meals helps digestion and reduces stress levels significantly.`,
    `Music has the power to change how we feel instantly. Calm music can reduce anxiety while upbeat songs boost energy. Many people use music to help them focus while working or studying.`,
  ],
  Medium: [
    `The human brain processes roughly eleven million bits of information per second, yet conscious thought accounts for only a tiny fraction of that capacity. Most mental activity operates silently below awareness, shaping decisions, habits, and perceptions without our knowledge.`,
    `Climate change is altering weather patterns across the globe, leading to more frequent droughts, floods, and extreme temperatures. Scientists argue that immediate action to reduce carbon emissions is essential to prevent long-term damage to ecosystems and human societies.`,
    `Effective communication requires both speaking clearly and listening actively. Many conflicts arise not from disagreement but from misunderstanding. Taking time to paraphrase what another person has said before responding can dramatically improve the quality of any conversation.`,
    `The rise of remote work has changed how millions of people structure their days. Without a fixed commute or office environment, workers must create their own boundaries between professional and personal time. Self-discipline and intentional scheduling have become essential skills.`,
    `Reading fiction builds empathy by placing the reader inside the perspective of characters from different backgrounds and circumstances. Studies suggest that habitual readers of literary fiction score higher on tests measuring the ability to understand other people's emotions.`,
    `Financial literacy is rarely taught in schools yet it affects every aspect of adult life. Understanding compound interest, budgeting, and the difference between assets and liabilities gives individuals greater control over their financial future and reduces long-term stress.`,
    `Urban green spaces provide more than aesthetic value. Parks and tree-lined streets reduce air pollution, lower ambient temperatures, and provide habitat for wildlife. Research consistently shows that people who live near green space report better mental health outcomes.`,
  ],
  Hard: [
    `Cognitive load theory explains how working memory capacity directly influences learning efficiency. When individuals process complex information under strict time constraints, they must strategically allocate mental resources to prevent overload. High intrinsic complexity, combined with environmental pressure, increases the likelihood of cognitive strain. Sustained performance in such conditions requires advanced attention regulation, executive control, and adaptive problem-solving strategies.`,
    `The philosophical question of free will has occupied thinkers for centuries without resolution. Determinists argue that every decision is the inevitable result of prior causes, rendering the concept of genuine choice illusory. Compatibilists counter that freedom is not incompatible with causation, provided that actions stem from one's own desires rather than external compulsion. The debate has profound implications for moral responsibility and the foundations of legal systems.`,
    `Neuroplasticity refers to the brain capacity to reorganise its structure and function in response to learning, experience, and injury. Unlike the long-held belief that the adult brain is fixed, contemporary research reveals that synaptic connections strengthen or weaken continuously throughout life. Deliberate practice, repeated exposure, and emotionally significant experiences all contribute to lasting structural changes in neural architecture.`,
    `The global financial system is built on a complex web of interdependencies that can amplify local disruptions into widespread crises. When investors lose confidence simultaneously, liquidity evaporates, credit markets freeze, and institutions that appeared solvent can collapse within days. Regulatory frameworks attempt to build resilience into this system, but the tension between innovation, efficiency, and stability remains fundamentally unresolved.`,
    `Quantum mechanics challenges classical intuitions about the nature of reality at the subatomic level. Particles exist in superpositions of multiple states until observed, at which point the wave function collapses to a single outcome. The implications of this indeterminacy extend beyond physics into philosophy, raising questions about the relationship between measurement and existence that remain deeply contested among physicists and philosophers alike.`,
  ]
};

// ========== WPM CAPS PER DIFFICULTY (realistic max) ==========
const WPM_CAPS = { Easy: 80, Medium: 65, Hard: 50 };
const WPM_BENCH = { Easy: 40, Medium: 30, Hard: 20 };

// ========== STATE ==========
let startTime         = 0;
let lastKeyTime       = 0;
let pauses            = 0;
let errors            = 0;
let backspaces        = 0;
let timerInterval     = null;
let timeLimit         = 0;
let testStarted       = false;
let blindModeActive   = false;
let blindHideTimer    = null;
let currentDifficulty = "Easy";
let currentText       = "";

const textarea        = document.getElementById("typingArea");
const referenceTextEl = document.getElementById("referenceText");
const timerText       = document.getElementById("timerText");
const timerFill       = document.getElementById("timerFill");
const difficultyInput = document.getElementById("difficultyInput");
const blindToggle     = document.getElementById("blindToggle");
const blindBadge      = document.getElementById("blindBadge");

// ========== PARAGRAPH ==========
function getRandomParagraph(level) {
  const pool = paragraphBank[level];
  return pool[Math.floor(Math.random() * pool.length)];
}

function loadParagraph() {
  currentText = getRandomParagraph(currentDifficulty);
  referenceTextEl.innerHTML = "";
  referenceTextEl.style.filter = "";
  referenceTextEl.style.userSelect = "";
  currentText.split("").forEach((char, i) => {
    const span = document.createElement("span");
    span.innerText = char;
    span.className = i === 0 ? "cursor-char" : "pending";
    referenceTextEl.appendChild(span);
  });
  if (textarea) textarea.value = "";
  updateLiveStats();
}

// ========== DIFFICULTY ==========
function setDifficulty(level, btn) {
  currentDifficulty = level;
  if (difficultyInput) difficultyInput.value = level;
  document.querySelectorAll(".diff-tab").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  resetTest();
  loadParagraph();
}

function resetTest() {
  clearInterval(timerInterval);
  clearTimeout(blindHideTimer);
  startTime = 0; lastKeyTime = 0;
  pauses = 0; errors = 0; backspaces = 0;
  testStarted = false;
  if (timerText) timerText.textContent = "—";
  if (timerFill) { timerFill.style.width = "100%"; timerFill.classList.remove("urgent"); }
  if (textarea)  { textarea.disabled = false; }
  if (referenceTextEl) { referenceTextEl.style.filter = ""; }
  updateLiveStats();
}

// ========== BLIND MODE TOGGLE ==========
if (blindToggle) {
  blindToggle.addEventListener("change", () => {
    blindModeActive = blindToggle.checked;
    if (blindBadge) blindBadge.style.display = blindModeActive ? "inline-flex" : "none";
  });
}

// ========== TIMER ==========
const timeLimits = { Easy: 30, Medium: 60, Hard: 80 };

function startTimer() {
  timeLimit = timeLimits[currentDifficulty] || 30;
  let remaining = timeLimit;
  if (timerText) timerText.textContent = remaining + "s";

  // Blind mode: hide text after 10 seconds
  if (blindModeActive) {
    blindHideTimer = setTimeout(() => {
      if (referenceTextEl) {
        referenceTextEl.style.filter = "blur(8px)";
        referenceTextEl.style.userSelect = "none";
        referenceTextEl.style.transition = "filter 0.6s ease";
      }
    }, 10000);
  }

  timerInterval = setInterval(() => {
    remaining--;
    if (timerText) timerText.textContent = remaining + "s";
    if (timerFill) {
      timerFill.style.width = (remaining / timeLimit * 100) + "%";
      if (remaining <= 10) timerFill.classList.add("urgent");
    }
    if (remaining <= 0) {
      clearInterval(timerInterval);
      if (textarea) textarea.disabled = true;
      if (timerText) timerText.textContent = "Done";
      calculateAndSubmit();
    }
  }, 1000);
}

// ========== TYPING EVENTS ==========
if (textarea) {
  textarea.addEventListener("focus", () => {
    if (!testStarted) {
      testStarted = true;
      startTime   = Date.now();
      lastKeyTime = startTime;
      startTimer();
    }
  });

  textarea.addEventListener("keydown", (e) => {
    const now = Date.now();
    if (now - lastKeyTime > 2000 && testStarted) pauses++;
    if (e.key === "Backspace") backspaces++;
    lastKeyTime = now;
    updateLiveStats();
  });

  textarea.addEventListener("input", () => {
    const typed = textarea.value;
    const spans = referenceTextEl.querySelectorAll("span");
    errors = 0;
    spans.forEach((span, i) => {
      span.classList.remove("cursor-char");
      const ch = typed[i];
      if (ch == null) {
        span.className = i === typed.length ? "cursor-char" : "pending";
      } else if (ch === span.innerText) {
        span.className = "correct";
      } else {
        span.className = "incorrect";
        errors++;
      }
    });
    updateLiveStats();
  });
}

// ========== LIVE STATS ==========
function updateLiveStats() {
  const wpmEl   = document.getElementById("liveWpm");
  const accEl   = document.getElementById("liveAcc");
  const errEl   = document.getElementById("liveErrors");
  const pauseEl = document.getElementById("livePauses");
  if (!wpmEl) return;

  const elapsedMin = startTime ? (Date.now() - startTime) / 60000 : 0;
  const words      = textarea ? textarea.value.trim().split(/\s+/).filter(w => w.length > 0) : [];

  // Cap WPM: only compute after at least 3 seconds, cap at difficulty max
  let wpm = 0;
  if (elapsedMin > 0.05) { // at least 3 seconds
    wpm = Math.round(words.length / elapsedMin);
    wpm = Math.min(wpm, WPM_CAPS[currentDifficulty]);
  }

  const refLen = currentText.length;
  const acc    = refLen > 0 ? Math.max(0, Math.round(((refLen - errors) / refLen) * 100)) : 100;

  wpmEl.textContent   = wpm;
  accEl.textContent   = acc + "%";
  errEl.textContent   = errors;
  pauseEl.textContent = pauses;
}

// ========== SUBMIT ==========
function calculateAndSubmit() {
  const text    = textarea ? textarea.value.trim() : "";
  const elapsedMin = Math.max((Date.now() - startTime) / 60000, 0.0167); // min 1 second
  const words   = text.split(/\s+/).filter(w => w.length > 0);

  // Compute accurate WPM — use actual elapsed time, cap at realistic max
  let wpm = words.length / elapsedMin;
  wpm = Math.min(wpm, WPM_CAPS[currentDifficulty]);
  wpm = Math.max(wpm, 0);

  // Accuracy based on characters typed vs reference
  const refLen   = currentText.length;
  const typedLen = textarea ? textarea.value.length : 0;

  // Count correct characters at each position
  let correctChars = 0;
  const typedFull  = textarea ? textarea.value : "";
  for (let i = 0; i < Math.min(typedLen, refLen); i++) {
    if (typedFull[i] === currentText[i]) correctChars++;
  }

  // Accuracy = correct chars / total reference length (penalises not finishing)
  const accuracy = refLen > 0
    ? Math.max(0, Math.min((correctChars / refLen) * 100, 100))
    : 0;

  document.getElementById("wpmInput").value       = wpm.toFixed(2);
  document.getElementById("errorsInput").value    = errors;
  document.getElementById("backspaceInput").value = backspaces;
  document.getElementById("pauseInput").value     = pauses;
  document.getElementById("accuracyInput").value  = accuracy.toFixed(2);

  document.getElementById("testForm").submit();
}

// ========== INIT ==========
window.onload = loadParagraph;
