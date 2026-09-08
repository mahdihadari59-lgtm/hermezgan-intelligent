import re
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class Intent:
    name: str
    confidence: float
    entities: Dict[str, str]

class IntentRouter:
    INTENTS = {
        "routing": ["مسیر", "راه", "چطور برم", "کجاست", "نقشه", "برو به", "فاصله"],
        "traffic": ["ترافیک", "شلوغی", "تقاطع", "دوربین", "محدودیت سرعت", "تعطیلی"],
        "tourism": ["گردشگری", "جاذبه", "دیدنی", "تفریح", "ساحل", "موزه", "تور"],
        "business": ["فروشگاه", "رستوران", "هتل", "بازار", "خرید", "کافه", "پمپ بنزین"],
        "auto": ["ماشین", "خودرو", "تعمیر", "لاستیک", "باطری", "روشن نمیشه", "سرویس"],
        "legal": ["قانون", "تصادف", "بیمه", "خلافی", "پلیس", "راهنمایی رانندگی"],
        "dialect": ["بندری", "مینابی", "قشمی", "بستکی", "لهجه", "محلی"],
        "local": ["بندرعباس", "کیش", "قشم", "میناب", "بندرلنگه", "حاجی آباد", "کجاست"],
    }

    def route(self, text: str) -> Intent:
        text_norm = text.lower().strip()
        scores = {}
        for intent, keywords in self.INTENTS.items():
            score = sum(1 for k in keywords if k in text_norm)
            scores[intent] = score / max(len(keywords), 1)

        best = max(scores, key=scores.get)
        confidence = scores[best]
        if confidence < 0.1:
            best = "general"
            confidence = 1.0

        entities = self._extract_entities(text_norm)
        return Intent(name=best, confidence=confidence, entities=entities)

    def _extract_entities(self, text: str) -> Dict[str, str]:
        entities = {}
        city_pattern = r"(بندرعباس|کیش|قشم|میناب|بندرلنگه|حاجی\s*آباد|بستک|پارسیان|رودان|جاسک|ابوموسی)"
        m = re.search(city_pattern, text)
        if m:
            entities["city"] = m.group(1).replace(" ", "")
        return entities
