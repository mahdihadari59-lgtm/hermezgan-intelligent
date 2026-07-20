import json
from pathlib import Path


class RuleEngine:
    def __init__(self, rules_dir="rules"):
        self.rules_dir = Path(rules_dir)
        self.aliases = {}
        self.entities = []
        self.load()

    def load(self):
        alias_file = self.rules_dir / "aliases.json"
        entity_file = self.rules_dir / "entities.json"

        if alias_file.exists():
            with open(alias_file, "r", encoding="utf-8") as f:
                self.aliases = json.load(f)

        if entity_file.exists():
            with open(entity_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.entities = data.get("entities", [])

    def get_alias(self, text):
        return self.aliases.get(text, text)

    def get_aliases(self):
        return self.aliases

    def get_entities(self):
        return self.entities
