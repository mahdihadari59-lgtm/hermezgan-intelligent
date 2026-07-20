import re

def normalize_persian(text):
    if not text:
        return ""

    reps = {
        'ي':'ی','ى':'ی','ﻱ':'ی','ﻲ':'ی','ﻳ':'ی','ﻴ':'ی',
        'ك':'ک','ﻙ':'ک','ﻚ':'ک','ﻛ':'ک','ﻜ':'ک',
        'ة':'ه','ۀ':'ه','ؤ':'و','ئ':'ی',
        'أ':'ا','إ':'ا',
        '۰':'0','۱':'1','۲':'2','۳':'3','۴':'4',
        '۵':'5','۶':'6','۷':'7','۸':'8','۹':'9'
    }

    for old, new in reps.items():
        text = text.replace(old, new)

    return re.sub(
        r'[\u200b\u200c\u200d\u200e\u200f\ufeff]',
        '',
        text.strip()
    )
