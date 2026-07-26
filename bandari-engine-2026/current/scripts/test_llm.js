const config = require('../config');
const logger = require('../utils/logger');
const LLMTranslator = require('../llm');

async function testLLM() {
  logger.info('\n🧪 Testing LLM Translator...');
  logger.info(`   Provider: ${config.LLM.provider}`);
  logger.info(`   API URL: ${config.LLM.apiUrl}`);
  
  const llm = new LLMTranslator();
  if (!llm.enabled) {
    logger.warn('⚠️ LLM is disabled. Set BANDARI_LLM_ENABLED=1');
    return;
  }
  
  logger.info('\n🏥 Health Check...');
  const isHealthy = await llm.healthCheck();
  logger.info(`   Health: ${isHealthy ? '✅ Online' : '❌ Offline'}`);
  if (!isHealthy) {
    logger.warn('⚠️ LLM service not responding. Check if llama.cpp is running.');
    return;
  }
  
  const tests = ['سلام چطوری؟', 'بریم دریا', 'مادرت خوبه؟'];
  logger.info('\n📝 Running tests...');
  for (const text of tests) {
    logger.info(`\n📝 Input: "${text}"`);
    const result = await llm.translate(text, []);
    if (result.used) logger.success(`   ✅ "${result.translation}"`);
    else logger.warn(`   ⚠️ ${result.reason}`);
  }
  logger.info('\n✅ Test completed!');
}

if (require.main === module) testLLM().catch(console.error);
module.exports = testLLM;
