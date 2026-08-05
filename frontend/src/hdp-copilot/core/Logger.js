const fs = require('fs');
const path = require('path');
const { once } = require('events');

class Logger {
  constructor(logDir = './logs') {
    this.logDir = logDir;
    this.currentDate = null;
    this.stream = null;
    if (!fs.existsSync(logDir)) fs.mkdirSync(logDir, { recursive: true });
  }

  _getFilePath() {
    const day = new Date().toISOString().slice(0, 10);
    return { day, file: path.join(this.logDir, `${day}.ndjson`) };
  }

  _ensureStream() {
    const { day, file } = this._getFilePath();
    if (this.currentDate !== day || !this.stream) {
      if (this.stream) {
        try { this.stream.end(); } catch (_) {}
      }
      this.currentDate = day;
      this.stream = fs.createWriteStream(file, { flags: 'a' });
      this.stream.on('error', (err) => console.error('[LOGGER_STREAM_ERROR]', err));
    }
  }

  async _write(level, data) {
    try {
      this._ensureStream();
      const line = JSON.stringify({ timestamp: new Date().toISOString(), level, ...data }) + '\n';
      if (this.stream && !this.stream.write(line)) await once(this.stream, 'drain');
      if (process.env.NODE_ENV !== 'production') {
        const fn = level === 'error' ? 'error' : level === 'warn' ? 'warn' : 'log';
        console[fn](`[${level.toUpperCase()}]`, data);
      }
    } catch (err) {
      console.error('[LOGGER_WRITE_ERROR]', err);
    }
  }

  info(data) { return this._write('info', data); }
  warn(data) { return this._write('warn', data); }
  error(data) { return this._write('error', data); }
}
module.exports = Logger;
