const BaseExpert = require('./BaseExpert');

class NearbyExpert extends BaseExpert {
  constructor(deps = {}) { super('NearbyExpert', deps); }
  async handle(intent, query, context, deps) {
    const category = intent.category;
    if (!category) return 'نوع خدمات را مشخص کنید. مثال: "تعمیرگاه نزدیک"';
    const loc = context.location || context.userLocation;
    if (!loc?.latitude || !loc?.longitude) return 'برای یافتن خدمات نزدیک، لطفاً موقعیت GPS خود را فعال کنید. 📍';

    const radius = intent.radius || 5;
    const cacheKey = `${category}:${loc.latitude.toFixed(3)}:${loc.longitude.toFixed(3)}:${radius}`;
    const services = await this.getCached('nearby', cacheKey, () => deps.knowledgeBase?.getNearbyServices?.(category, { latitude: loc.latitude, longitude: loc.longitude, radius: radius * 1000 }), 180);

    if (!services?.length) return `${category} در شعاع ${radius} کیلومتری پیدا نشد.`;

    let res = `📍 نزدیک‌ترین ${category} (شعاع ${radius}km):\n`;
    services.slice(0, 3).forEach((s, i) => {
      res += `\n${i + 1}. 🏢 ${s.name} | 📏 ${s.distance}m`;
      if (s.phone) res += ` | 📞 ${s.phone}`;
      if (s.isOpen !== undefined) res += s.isOpen ? ' | ✅ باز' : ' | ❌ بسته';
    });
    if (services.length > 3) res += `\n\n... و ${services.length - 3} مورد دیگر`;
    return res;
  }
}
module.exports = NearbyExpert;
