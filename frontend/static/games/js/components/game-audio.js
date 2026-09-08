/**
 * GameAudio — Procedural Web Audio synthesizer for Tezz-Mindz Game Engine.
 * Generates 100% pure synthesized arcade sounds with zero external MP3 dependencies.
 */
class GameAudio {
  constructor() {
    this.ctx = null;
    this.enabled = true;
  }

  init() {
    if (!this.ctx) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (AudioContext) {
        this.ctx = new AudioContext();
      }
    }
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  toggleSound() {
    this.enabled = !this.enabled;
    return this.enabled;
  }

  playTone(freq, type = 'sine', duration = 0.15, gain = 0.2) {
    if (!this.enabled) return;
    this.init();
    if (!this.ctx) return;

    try {
      const osc = this.ctx.createOscillator();
      const g = this.ctx.createGain();

      osc.type = type;
      osc.frequency.setValueAtTime(freq, this.ctx.currentTime);

      g.gain.setValueAtTime(gain, this.ctx.currentTime);
      g.gain.exponentialRampToValueAtTime(0.0001, this.ctx.currentTime + duration);

      osc.connect(g);
      g.connect(this.ctx.destination);

      osc.start();
      osc.stop(this.ctx.currentTime + duration);
    } catch (e) {}
  }

  playClick() {
    this.playTone(600, 'sine', 0.06, 0.15);
  }

  playDrop() {
    this.playTone(350, 'triangle', 0.12, 0.2);
  }

  playConstruct() {
    if (!this.enabled) return;
    this.init();
    if (!this.ctx) return;

    // Fast ascending sweep
    try {
      const now = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const g = this.ctx.createGain();

      osc.type = 'triangle';
      osc.frequency.setValueAtTime(220, now);
      osc.frequency.exponentialRampToValueAtTime(880, now + 0.25);

      g.gain.setValueAtTime(0.3, now);
      g.gain.exponentialRampToValueAtTime(0.0001, now + 0.3);

      osc.connect(g);
      g.connect(this.ctx.destination);

      osc.start(now);
      osc.stop(now + 0.3);
    } catch (e) {}
  }

  playSuccess() {
    if (!this.enabled) return;
    this.init();
    // Happy 3-tone arpeggio (C5 - E5 - G5 - C6)
    [523.25, 659.25, 783.99, 1046.50].forEach((freq, idx) => {
      setTimeout(() => {
        this.playTone(freq, 'sine', 0.2, 0.25);
      }, idx * 80);
    });
  }

  playError() {
    if (!this.enabled) return;
    this.init();
    // Low double buzz
    this.playTone(220, 'sawtooth', 0.15, 0.2);
    setTimeout(() => this.playTone(180, 'sawtooth', 0.2, 0.2), 120);
  }

  playFanfare() {
    if (!this.enabled) return;
    this.init();
    const chords = [523.25, 659.25, 783.99, 1046.50, 1318.51];
    chords.forEach((f, i) => {
      setTimeout(() => this.playTone(f, 'triangle', 0.4, 0.3), i * 110);
    });
  }
}

window.GameAudio = new GameAudio();
