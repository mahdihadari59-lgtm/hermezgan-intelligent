// اسکریپت ساخت بخش verified دیکشنری چندگویشی
const entries = [];

function addVerified(e) {
  entries.push({ ...e, confidence_score: e.confidence_score ?? 80, data_quality: 'verified' });
}

addVerified({
  word_standard: 'سلام', part_of_speech: 'interjection', category: 'greeting', subcategory: 'greeting',
  definition: 'سلام کردن، احوالپرسی',
  dialects: { ban: 'سَلام براری', min: 'سَلام چَکری؟', qes: 'سَلام قِشمی', jas: 'سَلام', lan: 'سَلام چَکری؟', bas: 'سَلام', kha: 'سَلام', rud: 'سَلام چَگُری؟', sir: 'سَلام' },
  ipa: { ban: 'sælɒːm bærɒːriː', min: 'sælɒːm tʃækriː' },
  examples: { ban: 'سَلام براری چطوری؟', min: 'سَلام چَکری؟' },
  region_usage: 'همه مناطق', etymology: 'عربی', cultural_note: 'رایج‌ترین احوالپرسی', confidence_score: 90
});

addVerified({
  word_standard: 'چطوری', part_of_speech: 'question', category: 'greeting', subcategory: 'question',
  definition: 'پرسیدن حال و احوال',
  dialects: { ban: 'ابی چش', min: 'چَکری', qes: 'چطوری', jas: 'چطوری', lan: 'چَکری', bas: 'چطوری', kha: 'چطوری', rud: 'چَگُری', sir: 'چطوری' },
  ipa: { ban: 'æbiː tʃeʃ', min: 'tʃækriː' },
  examples: { ban: 'ابی چش داداش؟', min: 'چَکری رفیق؟' },
  region_usage: 'همه مناطق', etymology: 'فارسی', cultural_note: 'پرسش روزمره', confidence_score: 95
});

module.exports = entries;
