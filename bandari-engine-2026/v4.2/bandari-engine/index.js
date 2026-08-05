const express = require('express');
const cors = require('cors');

const config = require('./config');
const logger = require('./utils/logger');

const Dictionary = require('./dictionary');
const MultilingualDictionary = require('./dictionary/multilingual');
const DialectDetector = require('./dialect');
const MorphologyAnalyzer = require('./morphology');
const GrammarEngine = require('./grammar');
const IntentAnalyzer = require('./intent');
const ContextEngine = require('./context');
const RAGEngine = require('./rag');
const LLMTranslator = require('./llm');
const createRoutes = require('./api/routes');

const app = express();
app.use(cors());
app.use(express.json());

logger.info('🌊 Bandari Engine v4.2 — راه‌اندازی معماری ۸ لایه‌ای + دیکشنری ۹-گویشی...');

const engines = {
  dictionary: new Dictionary(),
  multilingual: new MultilingualDictionary(),
  dialect: new DialectDetector(),
  morphology: new MorphologyAnalyzer(),
  grammar: new GrammarEngine(),
  intent: new IntentAnalyzer(),
  context: new ContextEngine(),
  rag: new RAGEngine(),
  llm: new LLMTranslator()
};

// اصطلاحات/ضرب‌المثل‌های دیکشنری را به دانش‌نامه RAG اضافه می‌کنیم
for (const [saying, meaning] of Object.entries(engines.dictionary.getProverbs())) {
  engines.rag.addSample(saying, meaning);
}

app.use('/api', createRoutes(engines));

const server = app.listen(config.PORT, () => {
  logger.success(`Bandari Engine روی http://localhost:${config.PORT} در حال اجراست`);
  logger.info(`${engines.dictionary.getStats().totalWords} واژه بارگذاری شد`);
});

function shutdown() {
  logger.info('در حال خاموش‌سازی...');
  engines.context.shutdown();
  server.close(() => process.exit(0));
}

process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);

module.exports = app;
