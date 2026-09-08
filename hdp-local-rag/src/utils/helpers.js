
export const generateId = () => Date.now().toString(36) + Math.random().toString(36).substr(2);
export const formatTime = (timestamp) => new Date(timestamp).toLocaleTimeString('fa-IR', { hour: '2-digit', minute: '2-digit' });
export const formatPersianDate = (timestamp) => new Date(timestamp).toLocaleDateString('fa-IR', { year: 'numeric', month: 'long', day: 'numeric' });
export const calculateDistance = (lat1, lon1, lat2, lon2) => {
  const R = 6371;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(dLat/2) * Math.sin(dLat/2) + Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
};
export const timeAgo = (timestamp) => {
  const now = Date.now();
  const diff = now - timestamp;
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);
  if (minutes < 1) return 'لحظاتی پیش';
  if (minutes < 60) return minutes + ' دقیقه پیش';
  if (hours < 24) return hours + ' ساعت پیش';
  if (days < 7) return days + ' روز پیش';
  return formatPersianDate(timestamp);
};
export const isValidEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
export const isValidPhone = (phone) => /^09[0-9]{9}$/.test(phone);
export const slugify = (text) => text.toLowerCase().replace(/[^\w\s-]/g, '').replace(/[\s_-]+/g, '-').replace(/^-+|-+$/g, '');
export const groupBy = (array, key) => array.reduce((result, item) => {
  const groupKey = item[key];
  if (!result[groupKey]) result[groupKey] = [];
  result[groupKey].push(item);
  return result;
}, {});
export const getDefaultLocation = () => ({ lat: 27.2158, lng: 56.2808, name: 'بندرعباس' });
