const BaseExpert = require('./BaseExpert');

class TransportExpert extends BaseExpert {
  constructor(deps = {}) { super('TransportExpert', deps); }

  detectType(text) {
    const t = String(text || '').toLowerCase();
    if (t.includes('پرواز') || t.includes('فرودگاه')) return 'flight';
    if (t.includes('شناور') || t.includes('لندی') || t.includes('کشتی')) return 'ship';
    if (t.includes('اتوبوس')) return 'bus';
    if (t.includes('تاکسی')) return 'taxi';
    return 'transport';
  }

  async handle(intent, query, context, deps) {
    const type = this.detectType(query);
    const destination = intent.destination || null;
    const origin = context.location?.city || 'بندرعباس';
    const info = await deps.knowledgeBase?.getTransportInfo?.(type, destination, origin);
    if (!info) return `اطلاعات ${type} ${destination || ''} در دسترس نیست.`;

    let icon = '🚏';
    if (type === 'flight') icon = '✈️';
    else if (type === 'ship') icon = '🚢';
    else if (type === 'bus') icon = '🚌';
    else if (type === 'taxi') icon = '🚖';

    let response = `${icon} اطلاعات ${type}${destination ? ` برای ${destination}` : ''}:\n`;
    if (info.schedule) response += `⏰ برنامه سفر: ${info.schedule}\n`;
    if (info.price) response += `💰 هزینه: ${info.price} تومان\n`;
    if (info.duration) response += `⏱️ مدت سفر: ${info.duration}\n`;
    if (info.phone) response += `📞 رزرو/استعلام: ${info.phone}\n`;
    if (info.note) response += `💡 ${info.note}`;
    return response.trim();
  }
}
module.exports = TransportExpert;
