/**
 * TezMindz Modular Educational Game: Fraction Pizza
 * Class 5 | Mathematics | Chapter 3: Fractions | Topic 1: Understanding Fractions
 */

(function() {
  'use strict';

  const state = {
    currentLevelIdx: 0,
    selectedSlices: new Set(),
    challenges: [
      { level: 1, targetNum: 3, targetDen: 8, title: "Level 1: 3/8 Pizza Order", xp: 20, coins: 5 },
      { level: 2, targetNum: 5, targetDen: 8, title: "Level 2: 5/8 Pizza Order", xp: 25, coins: 8 },
      { level: 3, targetNum: 2, targetDen: 6, title: "Level 3: 2/6 Pizza Slices", xp: 30, coins: 10 },
      { level: 4, targetNum: 3, targetDen: 4, title: "Level 4: 3/4 Quarter Slices", xp: 35, coins: 12 },
    ]
  };

  function renderPizzaSlices(totalSlices) {
    const group = document.getElementById('fp-slices-group');
    if (!group) return;
    group.innerHTML = '';

    const radius = 90;
    const anglePerSlice = (2 * Math.PI) / totalSlices;

    for (let i = 0; i < totalSlices; i++) {
      const startAngle = i * anglePerSlice - Math.PI / 2;
      const endAngle = (i + 1) * anglePerSlice - Math.PI / 2;

      const x1 = radius * Math.cos(startAngle);
      const y1 = radius * Math.sin(startAngle);
      const x2 = radius * Math.cos(endAngle);
      const y2 = radius * Math.sin(endAngle);

      const largeArc = anglePerSlice > Math.PI ? 1 : 0;
      const d = `M 0 0 L ${x1} ${y1} A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2} Z`;

      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      path.setAttribute('d', d);
      path.setAttribute('class', 'fp-slice');
      path.setAttribute('data-slice-id', i);

      path.addEventListener('click', () => {
        toggleSlice(i, path);
      });

      group.appendChild(path);
    }
  }

  function toggleSlice(id, element) {
    if (state.selectedSlices.has(id)) {
      state.selectedSlices.delete(id);
      element.classList.remove('selected');
    } else {
      state.selectedSlices.add(id);
      element.classList.add('selected');
    }
    if (window.TezMindzGameBridge) window.TezMindzGameBridge.playSound('click');
    updateCounter();
  }

  function updateCounter() {
    const ch = state.challenges[state.currentLevelIdx];
    const cnt = state.selectedSlices.size;
    const countEl = document.getElementById('fp-selected-count');
    const fracEl = document.getElementById('fp-current-fraction');
    if (countEl) countEl.textContent = cnt;
    if (fracEl) fracEl.textContent = `${cnt}/${ch.targetDen}`;
  }

  function loadChallenge(idx) {
    const ch = state.challenges[idx];
    if (!ch) {
      finishGame();
      return;
    }

    state.currentLevelIdx = idx;
    state.selectedSlices.clear();

    document.getElementById('fp-mission-tag').textContent = `Level ${ch.level} of ${state.challenges.length}`;
    document.getElementById('fp-task-heading').textContent = ch.title;
    document.getElementById('fp-target-num').textContent = ch.targetNum;
    document.getElementById('fp-target-den').textContent = ch.targetDen;
    document.getElementById('fp-total-slices').textContent = ch.targetDen;
    document.getElementById('fp-target-subtext').innerHTML = `Click <strong>${ch.targetNum}</strong> out of <strong>${ch.targetDen}</strong> slices.`;

    const fb = document.getElementById('fp-feedback');
    if (fb) fb.style.display = 'none';

    renderPizzaSlices(ch.targetDen);
    updateCounter();
  }

  function showFeedback(type, title, message) {
    const fb = document.getElementById('fp-feedback');
    const fbTitle = document.getElementById('fp-fb-title');
    const fbMsg = document.getElementById('fp-fb-msg');
    if (!fb) return;

    fb.className = `fp-feedback-card ${type}`;
    if (fbTitle) fbTitle.textContent = title;
    if (fbMsg) fbMsg.textContent = message;
    fb.style.display = 'flex';
  }

  async function handleSubmit() {
    const ch = state.challenges[state.currentLevelIdx];
    const isCorrect = (state.selectedSlices.size === ch.targetNum);

    if (window.TezMindzGameBridge) {
      window.TezMindzGameBridge.submitAnswer({
        level: ch.level,
        answer: { selected: state.selectedSlices.size, total: ch.targetDen },
        scoreDelta: isCorrect ? 100 : 0,
      });
    }

    if (isCorrect) {
      showFeedback('correct', 'Delicious!', `You correctly served ${ch.targetNum}/${ch.targetDen} of the pizza! (+${ch.xp} XP)`);
      setTimeout(() => {
        if (state.currentLevelIdx + 1 < state.challenges.length) {
          loadChallenge(state.currentLevelIdx + 1);
        } else {
          finishGame();
        }
      }, 1400);
    } else {
      showFeedback('wrong', 'Incorrect Portion', `You selected ${state.selectedSlices.size}/${ch.targetDen} slices. Try selecting exactly ${ch.targetNum}!`);
    }
  }

  async function finishGame() {
    showFeedback('correct', '🍕 Master Pizza Chef!', 'You mastered all fraction orders!');
    if (window.TezMindzGameBridge) {
      await window.TezMindzGameBridge.completeGame({ score: 400, totalLevels: 4 });
      setTimeout(() => {
        window.TezMindzGameBridge.finishAndRedirect();
      }, 1500);
    }
  }

  function init() {
    document.getElementById('fp-submit-btn').addEventListener('click', handleSubmit);
    document.getElementById('fp-reset-btn').addEventListener('click', () => {
      state.selectedSlices.clear();
      document.querySelectorAll('.fp-slice').forEach(s => s.classList.remove('selected'));
      updateCounter();
    });
    document.getElementById('fp-hint-btn').addEventListener('click', () => {
      const ch = state.challenges[state.currentLevelIdx];
      showFeedback('hint', 'Chef Hint', `The numerator is ${ch.targetNum}, so pick ${ch.targetNum} slices!`);
    });

    loadChallenge(0);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
