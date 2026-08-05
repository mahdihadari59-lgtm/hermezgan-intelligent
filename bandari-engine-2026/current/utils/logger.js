const colors = {
  reset: '\x1b[0m', bright: '\x1b[1m', dim: '\x1b[2m',
  red: '\x1b[31m', green: '\x1b[32m', yellow: '\x1b[33m',
  blue: '\x1b[34m', magenta: '\x1b[35m', cyan: '\x1b[36m',
  white: '\x1b[37m', gray: '\x1b[90m'
};

class Logger {
  constructor() {
    this.level = process.env.LOG_LEVEL || 'info';
    this.levels = { debug: 0, info: 1, warn: 2, error: 3, success: 1 };
  }

  _log(level, message, ...args) {
    if (this.levels[level] < this.levels[this.level]) return;
    const timestamp = new Date().toISOString();
    const levelColors = { debug: colors.gray, info: colors.blue, warn: colors.yellow, error: colors.red, success: colors.green };
    const color = levelColors[level] || colors.white;
    console.log(`${colors.dim}[${timestamp}]${colors.reset} ${color}${level.toUpperCase().padEnd(7)}${colors.reset} ${message}`, ...args);
  }

  debug(message, ...args) { this._log('debug', message, ...args); }
  info(message, ...args) { this._log('info', message, ...args); }
  warn(message, ...args) { this._log('warn', message, ...args); }
  error(message, ...args) { this._log('error', message, ...args); }
  success(message, ...args) { this._log('success', message, ...args); }
}

module.exports = new Logger();
