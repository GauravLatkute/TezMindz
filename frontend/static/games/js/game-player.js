/**
 * GamePlayer — Unified game orchestrator for Tezz-Mindz Game Engine.
 * Accurately tracks session levels, submits answers with specific level/content IDs, and updates 3D world state.
 */
class GamePlayer {
  constructor(config = {}) {
    this.gameSlug = config.gameSlug || 'dream-house-builder';
    this.gameType = config.gameType || 'house_builder';
    this.sessionId = config.sessionId || null;
    this.levels = [];
    this.currentLevelIndex = 0;
    this.score = 0;
    this.timeSpentInLevel = 0;
    this.timerInterval = null;

    // Components
    this.api = window.GameAPI;
    this.audio = window.GameAudio;
    this.world3D = null;
    this.dialogue = null;
  }

  async init() {
    this.initAudio();
    await this.loadGameLevels();
    this.init3DWorld();
    this.initDialogue();
    await this.startOrResumeSession();
  }

  initAudio() {
    if (this.audio) {
      document.addEventListener('click', () => this.audio.init(), { once: true });
      document.addEventListener('keydown', () => this.audio.init(), { once: true });
    }
  }

  init3DWorld() {
    if (window.House3DWorld) {
      this.world3D = new House3DWorld('house-3d-fullscreen-viewport', this);
    }
  }

  initDialogue() {
    if (window.InWorldDialogue) {
      this.dialogue = new InWorldDialogue(this);
      window.dialogue = this.dialogue;
    }
  }

  async loadGameLevels() {
    try {
      const res = await this.api.getGameLevels(this.gameSlug);
      if (res.success && res.data) {
        this.levels = res.data;
      }
    } catch (err) {
      console.error("Failed to load levels:", err);
    }
  }

  async startOrResumeSession() {
    try {
      const res = await this.api.startGame(this.gameSlug);
      if (res.success && res.data) {
        this.sessionId = res.data.session_id;
        this.score = res.data.score || 0;
        const targetLevel = (res.data.current_level || 1) - 1;
        this.currentLevelIndex = Math.max(0, Math.min(targetLevel, this.levels.length - 1));

        // Sync 3D World Stage
        if (this.world3D) {
          this.world3D.setStage(this.currentLevelIndex, false);
        }

        this.updateHUD();
        this.startTimer();
      }
    } catch (err) {
      console.error("Failed to start session:", err);
    }
  }

  updateHUD() {
    const scoreEl = document.getElementById('hud-score');
    if (scoreEl) scoreEl.textContent = this.score;

    const level = this.levels[this.currentLevelIndex] || { level_number: this.currentLevelIndex + 1, title: 'Buy the Land' };
    const levelPill = document.getElementById('hud-level-pill');
    if (levelPill) levelPill.textContent = `Level ${level.level_number} of 5`;

    const missionEl = document.getElementById('hud-objective-text');
    if (missionEl) {
      missionEl.innerHTML = this.getObjectiveText(level.level_number);
    }
  }

  getObjectiveText(levelNum) {
    switch (levelNum) {
      case 1: return "Walk to Land Broker Mr. Sharma &amp; Buy Plot [E]";
      case 2: return "Walk to Concrete Mixer Depot &amp; Pour Foundation [E]";
      case 3: return "Walk to Crane Console &amp; Build Brick Walls [E]";
      case 4: return "Walk to Marketplace Scale &amp; Order Roof [E]";
      case 5: return "Walk to Chief Architect &amp; Sign-Off Villa Royale [E]";
      default: return "Explore the 3D Construction Site";
    }
  }

  startTimer() {
    clearInterval(this.timerInterval);
    this.timeSpentInLevel = 0;
    const timerEl = document.getElementById('hud-timer');

    this.timerInterval = setInterval(() => {
      this.timeSpentInLevel++;
      if (timerEl) {
        timerEl.textContent = `${this.timeSpentInLevel}s`;
      }
    }, 1000);
  }

  async submitSpecificAnswer(level, content, answer, callback) {
    if (!level || !content) {
      level = this.levels[this.currentLevelIndex] || this.levels[0];
      content = (level.contents || [])[0] || {};
    }

    try {
      const res = await this.api.submitAnswer(this.sessionId, {
        level_id: level.id,
        content_id: content.id,
        answer: answer,
        time_taken: this.timeSpentInLevel,
        hints_used: 0
      });

      if (res.success && res.is_correct) {
        this.score = res.current_score;
        this.timeSpentInLevel = 0;

        if (this.audio) this.audio.playSuccess();
        this.showInWorldBanner(`🎉 LEVEL ${level.level_number} COMPLETE! +${res.points_earned} PTS`, 'success');

        // Advance level index
        const nextLevelNum = res.current_level || (level.level_number + 1);
        this.currentLevelIndex = Math.min(nextLevelNum - 1, this.levels.length - 1);
        this.updateHUD();

        if (callback) callback(true, res);

        // If completed all 5 levels, redirect to result screen
        if (level.level_number >= 5) {
          setTimeout(async () => {
            await this.api.completeGame(this.sessionId);
            window.location.href = `/games/dream-house-builder/result/${this.sessionId}/`;
          }, 2500);
        }
      } else {
        if (this.audio) this.audio.playError();
        this.showInWorldBanner(res.explanation || "💪 Not quite! Review the numbers and try again.", 'warning');
        if (callback) callback(false, res);
      }
    } catch (err) {
      console.error("Submission error:", err);
      if (callback) callback(false, { error: err.message });
    }
  }

  showInWorldBanner(msg, type = 'success') {
    const b = document.getElementById('in-world-toast');
    if (!b) return;
    b.className = `in-world-toast-banner ${type}`;
    b.innerHTML = msg;
    b.style.display = 'block';
    setTimeout(() => { b.style.display = 'none'; }, 4500);
  }
}

window.GamePlayer = GamePlayer;
