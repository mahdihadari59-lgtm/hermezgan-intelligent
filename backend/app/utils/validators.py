import re
import json
from typing import Tuple, Optional, Any, List
from datetime import datetime
import ipaddress
from email_validator import validate_email as validate_email_lib, EmailNotValidError
import phonenumbers


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    try:
        validate_email_lib(email)
        return True, None
    except EmailNotValidError as e:
        return False, str(e)


def validate_phone(phone: str, country: str = "IR") -> Tuple[bool, Optional[str]]:
    try:
        phone = re.sub(r'[\s\-\(\)]', '', phone)
        if country == "IR":
            pattern = r'^09\d{9}$'
            if re.match(pattern, phone):
                return True, None
            return False, "شماره تلفن باید با 09 شروع و 11 رقم باشد"
        parsed = phonenumbers.parse(phone, country)
        if phonenumbers.is_valid_number(parsed):
            return True, None
        return False, "شماره تلفن نامعتبر است"
    except Exception as e:
        return False, str(e)


def validate_mobile(phone: str) -> Tuple[bool, Optional[str]]:
    phone = re.sub(r'[\s\-\(\)]', '', phone)
    pattern = r'^09(1[0-9]|2[0-9]|3[0-9]|9[0-9])[0-9]{7}$'
    if re.match(pattern, phone):
        return True, None
    return False, "شماره موبایل نامعتبر است"


def validate_national_code(national_code: str) -> Tuple[bool, Optional[str]]:
    national_code = re.sub(r'[\s\-]', '', national_code)
    if len(national_code) != 10:
        return False, "کد ملی باید ۱۰ رقم باشد"
    if not national_code.isdigit():
        return False, "کد ملی باید عددی باشد"
    invalid_codes = ['0000000000', '1111111111', '2222222222', '3333333333', '4444444444', '5555555555', '6666666666', '7777777777', '8888888888', '9999999999']
    if national_code in invalid_codes:
        return False, "کد ملی نامعتبر است"
    check = int(national_code[9])
    s = sum(int(national_code[i]) * (10 - i) for i in range(9))
    remainder = s % 11
    if remainder < 2:
        valid = check == remainder
    else:
        valid = check == 11 - remainder
    if not valid:
        return False, "کد ملی نامعتبر است"
    return True, None


def validate_iranian_identity(national_code: str) -> Tuple[bool, Optional[str]]:
    return validate_national_code(national_code)


def validate_postal_code(postal_code: str) -> Tuple[bool, Optional[str]]:
    postal_code = re.sub(r'[\s\-]', '', postal_code)
    if len(postal_code) != 10:
        return False, "کد پستی باید ۱۰ رقم باشد"
    if not postal_code.isdigit():
        return False, "کد پستی باید عددی باشد"
    pattern = r'^(?!(\d)\1{9})\d{10}$'
    if re.match(pattern, postal_code):
        return True, None
    return False, "کد پستی نامعتبر است"


def validate_iranian_bank_card(card_number: str) -> Tuple[bool, Optional[str]]:
    card_number = re.sub(r'[\s\-]', '', card_number)
    if len(card_number) != 16:
        return False, "شماره کارت باید ۱۶ رقم باشد"
    if not card_number.isdigit():
        return False, "شماره کارت باید عددی باشد"
    total = 0
    for i, digit in enumerate(card_number):
        d = int(digit)
        if i % 2 == 0:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    if total % 10 == 0:
        return True, None
    return False, "شماره کارت نامعتبر است"


def validate_iban(iban: str) -> Tuple[bool, Optional[str]]:
    iban = re.sub(r'[\s\-]', '', iban).upper()
    if not iban.startswith("IR"):
        return False, "شبا باید با IR شروع شود"
    if len(iban) != 26:
        return False, "شبا باید ۲۶ کاراکتر باشد"
    if not iban[2:].isdigit():
        return False, "بعد از IR باید عدد باشد"
    digits = iban[4:] + iban[:4]
    digits = ''.join(str(ord(c) - 55) if c.isalpha() else c for c in digits)
    if int(digits) % 97 != 1:
        return False, "شبا نامعتبر است"
    return True, None


def validate_iranian_plate(plate: str) -> Tuple[bool, Optional[str]]:
    plate = re.sub(r'[\s\-]', '', plate)
    pattern = r'^\d{2}[آ-ی]{3}\d{2}[آ-ی]$'
    if re.match(pattern, plate):
        return True, None
    return False, "پلاک خودرو نامعتبر است"


def validate_url(url: str) -> Tuple[bool, Optional[str]]:
    pattern = r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/]?'
    if re.match(pattern, url):
        return True, None
    return False, "آدرس URL نامعتبر است"


def validate_ip(ip: str) -> Tuple[bool, Optional[str]]:
    try:
        ipaddress.ip_address(ip)
        return True, None
    except ValueError:
        return False, "آدرس IP نامعتبر است"


def validate_latitude(latitude: float) -> Tuple[bool, Optional[str]]:
    if -90 <= latitude <= 90:
        return True, None
    return False, "عرض جغرافیایی باید بین -۹۰ تا ۹۰ باشد"


def validate_longitude(longitude: float) -> Tuple[bool, Optional[str]]:
    if -180 <= longitude <= 180:
        return True, None
    return False, "طول جغرافیایی باید بین -۱۸۰ تا ۱۸۰ باشد"


def validate_coordinates(lat: float, lng: float) -> Tuple[bool, Optional[str]]:
    lat_valid, lat_error = validate_latitude(lat)
    if not lat_valid:
        return False, lat_error
    lng_valid, lng_error = validate_longitude(lng)
    if not lng_valid:
        return False, lng_error
    return True, None


def validate_date(date_str: str, fmt: str = "%Y-%m-%d") -> Tuple[bool, Optional[str]]:
    try:
        datetime.strptime(date_str, fmt)
        return True, None
    except ValueError:
        return False, f"تاریخ باید به فرمت {fmt} باشد"


def validate_time(time_str: str, fmt: str = "%H:%M") -> Tuple[bool, Optional[str]]:
    try:
        datetime.strptime(time_str, fmt)
        return True, None
    except ValueError:
        return False, f"زمان باید به فرمت {fmt} باشد"


def validate_datetime(dt_str: str) -> Tuple[bool, Optional[str]]:
    try:
        datetime.fromisoformat(dt_str)
        return True, None
    except ValueError:
        return False, "تاریخ و زمان باید به فرمت ISO باشد"


def validate_password_strength(password: str, min_length: int = 8, require_uppercase: bool = True, require_lowercase: bool = True, require_digit: bool = True, require_special: bool = True) -> Tuple[bool, str]:
    if len(password) < min_length:
        return False, f"رمز عبور باید حداقل {min_length} کاراکتر باشد"
    if require_uppercase and not any(c.isupper() for c in password):
        return False, "رمز عبور باید حداقل شامل یک حرف بزرگ باشد"
    if require_lowercase and not any(c.islower() for c in password):
        return False, "رمز عبور باید حداقل شامل یک حرف کوچک باشد"
    if require_digit and not any(c.isdigit() for c in password):
        return False, "رمز عبور باید حداقل شامل یک عدد باشد"
    if require_special and not any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?/" for c in password):
        return False, "رمز عبور باید حداقل شامل یک کاراکتر خاص باشد"
    return True, "رمز عبور معتبر است"


def validate_uuid(uuid_string: str) -> Tuple[bool, Optional[str]]:
    try:
        from uuid import UUID
        UUID(uuid_string)
        return True, None
    except ValueError:
        return False, "UUID نامعتبر است"


def validate_json(json_string: str) -> Tuple[bool, Optional[str]]:
    try:
        json.loads(json_string)
        return True, None
    except json.JSONDecodeError as e:
        return False, str(e)


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> Tuple[bool, Optional[str]]:
    import os
    ext = os.path.splitext(filename)[1].lower()
    if ext in allowed_extensions:
        return True, None
    return False, f"پسوند {ext} مجاز نیست. پسوندهای مجاز: {', '.join(allowed_extensions)}"


def validate_file_size(file_size: int, max_size: int) -> Tuple[bool, Optional[str]]:
    if file_size <= max_size:
        return True, None
    max_mb = max_size / (1024 * 1024)
    return False, f"حجم فایل باید کمتر از {max_mb:.1f} MB باشد"


def validate_mime_type(mime_type: str, allowed_mime_types: List[str]) -> Tuple[bool, Optional[str]]:
    if mime_type in allowed_mime_types:
        return True, None
    return False, f"MIME type {mime_type} مجاز نیست"
