import re
from typing import List, Dict, Any


class Matcher:
    def __init__(self):
        self._cache = {}

    def _compile(self, pattern: str):
        if pattern not in self._cache:
            self._cache[pattern] = re.compile(pattern)
        return self._cache[pattern]

    def match(self, pattern: str, text: str) -> List[str]:
        if not pattern or not text:
            return []

        try:
            regex = self._compile(pattern)
            matches = regex.findall(text)

            result = []

            for item in matches:
                if isinstance(item, tuple):
                    result.append(item[0].strip())
                else:
                    result.append(str(item).strip())

            return result

        except re.error:
            return []

    def match_rules(self, rules: List[Dict[str, Any]], text: str):
        entities = []

        for rule in rules:
            matches = self.match(rule["pattern"], text)

            for value in matches:
                entities.append({
                    "title": value,
                    "name": rule["name"],
                    "category": rule["category"],
                    "relation": rule["relation"]
                })

        return entities
