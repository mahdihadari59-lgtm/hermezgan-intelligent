export const APP_NAME = 'هرمزگان هوشمند';
export const APP_VERSION = '1.0.0';

export const COLORS = {
  primary: '#667eea',
  secondary: '#764ba2',
  success: '#2ed573',
  warning: '#ffa502',
  danger: '#ff4757',
  info: '#1e90ff',
  dark: '#2d3748',
  light: '#f8f9fa',
  white: '#ffffff',
  gray: '#a0aec0',
};

export const SERVICE_TYPES = {
  HOSPITAL: 'hospital',
  RESTAURANT: 'restaurant',
  TAXI: 'taxi',
  PHARMACY: 'pharmacy',
  SCHOOL: 'school',
};

export const CAMERA_STATUS = {
  ACTIVE: 'active',
  INSTALLING: 'installing',
  PENDING: 'pending',
};

export const DEFAULT_COORDINATES = {
  BANDAR_ABBAS: { lat: 27.2158, lng: 56.2808 },
  QESHM: { lat: 26.9500, lng: 55.4700 },
  KISH: { lat: 26.5200, lng: 53.9800 },
};

export const DEFAULT_RADIUS = 5;
export const MAX_SEARCH_RADIUS = 50;

export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
export const API_VERSION = 'v1';
export const API_PREFIX = `/api/${API_VERSION}`;

export const CACHE_TTL = {
  SHORT: 60,
  MEDIUM: 300,
  LONG: 3600,
  VERY_LONG: 86400,
};

export const ERROR_MESSAGES = {
  NETWORK: 'خطا در ارتباط با سرور',
  UNAUTHORIZED: 'لطفاً وارد حساب کاربری خود شوید',
  NOT_FOUND: 'مورد درخواستی یافت نشد',
  SERVER: 'خطای سرور، لطفاً بعداً تلاش کنید',
  VALIDATION: 'اطلاعات وارد شده صحیح نیست',
};

export const LANGUAGES = {
  FA: 'fa',
  EN: 'en',
};
