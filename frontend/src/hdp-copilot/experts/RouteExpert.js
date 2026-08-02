const BaseExpert = require('./BaseExpert');

class RouteExpert extends BaseExpert {
  constructor(deps = {}) { super('RouteExpert', deps); }
  async handle(intent, query, context, deps) {
    const dest = intent.destination;
    if (!dest) return 'مقصد را مشخص کنید. مثال: "راه قشم چطوره؟"';
    const cacheKey = `${intent.origin || 'unknown'}:${dest}`;
    const route = await this.getCached('route', cacheKey, () => deps.knowledgeBase?.getRoute?.(dest, intent.origin), 300);
    if (!route) return `مسیر ${dest} در پایگاه داده موجود نیست.`;
    let res = `🚗 مسیر ${intent.origin ? `${intent.origin} → ` : ''}${dest}: ${route.distance} کیلومتر، حدود ${route.duration} دقیقه.`;
    if (route.traffic) res += `\n📊 وضعیت ترافیک: ${route.traffic}`;
    if (route.tip) res += `\n💡 ${route.tip}`;
    if (route.alternative) res += `\n🛣️ مسیر جایگزین: ${route.alternative}`;
    return res;
  }
}
module.exports = RouteExpert;
