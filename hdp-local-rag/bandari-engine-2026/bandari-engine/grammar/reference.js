const fs = require('fs');
const path = require('path');
const logger = require('../utils/logger');

/**
 * لایه مرجع دستور زبان — داده‌های واقعی از مستندات کاربر (نه ساخته این سرویس).
 * شامل: ضمایر، صرف افعال رایج، اصطلاحات خانوادگی، اصطلاحات/کنایات، مکالمات
 * نمونه به تفکیک موقعیت، و قواعد نشانه‌گذاری مفعول («را»-حذفی).
 */
class GrammarReference {
  constructor() {
    this.pronouns = [];
    this.verbConjugations = [];
    this.familyTerms = [];
    this.idioms = [];
    this.dialogues = [];
    this.objectMarking = {};
    this.grammarRules = {};
    this.loaded = false;
    this.load();
  }

  load() {
    try {
      const dataDir = path.join(__dirname, 'data');
      this.pronouns = JSON.parse(fs.readFileSync(path.join(dataDir, 'pronouns.json'), 'utf8'));
      this.verbConjugations = JSON.parse(fs.readFileSync(path.join(dataDir, 'verb_conjugations.json'), 'utf8'));
      this.familyTerms = JSON.parse(fs.readFileSync(path.join(dataDir, 'family_terms.json'), 'utf8'));
      this.idioms = JSON.parse(fs.readFileSync(path.join(dataDir, 'idioms.json'), 'utf8'));
      this.dialogues = JSON.parse(fs.readFileSync(path.join(dataDir, 'dialogues.json'), 'utf8'));
      this.objectMarking = JSON.parse(fs.readFileSync(path.join(dataDir, 'object_marking.json'), 'utf8'));
      this.grammarRules = JSON.parse(fs.readFileSync(path.join(dataDir, 'grammar_rules.json'), 'utf8'));
      this.loaded = true;

      const idiomCount = this.idioms.reduce((sum, s) => sum + s.items.length, 0);
      const dialogueLineCount = this.dialogues.reduce((sum, s) => sum + s.lines.length, 0);
      logger.success(
        `Grammar reference loaded: ${idiomCount} idioms, ${this.dialogues.length} dialogue scenarios (${dialogueLineCount} lines), ${this.verbConjugations.length} verb conjugations`
      );
    } catch (e) {
      logger.error('خطا در بارگذاری مرجع دستور زبان:', e.message);
      this.loaded = false;
    }
  }

  getPronouns() {
    return this.pronouns;
  }

  getVerbConjugations(verb) {
    if (!verb) return this.verbConjugations;
    return this.verbConjugations.filter((v) => v.header.includes(verb));
  }

  getFamilyTerms() {
    return this.familyTerms;
  }

  getIdioms(category) {
    if (!category) return this.idioms;
    return this.idioms.filter((s) => s.header.includes(category));
  }

  /** فهرست تخت همه اصطلاحات، برای جستجوی ساده */
  flatIdioms() {
    const flat = [];
    for (const section of this.idioms) {
      for (const item of section.items) {
        flat.push({ ...item, category: section.header });
      }
    }
    return flat;
  }

  searchIdiom(term) {
    return this.flatIdioms().filter(
      (i) => i.term.includes(term) || i.meaning.includes(term)
    );
  }

  getDialogues(scenario) {
    if (!scenario) return this.dialogues;
    return this.dialogues.filter((s) => s.scenario.includes(scenario));
  }

  getObjectMarking() {
    return this.objectMarking;
  }

  getGrammarRules() {
    return this.grammarRules;
  }

  getStats() {
    return {
      loaded: this.loaded,
      pronounTables: this.pronouns.length,
      verbConjugations: this.verbConjugations.length,
      familyTermTables: this.familyTerms.length,
      idiomCount: this.flatIdioms().length,
      dialogueScenarios: this.dialogues.length
    };
  }
}

module.exports = GrammarReference;
