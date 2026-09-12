/**
 * Place Value Blitz - Interactive Game Engine
 * Developed for TezMindz Educational Platform
 */

// Sound Synthesizer via Web Audio API
class SoundFX {
  constructor() {
    this.ctx = null;
    this.init();
  }

  init() {
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) {
        this.ctx = new AudioCtx();
      }
    } catch (e) {
      console.warn("AudioContext not supported", e);
    }
  }

  playBeep(freq, type, duration) {
    if (!this.ctx) return;
    if (this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
    gain.gain.setValueAtTime(0.2, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + duration);
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start();
    osc.stop(this.ctx.currentTime + duration);
  }

  correct() {
    this.playBeep(587.33, 'sine', 0.1);
    setTimeout(() => this.playBeep(880.0, 'triangle', 0.25), 100);
  }

  wrong() {
    this.playBeep(220.0, 'sawtooth', 0.25);
  }

  win() {
    const notes = [523.25, 659.25, 783.99, 1046.50];
    notes.forEach((freq, idx) => {
      setTimeout(() => this.playBeep(freq, 'sine', 0.3), idx * 120);
    });
  }
}

const sounds = new SoundFX();

// Game State
const PLACE_NAMES = [
  { name: "Ones (O)", multiplier: 1, tag: "O" },
  { name: "Tens (T)", multiplier: 10, tag: "T" },
  { name: "Hundreds (H)", multiplier: 100, tag: "H" },
  { name: "Thousands (Th)", multiplier: 1000, tag: "Th" },
  { name: "Ten Thousands (TTh)", multiplier: 10000, tag: "TTh" },
  { name: "Lakhs (L)", multiplier: 100000, tag: "L" },
  { name: "Ten Lakhs (TL)", multiplier: 1000000, tag: "TL" },
];

let state = {
  score: 0,
  streak: 0,
  level: 1,
  totalQuestions: 8,
  currentQuestionIdx: 0,
  correctCount: 0,
  timeLeft: 60,
  timerInterval: null,
  currentProblem: null,
  isInputLocked: false,
};

function formatIndianNumber(num) {
  const s = num.toString();
  if (s.length <= 3) return s;
  let lastThree = s.substring(s.length - 3);
  let otherNumbers = s.substring(0, s.length - 3);
  if (otherNumbers !== '') {
    lastThree = ',' + lastThree;
  }
  return otherNumbers.replace(/\B(?=(\d{2})+(?!\d))/g, ",") + lastThree;
}

function generateProblem(level) {
  // Determine number length based on level:
  // Level 1: 3-4 digits (Hundreds / Thousands)
  // Level 2: 5 digits (Ten Thousands)
  // Level 3: 6-7 digits (Lakhs / Ten Lakhs)
  let numDigits = 3;
  if (level === 1) numDigits = Math.floor(Math.random() * 2) + 3; // 3 or 4
  else if (level === 2) numDigits = Math.floor(Math.random() * 2) + 4; // 4 or 5
  else numDigits = Math.floor(Math.random() * 2) + 6; // 6 or 7

  // Generate digits (first digit not 0)
  const digits = [];
  digits.push(Math.floor(Math.random() * 9) + 1);
  for (let i = 1; i < numDigits; i++) {
    digits.push(Math.floor(Math.random() * 10));
  }

  // Pick target digit index (from right)
  const targetIndexFromLeft = Math.floor(Math.random() * numDigits);
  const targetDigit = digits[targetIndexFromLeft];
  const placePower = numDigits - 1 - targetIndexFromLeft;
  const placeMultiplier = Math.pow(10, placePower);
  const placeInfo = PLACE_NAMES[placePower] || { name: `${placeMultiplier}`, tag: "" };

  const correctValue = targetDigit * placeMultiplier;

  // Generate 3 plausible distractors
  const options = new Set();
  options.add(correctValue);

  // Distractor 1: Face value
  options.add(targetDigit);

  // Distractor 2: One place off higher
  options.add(targetDigit * (placeMultiplier * 10));

  // Distractor 3: One place off lower
  if (placeMultiplier >= 10) {
    options.add(targetDigit * (placeMultiplier / 10));
  } else {
    options.add(targetDigit * 100);
  }

  // Fill up if needed
  while (options.size < 4) {
    const fakeMult = Math.pow(10, Math.floor(Math.random() * numDigits));
    options.add(targetDigit * fakeMult);
  }

  // Shuffle options
  const shuffledOptions = Array.from(options).sort(() => Math.random() - 0.5);

  return {
    digits,
    targetIndexFromLeft,
    targetDigit,
    placeInfo,
    correctValue,
    options: shuffledOptions,
  };
}

function renderProblem() {
  state.isInputLocked = false;
  const problem = generateProblem(state.level);
  state.currentProblem = problem;

  // Update HUD
  document.getElementById('level-display').innerText = state.level;
  document.getElementById('score-display').innerText = state.score;
  document.getElementById('streak-display').innerText = `🔥 ${state.streak}`;

  // Render digits
  const numContainer = document.getElementById('number-container');
  numContainer.innerHTML = '';

  problem.digits.forEach((d, idx) => {
    const box = document.createElement('div');
    const isTarget = idx === problem.targetIndexFromLeft;
    box.className = `digit-box ${isTarget ? 'target' : ''}`;

    const placeIndex = problem.digits.length - 1 - idx;
    const tag = PLACE_NAMES[placeIndex] ? PLACE_NAMES[placeIndex].tag : '';

    box.innerHTML = `<span>${d}</span><span class="place-tag">${tag}</span>`;
    numContainer.appendChild(box);
  });

  // Highlight pill
  document.getElementById('highlighted-digit').innerText = problem.targetDigit;
  document.getElementById('digit-info').innerHTML = 
    `What is the exact value of <strong style="color:#FACC15; font-size:1.2rem;">${problem.targetDigit}</strong> in this number?`;

  // Render Options
  const optContainer = document.getElementById('options-container');
  optContainer.innerHTML = '';

  problem.options.forEach((val) => {
    const btn = document.createElement('button');
    btn.className = 'btn-option';
    btn.innerText = formatIndianNumber(val);
    btn.onclick = () => checkAnswer(btn, val);
    optContainer.appendChild(btn);
  });

  document.getElementById('feedback-banner').innerText = '';
}

function checkAnswer(btnElement, selectedValue) {
  if (state.isInputLocked) return;
  state.isInputLocked = true;

  const problem = state.currentProblem;
  const isCorrect = selectedValue === problem.correctValue;

  const feedback = document.getElementById('feedback-banner');

  if (isCorrect) {
    sounds.correct();
    btnElement.classList.add('correct');
    state.score += 20 + state.streak * 5;
    state.streak += 1;
    state.correctCount += 1;
    feedback.style.color = '#34D399';
    feedback.innerText = `✨ Correct! ${problem.targetDigit} is in the ${problem.placeInfo.name} place = ${formatIndianNumber(problem.correctValue)}!`;
  } else {
    sounds.wrong();
    btnElement.classList.add('wrong');
    state.streak = 0;
    feedback.style.color = '#F87171';
    feedback.innerText = `💡 Not quite! The value is ${formatIndianNumber(problem.correctValue)} (${problem.placeInfo.name}).`;

    // Highlight correct button
    const allBtns = document.querySelectorAll('.btn-option');
    allBtns.forEach((b) => {
      if (b.innerText === formatIndianNumber(problem.correctValue)) {
        b.classList.add('correct');
      }
    });
  }

  state.currentQuestionIdx += 1;

  // Level up conditions
  if (state.currentQuestionIdx === 3) state.level = 2;
  if (state.currentQuestionIdx === 6) state.level = 3;

  setTimeout(() => {
    if (state.currentQuestionIdx >= state.totalQuestions || state.timeLeft <= 0) {
      endGame();
    } else {
      renderProblem();
    }
  }, 1200);
}

function startTimer() {
  clearInterval(state.timerInterval);
  state.timeLeft = 60;
  const timerElem = document.getElementById('timer-display');

  state.timerInterval = setInterval(() => {
    state.timeLeft -= 1;
    if (state.timeLeft >= 0) {
      timerElem.innerText = `${state.timeLeft}s`;
    }
    if (state.timeLeft <= 10) {
      timerElem.style.color = '#EF4444';
    }
    if (state.timeLeft <= 0) {
      clearInterval(state.timerInterval);
      endGame();
    }
  }, 1000);
}

function endGame() {
  clearInterval(state.timerInterval);
  sounds.win();

  document.getElementById('results-modal').style.display = 'flex';
  document.getElementById('final-score').innerText = state.score;
  document.getElementById('correct-answers').innerText = `${state.correctCount}/${state.currentQuestionIdx}`;

  // SDK Complete hook
  if (window.parent && window.parent.TezMindzGameBridge) {
    window.parent.TezMindzGameBridge.completeGame({
      score: state.score,
      correct: state.correctCount,
      total: state.currentQuestionIdx,
    });
  }
}

function restartGame() {
  state.score = 0;
  state.streak = 0;
  state.level = 1;
  state.currentQuestionIdx = 0;
  state.correctCount = 0;
  document.getElementById('results-modal').style.display = 'none';
  document.getElementById('timer-display').style.color = '#38BDF8';
  startTimer();
  renderProblem();
}

// Bootstrap on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  startTimer();
  renderProblem();
});
