import re
from typing import List

class PersianProcessor:
    def normalize(self, text: str) -> str:
        text = text.strip()
        text = re.sub(r"\s+", " ", text)
        text = text.replace("ي", "ی").replace("ك", "ک")
        text = re.sub(r"[^\w\s\u0600-\u06FF]", "", text)
        return text

    def tokenize(self, text: str) -> List[str]:
        return self.normalize(text).split()
