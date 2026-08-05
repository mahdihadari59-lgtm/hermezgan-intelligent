import uuid
import random
import string
import hashlib
import re
import json
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
import os
import ipaddress
from pathlib import Path


def generate_uuid() -> str:
    return str(uuid.uuid4())


def generate_short_uuid(length: int = 8) -> str:
    return str(uuid.uuid4())[:length]


def generate_otp(length: int = 6) -> str:
    return ''.join(random.choices(string.digits, k=length))


def generate_random_string(length: int = 16, include_special: bool = False) -> str:
    chars = string.ascii_letters + string.digits
    if include_special:
        chars += string.punctuation
    return ''.join(random.choices(chars, k=length))


def generate_random_number(min_val: int = 0, max_val: int = 100) -> int:
    return random.randint(min_val, max_val)


def generate_verification_code(length: int = 6) -> str:
    return generate_otp(length)


def slugify(text: str, separator: str = "-") -> str:
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', separator, text)
    return text.strip(separator)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length] + suffix


def clean_text(text: str) -> str:
    text = re.sub(r'<[^>]+>', '', text)
    text = ' '.join(text.split())
    return text.strip()


def extract_numbers(text: str) -> List[int]:
    return [int(x) for x in re.findall(r'\d+', text)]


def normalize_persian_text(text: str) -> str:
    arabic_to_persian = {'ي': 'ی', 'ك': 'ک', 'ة': 'ه', 'أ': 'ا', 'إ': 'ا', 'آ': 'ا'}
    for arabic, persian in arabic_to_persian.items():
        text = text.replace(arabic, persian)
    arabic_numbers = '٠١٢٣٤٥٦٧٨٩'
    persian_numbers = '۰۱۲۳۴۵۶۷۸۹'
    for i, char in enumerate(arabic_numbers):
        text = text.replace(char, persian_numbers[i])
    return text


def convert_to_persian_digits(text: str) -> str:
    english_to_persian = {'0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴', '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'}
    for english, persian in english_to_persian.items():
        text = text.replace(english, persian)
    return text


def convert_to_english_digits(text: str) -> str:
    persian_to_english = {'۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4', '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'}
    for persian, english in persian_to_english.items():
        text = text.replace(persian, english)
    return text


def get_current_timestamp() -> str:
    return datetime.utcnow().isoformat()


def get_current_datetime() -> datetime:
    return datetime.utcnow()


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    return dt.strftime(format_str)


def time_ago(dt: datetime) -> str:
    now = datetime.utcnow()
    diff = now - dt
    seconds = diff.total_seconds()
    minutes = seconds / 60
    hours = minutes / 60
    days = hours / 24
    weeks = days / 7
    months = days / 30
    years = days / 365
    if seconds < 60:
        return "چند لحظه پیش"
    elif minutes < 60:
        return f"{int(minutes)} دقیقه پیش"
    elif hours < 24:
        return f"{int(hours)} ساعت پیش"
    elif days < 7:
        return f"{int(days)} روز پیش"
    elif weeks < 4:
        return f"{int(weeks)} هفته پیش"
    elif months < 12:
        return f"{int(months)} ماه پیش"
    else:
        return f"{int(years)} سال پیش"


def calculate_age(birth_date: datetime) -> int:
    today = datetime.utcnow()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


def get_persian_date(dt: Optional[datetime] = None) -> str:
    if dt is None:
        dt = datetime.utcnow()
    try:
        import jdatetime
        jd = jdatetime.datetime.fromgregorian(datetime=dt)
        return jd.strftime("%Y/%m/%d")
    except ImportError:
        return dt.strftime("%Y-%m-%d")


def get_persian_datetime(dt: Optional[datetime] = None) -> str:
    if dt is None:
        dt = datetime.utcnow()
    try:
        import jdatetime
        jd = jdatetime.datetime.fromgregorian(datetime=dt)
        return jd.strftime("%Y/%m/%d %H:%M:%S")
    except ImportError:
        return dt.strftime("%Y-%m-%d %H:%M:%S")


def human_readable_size(size: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"


def parse_json(data: str) -> Optional[Dict]:
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return None


def to_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False)


def is_valid_uuid(uuid_string: str) -> bool:
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False


def get_client_ip(request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    return request.client.host if request.client else "unknown"


def get_user_agent(request) -> str:
    return request.headers.get("User-Agent", "unknown")


def is_mobile_device(user_agent: str) -> bool:
    mobile_patterns = ['Mobile', 'Android', 'iPhone', 'iPad', 'iPod', 'BlackBerry', 'Windows Phone']
    return any(pattern in user_agent for pattern in mobile_patterns)


def get_browser_info(user_agent: str) -> Dict[str, str]:
    info = {"browser": "Unknown", "os": "Unknown", "device": "Desktop"}
    if "Chrome" in user_agent and "Edge" not in user_agent:
        info["browser"] = "Chrome"
    elif "Firefox" in user_agent:
        info["browser"] = "Firefox"
    elif "Safari" in user_agent and "Chrome" not in user_agent:
        info["browser"] = "Safari"
    elif "Edge" in user_agent:
        info["browser"] = "Edge"
    elif "Opera" in user_agent:
        info["browser"] = "Opera"
    if "Windows" in user_agent:
        info["os"] = "Windows"
    elif "Mac OS" in user_agent:
        info["os"] = "macOS"
    elif "Linux" in user_agent:
        info["os"] = "Linux"
    elif "Android" in user_agent:
        info["os"] = "Android"
    elif "iOS" in user_agent or "iPhone" in user_agent:
        info["os"] = "iOS"
    if is_mobile_device(user_agent):
        info["device"] = "Mobile"
    return info
