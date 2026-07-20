# core/normalizer.py

import re
from typing import Dict, List, Union

from .rule_engine import RuleEngine


class Normalizer:
    """
    عادی‌سازی متن برای پروژه HDP
    """

    def __init__(self, source: Union[RuleEngine, Dict[str, str], None] = None):
        if isinstance(source, RuleEngine):
            self.aliases = source.get_aliases()
        elif isinstance(source, dict):
            self.aliases = source
        else:
            self.aliases = {}

        # حذف اعراب
        self.diacritics = re.compile(r'[\u064B-\u0652\u0670]')

        # فقط فاصله‌های معمولی
        self.space_normalizer = re.compile(r' +')

    def normalize(self, text: str) -> str:
        if not text or not isinstance(text, str):
            return ""

        # حذف فاصله‌های ابتدا و انتها
        text = text.strip()

        # تبدیل چند فاصله به یک فاصله
        text = self.space_normalizer.sub(" ", text)

        # حذف اعراب
        text = self.diacritics.sub("", text)

        # اعمال Alias ها (از طولانی به کوتاه)
        if self.aliases:
            for alias in sorted(self.aliases.keys(), key=len, reverse=True):
                canonical = self.aliases[alias]
                text = text.replace(alias, canonical)

        # حذف فاصله‌های اضافه دوباره
        text = self.space_normalizer.sub(" ", text).strip()

        return text

    def normalize_entity(self, entity_title: str) -> str:
        return self.normalize(entity_title)

    def normalize_list(self, texts: List[str]) -> List[str]:
        return [self.normalize(t) for t in texts]
