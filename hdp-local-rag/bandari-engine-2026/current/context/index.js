const config = require('../config');

class ContextEngine {
  constructor(ttlMs = config.CONTEXT_TTL_MS) {
    this.sessions = new Map();
    this.ttlMs = ttlMs;
    this._startCleanup();
  }

  _startCleanup() {
    this.cleanupInterval = setInterval(() => this._sweepExpired(), Math.min(this.ttlMs, 5 * 60 * 1000));
    if (this.cleanupInterval.unref) this.cleanupInterval.unref();
  }

  _sweepExpired() {
    const now = Date.now();
    for (const [id, session] of this.sessions) {
      if (now - session.lastSeen > this.ttlMs) this.sessions.delete(id);
    }
  }

  _getOrCreate(sessionId) {
    if (!this.sessions.has(sessionId)) {
      this.sessions.set(sessionId, { history: [], lastSeen: Date.now() });
    }
    const session = this.sessions.get(sessionId);
    session.lastSeen = Date.now();
    return session;
  }

  addTurn(sessionId, turn) {
    if (!sessionId) return;
    const session = this._getOrCreate(sessionId);
    session.history.push({ ...turn, at: Date.now() });
    if (session.history.length > 20) session.history.shift();
  }

  getHistory(sessionId, limit = 5) {
    if (!sessionId || !this.sessions.has(sessionId)) return [];
    const session = this.sessions.get(sessionId);
    session.lastSeen = Date.now();
    return session.history.slice(-limit);
  }

  getStats() { return { activeSessions: this.sessions.size }; }

  shutdown() { clearInterval(this.cleanupInterval); }
}

module.exports = ContextEngine;
