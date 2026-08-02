const BaseExpert = require('./BaseExpert');

class TouristExpert extends BaseExpert {
  constructor(deps = {}) { super('TouristExpert', deps); }
  async handle(intent, query, context, deps) {
    const destination = intent.destination;
    if (!destination) return 'مقصد گردشگری را مشخص کنید. مثال: "جاذبه‌های قشم" یا "دیدنی‌های هرمز"';

    const places = await this.getCached('tourism', destination, () => deps.knowledgeBase?.getTouristPlaces?.(destination), 86400);
    if (!places?.length) return `جاذبه‌ای برای ${destination} یافت نشد.`;

    let response = `🏝️ جاذبه‌های گردشگری ${destination}:\n`;
    for (let i = 0; i < Math.min(5, places.length); i++) {
      const place = places[i];
      response += `\n${i + 1}. ${place.name}`;
      if (place.description) response += ` - ${place.description}`;
      if (place.rating) response += ` ⭐${place.rating}`;
    }
    if (places.length > 5) response += `\n\n... و ${places.length - 5} مکان دیگر`;
    return response;
  }
}
module.exports = TouristExpert;
