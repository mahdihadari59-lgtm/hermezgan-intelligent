const BaseExpert = require('./BaseExpert');
const fs = require('fs');
const path = require('path');

class EmergencyExpert extends BaseExpert {
  constructor(deps = {}, configPath = './config/emergency.json') {
    super('EmergencyExpert', deps);
    const raw = fs.readFileSync(path.resolve(configPath), 'utf8');
    this.contacts = JSON.parse(raw);
  }

  _normalizeCity(city) {
    return String(city || 'default').trim().toLowerCase().replace(/\s+/g, '');
  }

  detectType(text) {
    const t = String(text || '').toLowerCase();
    if (t.includes('تصادف')) return 'accident';
    if (t.includes('پنچر')) return 'flat_tire';
    if (t.includes('خراب') || t.includes('استارت')) return 'breakdown';
    if (t.includes('آتش') || t.includes('حریق')) return 'fire';
    if (t.includes('پلیس') || t.includes('سرقت')) return 'police';
    return 'general';
  }

  async handle(intent, query, context, deps) {
    const type = this.detectType(intent.text || query);
    const loc = context.location || context.userLocation;
    const cityKey = this._normalizeCity(context.location?.city || 'default');
    const contacts = this.contacts[cityKey] || this.contacts.default;

    let res = `🚨 درخواست امداد ثبت شد\n\n`;
    switch (type) {
      case 'accident': res += `📞 اورژانس: ${contacts.emergency}\n🚔 پلیس راهور: ${contacts.police}\n`; break;
      case 'flat_tire':
      case 'breakdown': res += `🔧 در حال جستجوی امداد خودرو...\n📞 امداد خودرو: ${contacts.roadside}\n`; break;
      case 'fire': res += `📞 آتش‌نشانی: ${contacts.fire}\n`; break;
      case 'police': res += `📞 پلیس: ${contacts.police}\n`; break;
      default: res += `📞 شماره‌های اضطراری:\n`;
    }

    res += `• اورژانس: ${contacts.emergency}\n`;
    res += `• پلیس: ${contacts.police}\n`;
    res += `• آتش‌نشانی: ${contacts.fire}\n`;
    res += `• هلال احمر: ${contacts.redcrescent}\n`;
    res += `• مدیریت بحران: ${contacts.crisis || contacts.emergency}\n`;

    if (loc?.latitude && loc?.longitude) {
      res += `\n📍 موقعیت: ${loc.latitude}, ${loc.longitude}\n`;
      if (deps.emergencyService?.sendAlert) {
        try {
          await deps.emergencyService.sendAlert({ type, location: { lat: loc.latitude, lng: loc.longitude }, timestamp: new Date().toISOString(), userId: context.userId });
          res += `✅ موقعیت برای مرکز امداد ارسال شد.`;
        } catch (e) {
          res += `⚠️ خطا در ارسال. لطفاً با ${contacts.emergency} تماس بگیرید.`;
        }
      }
    } else {
      res += `\n⚠️ لطفاً GPS را فعال کنید.`;
    }
    return res;
  }
}
module.exports = EmergencyExpert;
