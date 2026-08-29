class ConversationSummary {
  build(messages = [], previous = {}) {
    const recent = Array.isArray(messages) ? messages.slice(-8) : [];
    const userTurns = recent.filter(m => m.role === 'user');
    const assistantTurns = recent.filter(m => m.role === 'assistant');
    const intents = [...new Set(userTurns.map(m => m.intent).filter(Boolean))];
    const lastDestination = [...userTurns].reverse().find(m => m.destination)?.destination || previous.lastDestination || null;
    const lastCategory = [...userTurns].reverse().find(m => m.category)?.category || previous.lastCategory || null;
    const lastQuery = userTurns.length ? userTurns[userTurns.length - 1].text : null;

    const textParts = [];
    if (lastDestination) textParts.push(`مقصد: ${lastDestination}`);
    if (lastCategory) textParts.push(`دسته: ${lastCategory}`);
    if (intents.length) textParts.push(`نیت‌ها: ${intents.join('، ')}`);
    if (lastQuery) textParts.push(`آخرین پرسش: ${lastQuery}`);

    return {
      text: textParts.join(' | '),
      lastDestination,
      lastCategory,
      intents,
      updatedAt: new Date().toISOString(),
      recentTurns: { user: userTurns.length, assistant: assistantTurns.length }
    };
  }
}
module.exports = ConversationSummary;
