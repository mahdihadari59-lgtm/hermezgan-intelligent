# core/extractor.py

from .rule_engine import RuleEngine
from .normalizer import Normalizer
from .matcher import Matcher
from .document import Document


class Extractor:
    """
    استخراج موجودیت‌ها از متن با استفاده از RuleEngine، Normalizer و Matcher
    """

    def __init__(self, rule_engine: RuleEngine):
        self.rule_engine = rule_engine
        self.normalizer = Normalizer(rule_engine)
        self.matcher = Matcher()

    def extract(self, doc: Document) -> Document:
        """
        استخراج موجودیت‌ها از یک Document
        """

        # دریافت متن
        text = ""

        if hasattr(doc, "sentences") and doc.sentences:
            text = " ".join(doc.sentences)
        elif hasattr(doc, "content"):
            text = doc.content

        if not text:
            doc.entities = []
            return doc

        # نرمال‌سازی
        text = self.normalizer.normalize(text)

        entities = []

        # قوانین موجودیت‌ها
        rules = self.rule_engine.get_entities()

        for rule in rules:

            pattern = rule.get("pattern")
            if not pattern:
                continue

            matches = self.matcher.match(pattern, text)

            for match in matches:

                title = self.normalizer.normalize_entity(match)

                entity = {
                    "title": title,
                    "raw_title": match,
                    "name": rule.get("name"),
                    "category": rule.get("category"),
                    "relation": rule.get("relation")
                }

                entities.append(entity)

        doc.entities = entities

        return doc
