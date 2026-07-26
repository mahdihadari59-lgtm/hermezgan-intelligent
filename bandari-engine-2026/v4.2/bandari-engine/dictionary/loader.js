const fs = require('fs');
const path = require('path');
const config = require('../config');
const logger = require('../utils/logger');

function loadBaseWords() {
  const raw = fs.readFileSync(path.join(__dirname, 'words.json'), 'utf8');
  const data = JSON.parse(raw);

  // پشتیبانی از هر دو ساختار: قدیمی (bandari_to_persian تخت) و جدید (categories)
  const words = {};
  const wordCategory = {}; // واژه -> کلید دسته، برای مرور دسته‌ای
  const categoryMeta = {}; // کلید دسته -> برچسب فارسی

  if (data.categories) {
    for (const [catKey, catData] of Object.entries(data.categories)) {
      categoryMeta[catKey] = catData.label || catKey;
      for (const [fa, bnd] of Object.entries(catData.words || {})) {
        words[fa] = bnd;
        wordCategory[fa] = catKey;
        wordCategory[bnd] = catKey;
      }
    }
  }
  if (data.bandari_to_persian) {
    Object.assign(words, data.bandari_to_persian);
  }

  return {
    words,
    phrases: data.phrases || {},
    proverbs: data.proverbs || {},
    wordCategory,
    categoryMeta
  };
}

function loadLearnedWords() {
  try {
    if (!fs.existsSync(config.LEARNED_WORDS_FILE)) return {};
    const raw = fs.readFileSync(config.LEARNED_WORDS_FILE, 'utf8');
    const data = JSON.parse(raw);
    return data.learned || {};
  } catch (e) {
    logger.warn('نمی‌توان واژگان آموخته‌شده را خواند، شروع خالی:', e.message);
    return {};
  }
}

function persistLearnedWord(word, translation, existingLearned) {
  existingLearned[word] = translation;
  try {
    fs.mkdirSync(path.dirname(config.LEARNED_WORDS_FILE), { recursive: true });
    fs.writeFileSync(
      config.LEARNED_WORDS_FILE,
      JSON.stringify({ learned: existingLearned }, null, 2),
      'utf8'
    );
    return true;
  } catch (e) {
    logger.error('خطا در ذخیره‌سازی واژه جدید:', e.message);
    return false;
  }
}

module.exports = { loadBaseWords, loadLearnedWords, persistLearnedWord };
