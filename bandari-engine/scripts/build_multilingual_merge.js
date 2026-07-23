const fs = require('fs');
const path = require('path');

let verified = [];
try { verified = require('./build_multilingual_verified.js'); } catch(e) { console.warn('⚠️ verified یافت نشد'); }

const all = verified.map((e, idx) => ({ id: idx + 1, ...e }));

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
    sourced_entries: 0,
    dialect_word_counts: dialectCounts,
    generated_at: new Date().toISOString()
  },
  entries: all
};

const outPath = path.join(__dirname, '..', 'dictionary', 'multilingual_words.json');
fs.writeFileSync(outPath, JSON.stringify(output, null, 2), 'utf8');
console.log(`✅ ${all.length} ورودی نوشته شد`);
