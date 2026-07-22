import { DEFAULT_COORDINATES } from './constants';

export const calculateDistance = (lat1, lng1, lat2, lng2) => {
  const R = 6371;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLng = (lng2 - lng1) * Math.PI / 180;
  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLng / 2) * Math.sin(dLng / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
};

export const formatPersianDate = (timestamp) => {
  const date = new Date(timestamp);
  return date.toLocaleDateString('fa-IR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

export const formatTime = (timestamp) => {
  const date = new Date(timestamp);
  return date.toLocaleTimeString('fa-IR', {
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const timeAgo = (timestamp) => {
  const now = Date.now();
  const diff = now - timestamp;
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (seconds < 60) return 'لحظاتی پیش';
  if (minutes < 60) return `${minutes} دقیقه پیش`;
  if (hours < 24) return `${hours} ساعت پیش`;
  if (days < 30) return `${days} روز پیش`;
  return formatPersianDate(timestamp);
};

export const generateId = () => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2, 5);
};

export const isValidEmail = (email) => {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
};

export const isValidPhone = (phone) => {
  return /^09[0-9]{9}$/.test(phone);
};

export const groupBy = (array, key) => {
  return array.reduce((result, item) => {
    const groupKey = item[key];
    if (!result[groupKey]) result[groupKey] = [];
    result[groupKey].push(item);
    return result;
  }, {});
};

export const getDefaultLocation = (city = 'bandar-abbas') => {
  const locations = {
    'bandar-abbas': DEFAULT_COORDINATES.BANDAR_ABBAS,
    'qeshm': DEFAULT_COORDINATES.QESHM,
    'kish': DEFAULT_COORDINATES.KISH,
  };
  return locations[city] || DEFAULT_COORDINATES.BANDAR_ABBAS;
};

export const slugify = (text) => {
  return text
    .toLowerCase()
    .replace(/[\s_]+/g, '-')
    .replace(/[^\w\-]+/g, '')
    .replace(/--+/g, '-');
};
