/**
 * TezMindz Modular Educational Game: Number Builder
 * Class 5 | Mathematics | Chapter 1 | Topic 1
 * Uses TezMindzGameBridge SDK for session submission, hints, and score synchronization.
 */

(function() {
  'use strict';

  // ── GAME STATE ──
  const state = {
    currentLevelIdx: 0,
    activeSlot: 'o',
    digits: {
      tl: 0, // Ten Lakhs
      l: 0,  // Lakhs
      tth: 0,// Ten Thousands
      th: 0, // Thousands
      h: 0,  // Hundreds
      t: 0,  // Tens
      o: 0,  // Ones
    },
    challenges: [
      {
        level: 1,
        title: "Level 1: 6-Digit Builder",
        instruction: "Build the number corresponding to the words below:",
        words: "Two Lakh Fifty Thousand",
        targetNumber: 250000,
        hint: "Two Lakh = 2 in Lakhs place, Fifty Thousand = 5 in Ten Thousands place.",
        xp: 20,
        coins: 5,
      },
      {
        level: 2,
        title: "Level 2: Place Value Master",
        instruction: "Build the 6-digit number:",
        words: "Three Lakh Twenty-Five Thousand Four Hundred Ten",
        targetNumber: 325410,
        hint: "3 in Lakhs, 2 in Ten-Thousands, 5 in Thousands, 4 in Hundreds, 1 in Tens, 0 in Ones.",
        xp: 25,
        coins: 8,
      },
      {
        level: 3,
        title: "Level 3: Zero Placeholders",
        instruction: "Carefully place zeros in empty periods:",
        words: "Five Lakh Eight Thousand Two Hundred",
        targetNumber: 508200,
        hint: "Notice Ten-Thousands has 0, and Ones has 0: 5,08,200.",
        xp: 30,
        coins: 10,
      },
      {
        level: 4,
        title: "Level 4: 7-Digit Challenge",
        instruction: "Step up to Ten Lakhs (7 digits):",
        words: "Twelve Lakh Thirty-Four Thousand Five Hundred Sixty",
        targetNumber: 1234560,
        hint: "1 in Ten Lakhs, 2 in Lakhs -> 12 Lakhs.",
        xp: 35,
        coins: 12,
      },
      {
        level: 5,
        title: "Level 5: Grand Olympiad Finale",
        instruction: "Construct the maximum 7-digit value:",
        words: "Forty-Five Lakh Six Thousand Seven Hundred Eighty-Nine",
        targetNumber: 4506789,
        hint: "45 in Lakhs period, 06 in Thousands period, 789 in Units period.",
        xp: 50,
        coins: 15,
      }
    ]
  };

  // ── INDIAN NUMBER FORMATTING ──
  function formatIndianNumber(num) {
    if (num === 0) return "0";
    let s = num.toString();
    if (s.length <= 3) return s;
    let last3 = s.substring(s.length - 3);
    let rest = s.substring(0, s.length - 3);
    let formatted = "";
    while (rest.length > 2) {
      formatted = "," + rest.substring(rest.length - 2) + formatted;
      rest = rest.substring(0, rest.length - 2);
    }
    return rest + formatted + "," + last3;
  }

  function calculateCurrentNumber() {
    return (
      state.digits.tl * 1000000 +
      state.digits.l * 100000 +
      state.digits.tth * 10000 +
      state.digits.th * 1000 +
      state.digits.h * 100 +
      state.digits.t * 10 +
      state.digits.o
    );
  }

  // ── UI REFRESH ──
  function updateUI() {
    // Update individual digit slots
    for (const [slot, val] of Object.entries(state.digits)) {
      const el = document.getElementById(`digit-${slot}`);
      if (el) el.textContent = val;
    }

    // Update live formatted reading
    const currentVal = calculateCurrentNumber();
    const readingEl = document.getElementById('nb-current-val');
    if (readingEl) {
      readingEl.textContent = formatIndianNumber(currentVal);
    }

    // Active slot styling
    document.querySelectorAll('.nb-slot-box').forEach(box => {
      box.classList.remove('active-slot');
    });
    const activeBox = document.getElementById(`slot-${state.activeSlot}`);
    if (activeBox) activeBox.classList.add('active-slot');
  }

  function loadChallenge(idx) {
    const ch = state.challenges[idx];
    if (!ch) {
      // Completed all levels!
      finishGame();
      return;
    }

    state.currentLevelIdx = idx;
    // Reset digits
    Object.keys(state.digits).forEach(k => state.digits[k] = 0);
    state.activeSlot = 'l';

    // Hide Ten Lakhs slot for 6-digit challenges if not needed
    const tlSlot = document.getElementById('slot-tl');
    if (tlSlot) {
      tlSlot.style.display = ch.targetNumber >= 1000000 ? 'flex' : (ch.level >= 4 ? 'flex' : 'none');
    }

    // Update headers
    const tag = document.getElementById('nb-mission-tag');
    if (tag) tag.textContent = `Level ${ch.level} of ${state.challenges.length}`;

    const title = document.getElementById('nb-task-heading');
    if (title) title.textContent = ch.title;

    const desc = document.getElementById('nb-task-instruction');
    if (desc) desc.textContent = ch.instruction;

    const words = document.getElementById('nb-target-text');
    if (words) words.textContent = ch.words;

    // Hide feedback
    const fb = document.getElementById('nb-feedback');
    if (fb) fb.style.display = 'none';

    // Update level step badges in HUD
    document.querySelectorAll('.level-step-badge').forEach((badge, i) => {
      badge.classList.remove('active');
      if (i === idx) badge.classList.add('active');
      if (i < idx) badge.classList.add('completed');
    });

    updateUI();
  }

  function showFeedback(type, title, message) {
    const fb = document.getElementById('nb-feedback');
    const fbIcon = document.getElementById('nb-fb-icon');
    const fbTitle = document.getElementById('nb-fb-title');
    const fbMsg = document.getElementById('nb-fb-msg');

    if (!fb) return;

    fb.className = `nb-feedback-card ${type}`;
    if (fbIcon) fbIcon.textContent = type === 'correct' ? '🎉' : (type === 'hint' ? '💡' : '❌');
    if (fbTitle) fbTitle.textContent = title;
    if (fbMsg) fbMsg.textContent = message;

    fb.style.display = 'flex';
  }

  // ── SUBMISSION LOGIC ──
  async function handleSubmit() {
    const ch = state.challenges[state.currentLevelIdx];
    const currentVal = calculateCurrentNumber();

    const isCorrect = (currentVal === ch.targetNumber);

    if (window.TezMindzGameBridge) {
      window.TezMindzGameBridge.submitAnswer({
        level: ch.level,
        answer: { value: currentVal, formatted: formatIndianNumber(currentVal) },
        scoreDelta: isCorrect ? 100 : 0,
      });
    }

    if (isCorrect) {
      showFeedback('correct', 'Brilliant!', `You accurately built ₹${formatIndianNumber(currentVal)}! (+${ch.xp} XP, +${ch.coins} Coins)`);
      
      setTimeout(() => {
        if (state.currentLevelIdx + 1 < state.challenges.length) {
          loadChallenge(state.currentLevelIdx + 1);
        } else {
          finishGame();
        }
      }, 1400);
    } else {
      showFeedback('wrong', 'Not Quite', `You built ${formatIndianNumber(currentVal)}. Check the place values and try again!`);
    }
  }

  function handleHint() {
    const ch = state.challenges[state.currentLevelIdx];
    if (window.TezMindzGameBridge) {
      window.TezMindzGameBridge.playSound('click');
    }
    showFeedback('hint', 'Helpful Hint', ch.hint);
  }

  async function finishGame() {
    showFeedback('correct', '🏆 Champion!', 'You conquered all 5 levels of Number Builder!');
    if (window.TezMindzGameBridge) {
      await window.TezMindzGameBridge.completeGame({
        score: 500,
        totalLevels: 5,
      });
      setTimeout(() => {
        window.TezMindzGameBridge.finishAndRedirect();
      }, 1500);
    }
  }

  // ── EVENT LISTENERS ──
  function setupEvents() {
    // Slot selection
    document.querySelectorAll('.nb-slot-box').forEach(box => {
      box.addEventListener('click', (e) => {
        if (e.target.classList.contains('nb-step-btn')) return;
        const placeId = box.id.replace('slot-', '');
        state.activeSlot = placeId;
        if (window.TezMindzGameBridge) window.TezMindzGameBridge.playSound('click');
        updateUI();
      });
    });

    // Stepper buttons (up / down)
    document.querySelectorAll('.nb-step-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const slot = btn.getAttribute('data-slot');
        const dir = parseInt(btn.getAttribute('data-dir'), 10);
        let cur = state.digits[slot] || 0;
        cur = (cur + dir + 10) % 10;
        state.digits[slot] = cur;
        state.activeSlot = slot;
        if (window.TezMindzGameBridge) window.TezMindzGameBridge.playSound('click');
        updateUI();
      });
    });

    // Digit stamp buttons (0-9)
    document.querySelectorAll('.nb-stamp-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        if (btn.id === 'nb-clear-btn') {
          Object.keys(state.digits).forEach(k => state.digits[k] = 0);
          if (window.TezMindzGameBridge) window.TezMindzGameBridge.playSound('click');
          updateUI();
          return;
        }
        const num = parseInt(btn.getAttribute('data-num'), 10);
        if (state.activeSlot && !isNaN(num)) {
          state.digits[state.activeSlot] = num;
          if (window.TezMindzGameBridge) window.TezMindzGameBridge.playSound('click');
          
          // Auto advance to next place value slot to the right
          const slotOrder = ['tl', 'l', 'tth', 'th', 'h', 't', 'o'];
          const curIdx = slotOrder.indexOf(state.activeSlot);
          if (curIdx !== -1 && curIdx < slotOrder.length - 1) {
            state.activeSlot = slotOrder[curIdx + 1];
          }
          updateUI();
        }
      });
    });

    // Submit & Hint
    const submitBtn = document.getElementById('nb-submit-btn');
    if (submitBtn) submitBtn.addEventListener('click', handleSubmit);

    const hintBtn = document.getElementById('nb-hint-btn');
    if (hintBtn) hintBtn.addEventListener('click', handleHint);
  }

  // ── INITIALIZATION ──
  function initGame() {
    setupEvents();
    loadChallenge(0);
    console.log("[Number Builder] Initialized successfully.");
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initGame);
  } else {
    initGame();
  }

})();
