const BaseExpert = require('./BaseExpert');

class WeatherExpert extends BaseExpert {
  constructor(deps = {}) { super('WeatherExpert', deps); }
  async handle(intent, query, context, deps) {
    const city = intent.destination || context.lastDestination || 'بندرعباس';
    const weather = await this.getCached('weather', city, () => deps.knowledgeBase?.getWeatherInfo?.(city), 600);
    if (!weather) return `اطلاعات آب و هوای ${city} در دسترس نیست.`;
    return `🌡️ ${weather.city || city}: ${weather.temp}°C، رطوبت ${weather.humidity}%\n🌬️ باد: ${weather.wind || 'نامشخص'}\n☀️ وضعیت: ${weather.condition || 'آفتابی'}\n💡 ${weather.tip || 'کولر فراموش نشود'}`;
  }
}
module.exports = WeatherExpert;
