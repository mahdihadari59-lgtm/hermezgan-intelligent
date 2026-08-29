export const validateUsername = (username) => {
  if (!username || username.length < 3) {
    return { valid: false, message: 'نام کاربری حداقل ۳ کاراکتر باشد' };
  }
  if (username.length > 50) {
    return { valid: false, message: 'نام کاربری حداکثر ۵۰ کاراکتر' };
  }
  if (!/^[a-zA-Z0-9_]+$/.test(username)) {
    return { valid: false, message: 'فقط حروف انگلیسی، اعداد و زیرخط' };
  }
  return { valid: true };
};

export const validateEmail = (email) => {
  if (!email) return { valid: false, message: 'ایمیل الزامی است' };
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return { valid: false, message: 'ایمیل نامعتبر است' };
  }
  return { valid: true };
};

export const validatePassword = (password) => {
  if (!password || password.length < 8) {
    return { valid: false, message: 'رمز عبور حداقل ۸ کاراکتر' };
  }
  if (!/[a-z]/.test(password) || !/[A-Z]/.test(password)) {
    return { valid: false, message: 'شامل حروف بزرگ و کوچک باشد' };
  }
  if (!/[0-9]/.test(password)) {
    return { valid: false, message: 'شامل عدد باشد' };
  }
  return { valid: true };
};

export const validatePhone = (phone) => {
  if (!phone) return { valid: false, message: 'شماره موبایل الزامی است' };
  if (!/^09[0-9]{9}$/.test(phone)) {
    return { valid: false, message: 'شماره موبایل نامعتبر است' };
  }
  return { valid: true };
};

export const validateForm = (data, rules) => {
  const errors = {};
  for (const [field, validators] of Object.entries(rules)) {
    const value = data[field];
    for (const validator of validators) {
      const result = validator(value);
      if (!result.valid) {
        errors[field] = result.message;
        break;
      }
    }
  }
  return { valid: Object.keys(errors).length === 0, errors };
};
