class CircuitBreaker {
  constructor({ failureThreshold = 3, cooldownMs = 30000 } = {}) {
    this.failureThreshold = failureThreshold;
    this.cooldownMs = cooldownMs;
    this.state = new Map();
  }

  _get(key) {
    if (!this.state.has(key)) {
      this.state.set(key, { failures: 0, openedAt: 0, halfOpenTrial: false });
    }
    return this.state.get(key);
  }

  _isOpen(entry) {
    if (!entry.openedAt) return false;
    return (Date.now() - entry.openedAt) < this.cooldownMs;
  }

  async execute(key, fn) {
    const entry = this._get(key);
    if (this._isOpen(entry)) return null;
    try {
      const result = await fn();
      entry.failures = 0;
      entry.openedAt = 0;
      entry.halfOpenTrial = false;
      return result;
    } catch (err) {
      entry.failures += 1;
      if (entry.failures >= this.failureThreshold) {
        entry.openedAt = Date.now();
        entry.halfOpenTrial = false;
      }
      throw err;
    }
  }
}
module.exports = CircuitBreaker;
