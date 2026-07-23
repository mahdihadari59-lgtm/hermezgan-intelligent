const fs = require('fs');
const path = require('path');

const verified = require('./build_multilingual_verified.js');
const sourced = require('./build_multilingual_sourced.js');

const all = [...verified, ...sourced].map((e, idx) => ({ id: idx + 1, ...e }));

// بررسی تصادم روی (word_standard) در کل مجموعه، فقط برای هشدار (نه خطای سخت،
// چون ممکنه دو معنی متفاوت باشه با همون واژه استاندارد)
const seen = new Map();
const collisions = [];
for (const e of all) {
  const key = e.word_standard;
  if (seen.has(key)) collisions.push([key, seen.get(key), e.category]);
  seen.set(key, e.category);
}

const dialectCodes = ['ban', 'min', 'qes', 'jas', 'lan', 'bas', 'kha', 'rud', 'sir'];
const dialectCounts = {};
for (const code of dialectCodes) {
  dialectCounts[code] = all.filter((e) => e.dialects && e.dialects[code]).length;
}

const output = {
  meta: {
    version: '4.2.0',
    total_entries: all.length,
    verified_entries: verified.length,
    sourced_entries: sourced.length,
    dialect_word_counts: dialectCounts,
    generated_at: new Date().toISOString()
  },
  entries: all
};

fs.writeFileSync(
  path.join(__dirname, '..', 'dictionary', 'multilingual_words.json'),
  JSON.stringify(output, null, 2),
  'utf8'
);

console.log(`✅ ${all.length} ورودی نوشته شد (${verified.length} verified + ${sourced.length} sourced)`);
console.log('تعداد واژه به تفکیک گویش:', dialectCounts);
if (collisions.length) {
  console.log('⚠️ تصادم روی word_standard (بررسی دستی لازم است):', collisions);
} else {
  console.log('✅ هیچ تصادمی روی word_standard نیست');
}
