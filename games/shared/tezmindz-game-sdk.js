/**
 * TezMindz Educational Game SDK (Bridge)
 * Provides isolated educational games with standardized communication to Django backend:
 * - Session tracking & state management
 * - Level progress, scores, attempts & validation
 * - Dynamic sound synthesis & audio FX (zero external asset dependencies)
 * - XP, Coins, and Streak synchronization
 * - Result celebrations and seamless redirection
 */

(function(window) {
  'use strict';

  // ── CSRF HELPER ────────────────────────────────────────────────────────────
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  // ── SYNTHESIZED WEB AUDIO ENGINE ──────────────────────────────────────────
  class TezMindzAudio {
    constructor() {
      this.ctx = null;
      this.isMuted = false;
      this.initAudioContext();
    }

    initAudioContext() {
      if (!this.ctx && (window.AudioContext || window.webkitAudioContext)) {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        this.ctx = new AudioCtx();
      }
    }

    resume() {
      if (this.ctx && this.ctx.state === 'suspended') {
        this.ctx.resume();
      }
    }

    play(type) {
      if (this.isMuted) return;
      this.initAudioContext();
      this.resume();
      if (!this.ctx) return;

      const now = this.ctx.currentTime;

      if (type === 'click') {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(400, now);
        osc.frequency.exponentialRampToValueAtTime(600, now + 0.05);
        gain.gain.setValueAtTime(0.15, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.05);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(now);
        osc.stop(now + 0.05);
      } else if (type === 'correct') {
        const notes = [523.25, 659.25, 783.99, 1046.50]; // C5, E5, G5, C6
        notes.forEach((freq, idx) => {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'triangle';
          osc.frequency.setValueAtTime(freq, now + idx * 0.08);
          gain.gain.setValueAtTime(0.2, now + idx * 0.08);
          gain.gain.exponentialRampToValueAtTime(0.01, now + idx * 0.08 + 0.16);
          osc.connect(gain);
          gain.connect(this.ctx.destination);
          osc.start(now + idx * 0.08);
          osc.stop(now + idx * 0.08 + 0.18);
        });
      } else if (type === 'wrong') {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(220, now);
        osc.frequency.linearRampToValueAtTime(140, now + 0.22);
        gain.gain.setValueAtTime(0.2, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.22);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(now);
        osc.stop(now + 0.23);
      } else if (type === 'coin') {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(987.77, now); // B5
        osc.frequency.setValueAtTime(1318.51, now + 0.08); // E6
        gain.gain.setValueAtTime(0.25, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.3);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(now);
        osc.stop(now + 0.32);
      } else if (type === 'fanfare') {
        const fanfareNotes = [440, 554.37, 659.25, 880]; // A4, C#5, E5, A5
        fanfareNotes.forEach((freq, idx) => {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'triangle';
          osc.frequency.setValueAtTime(freq, now + idx * 0.12);
          gain.gain.setValueAtTime(0.25, now + idx * 0.12);
          gain.gain.exponentialRampToValueAtTime(0.01, now + idx * 0.12 + 0.35);
          osc.connect(gain);
          gain.connect(this.ctx.destination);
          osc.start(now + idx * 0.12);
          osc.stop(now + idx * 0.12 + 0.38);
        });
      }
    }
  }

  // ── CORE GAME BRIDGE ───────────────────────────────────────────────────────
  const TezMindzGameBridge = {
    audio: new TezMindzAudio(),
    session: null,
    game: null,
    student: null,
    score: 0,
    currentLevel: 1,
    csrfToken: null,

    /**
     * Initialize SDK with environment configuration
     */
    init: function(config = {}) {
      this.csrfToken = config.csrfToken || getCookie('csrftoken') || '';
      this.session = config.session || (window.GAME_CONTEXT && window.GAME_CONTEXT.session) || null;
      this.game = config.game || (window.GAME_CONTEXT && window.GAME_CONTEXT.game) || {};
      this.student = config.student || (window.GAME_CONTEXT && window.GAME_CONTEXT.student) || {};
      this.score = this.session ? (this.session.score || 0) : 0;
      this.currentLevel = this.session ? (this.session.current_level || 1) : 1;

      console.log(`[TezMindz Game SDK] Initialized for game: "${this.game.title || 'Educational Game'}"`);

      // Dispatch event to inform game scripts that SDK is ready
      const readyEvent = new CustomEvent('tezmindz:ready', {
        detail: {
          bridge: this,
          game: this.game,
          session: this.session,
          student: this.student
        }
      });
      window.dispatchEvent(readyEvent);
      return this;
    },

    /**
     * Submit an answer or level completion attempt
     */
    submitAnswer: async function(payload = {}) {
      this.audio.resume();
      const sessionId = this.session ? this.session.id : (payload.sessionId || (window.GAME_CONTEXT && window.GAME_CONTEXT.sessionId));
      
      const requestData = {
        level_number: payload.level || this.currentLevel,
        content_id: payload.contentId || payload.questionId,
        answer: payload.answer,
        time_taken: payload.timeTaken || 0,
        score_delta: payload.scoreDelta || 0,
      };

      try {
        let endpoint = `/api/game-sessions/${sessionId}/submit/`;
        if (!sessionId) {
          endpoint = `/api/game/submit/`;
          requestData.game_id = this.game.id;
          requestData.difficulty = this.game.difficulty || 'easy';
        }

        const response = await fetch(endpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.csrfToken,
          },
          body: JSON.stringify(requestData),
        });

        const data = await response.json();

        if (data.is_correct || data.success) {
          this.audio.play('correct');
          if (data.coins_earned || data.xp_earned) {
            setTimeout(() => this.audio.play('coin'), 180);
          }
        } else {
          this.audio.play('wrong');
        }

        if (data.new_score !== undefined) {
          this.score = data.new_score;
          this.updateHUDScore(this.score);
        }

        return data;
      } catch (err) {
        console.error('[TezMindz Game SDK] Submit failed:', err);
        return { success: false, error: err.message };
      }
    },

    /**
     * Request tiered hint
     */
    getHint: async function(payload = {}) {
      const sessionId = this.session ? this.session.id : payload.sessionId;
      if (!sessionId) return { success: false, message: "No active session." };

      try {
        const res = await fetch(`/api/game-sessions/${sessionId}/hint/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.csrfToken,
          },
          body: JSON.stringify(payload),
        });
        return await res.json();
      } catch (err) {
        return { success: false, error: err.message };
      }
    },

    /**
     * Complete entire game session
     */
    completeGame: async function(finalStats = {}) {
      this.audio.play('fanfare');
      const sessionId = this.session ? this.session.id : finalStats.sessionId;
      const finalScore = finalStats.score !== undefined ? finalStats.score : this.score;

      try {
        let endpoint = `/api/game-sessions/${sessionId}/complete/`;
        if (!sessionId) {
          endpoint = `/api/game/submit/`;
        }

        const response = await fetch(endpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.csrfToken,
          },
          body: JSON.stringify({
            final_score: finalScore,
            total_levels_completed: finalStats.totalLevels || this.currentLevel,
            game_id: this.game.id,
            difficulty: this.game.difficulty || 'easy',
            is_completed: true,
          }),
        });

        const data = await response.json();
        return data;
      } catch (err) {
        console.error('[TezMindz Game SDK] Complete game failed:', err);
        return { success: false, error: err.message };
      }
    },

    /**
     * Update HUD score element if present
     */
    updateHUDScore: function(newScore) {
      const el = document.getElementById('tmz-hud-score') || document.querySelector('.player-score-value');
      if (el) {
        el.textContent = newScore;
      }
    },

    /**
     * Redirect to celebratory result page
     */
    finishAndRedirect: function(customUrl) {
      const target = customUrl || (this.session ? `/games/dream-house-builder/result/${this.session.id}/` : '/result/');
      window.location.href = target;
    },

    /**
     * Play sound effect
     */
    playSound: function(type) {
      this.audio.play(type);
    }
  };

  // Expose globally
  window.TezMindzGameBridge = TezMindzGameBridge;

  // Auto initialize when DOM is loaded if context is available
  document.addEventListener('DOMContentLoaded', () => {
    if (window.GAME_CONTEXT) {
      TezMindzGameBridge.init(window.GAME_CONTEXT);
    }
  });

})(window);
