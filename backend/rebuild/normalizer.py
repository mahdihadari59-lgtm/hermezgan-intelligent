import re

PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
ENGLISH_DIGITS = "0123456789"

DIGIT_MAP = str.maketrans(PERSIAN_DIGITS, ENGLISH_DIGITS)


def normalize(text: str) -> str:

    if text is None:
        return ""

    text = str(text)

    # حذف نیم‌فاصله
    text = text.replace("\u200c", " ")

    # تبدیل اعداد فارسی به انگلیسی
    text = text.translate(DIGIT_MAP)

    # یکسان‌سازی حروف عربی
    text = text.replace("ي", "ی")
    text = text.replace("ك", "ک")

    # حذف فاصله‌های اضافی
    text = re.sub(r"\s+", " ", text)

    return text.strip()
