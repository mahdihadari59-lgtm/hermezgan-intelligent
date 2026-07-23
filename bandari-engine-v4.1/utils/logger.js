const LEVELS = { error: 0, warn: 1, info: 2, debug: 3 };
const CURRENT_LEVEL = LEVELS[process.env.LOG_LEVEL] ?? LEVELS.info;

function ts() {
  return new Date().toISOString();
}

function log(level, icon, ...args) {
  if (LEVELS[level] > CURRENT_LEVEL) return;
  console.log(`${icon} [${ts()}] [${level.toUpperCase()}]`, ...args);
}

module.exports = {
  info: (...a) => log('info', 'ℹ️', ...a),
  warn: (...a) => log('warn', '⚠️', ...a),
  error: (...a) => log('error', '❌', ...a),
  debug: (...a) => log('debug', '🔍', ...a),
  success: (...a) => log('info', '✅', ...a)
};
