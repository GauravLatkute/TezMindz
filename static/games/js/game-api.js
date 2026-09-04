/**
 * GameAPI — Client-side REST API wrapper for Tezz-Mindz Game Engine.
 */
class GameAPI {
  constructor(baseUrl = '') {
    this.baseUrl = baseUrl;
  }

  getCsrfToken() {
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    if (match) return match[1];
    const input = document.querySelector('[name=csrfmiddlewaretoken]');
    return input ? input.value : '';
  }

  async request(endpoint, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      'X-CSRFToken': this.getCsrfToken(),
      ...(options.headers || {})
    };

    const res = await fetch(this.baseUrl + endpoint, {
      ...options,
      headers
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ message: 'Server error' }));
      throw new Error(err.message || `Request failed with status ${res.status}`);
    }

    return await res.json();
  }

  async getGameDetails(slug) {
    return await this.request(`/api/games/${slug}/`);
  }

  async getGameLevels(slug) {
    return await this.request(`/api/games/${slug}/levels/`);
  }

  async startGame(slug) {
    return await this.request(`/api/games/${slug}/start/`, {
      method: 'POST',
      body: JSON.stringify({})
    });
  }

  async submitAnswer(sessionId, payload) {
    return await this.request(`/api/game-sessions/${sessionId}/submit/`, {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  async getHint(sessionId, payload) {
    return await this.request(`/api/game-sessions/${sessionId}/hint/`, {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  async completeGame(sessionId) {
    return await this.request(`/api/game-sessions/${sessionId}/complete/`, {
      method: 'POST',
      body: JSON.stringify({})
    });
  }
}

window.GameAPI = new GameAPI();
