const BaseExpert = require('./BaseExpert');

class TrafficExpert extends BaseExpert {
  constructor(deps = {}) { super('TrafficExpert', deps); }
  async handle(intent, query, context, deps) {
    const area = intent.destination || context.location?.city || 'بندرعباس';
    const traffic = await this.getCached('traffic', area, () => deps.knowledgeBase?.getTrafficInfo?.(area), 60);
    if (!traffic || !Object.keys(traffic).length) return `اطلاعات ترافیکی ${area} در دسترس نیست.`;
    let res = `🚦 وضعیت ترافیک ${area}:\n`;
    for (const [road, status] of Object.entries(traffic)) {
      const emoji = status === 'سنگین' ? '🔴' : status === 'نیمه سنگین' ? '🟡' : status === 'بسته' ? '⛔' : '🟢';
      res += `${emoji} ${road}: ${status}\n`;
    }
    return res.trim();
  }
}
module.exports = TrafficExpert;
