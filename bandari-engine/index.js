#!/usr/bin/env node

const express = require('express');
const cors = require('cors');
const path = require('path');
const logger = require('./utils/logger');
const config = require('./config');
const routes = require('./api/routes');
const RAGEngine = require('./rag');
const dictionary = require('./dictionary');

// ============================================================
// بارگذاری اولیه
// ============================================================
logger.info('🌊 Bandari Engine v4.2.0');
logger.info('📚 بارگذاری دیکشنری...');
logger.info('🧠 بارگذاری RAG Engine...');

// Initialize RAG
const rag = new RAGEngine();

// ============================================================
// Express App
// ============================================================
const app = express();
const PORT = config.PORT || 5200;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Request Logger
app.use((req, res, next) => {
  logger.info(`${req.method} ${req.path}`);
  next();
});

// Routes
app.use('/api', routes);

// Root
app.get('/', (req, res) => {
  res.json({
    name: 'Bandari Engine',
    version: '4.2.0',
    status: 'running',
    endpoints: {
      health: '/api/health',
      dictionary: '/api/dictionary/search?q=سلام',
      multilingual: '/api/multilingual/search?q=سلام',
      rag: '/api/rag/search?q=بندرعباس',
      llm: '/api/llm/status'
    }
  });
});

// ============================================================
// Start Server
// ============================================================
app.listen(PORT, '0.0.0.0', () => {
  logger.success(`✅ Bandari Engine v4.2.0 اجرا شد`);
  logger.info(`🌐 http://localhost:${PORT}`);
  logger.info(`📚 دیکشنری: ${Object.keys(dictionary.getCategories?.() || {}).length || 0} دسته`);
  
  const stats = rag.getStats();
  logger.info(`🧠 RAG: ${stats.totalKnowledgeEntries} مدخل`);
  logger.info(`🤖 LLM: ${process.env.BANDARI_LLM_ENABLED === '1' ? 'فعال' : 'غیرفعال'}`);
});

// ============================================================
// Graceful Shutdown
// ============================================================
process.on('SIGINT', () => {
  logger.info('🛑 دریافت سیگنال خاموشی...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  logger.info('🛑 دریافت سیگنال توقف...');
  process.exit(0);
});
