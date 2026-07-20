from engine.base_engine import BaseEngine


class MedicalEngine(BaseEngine):

    def __init__(self, manager):
        super().__init__(
            name="medical",
            weight=2.0
        )
        self.manager = manager

    def search(self, query, context=None):

        results = []

        # ابتدا گراف
        results += self.manager.graph.search(query)

        # سپس FTS
        results += self.manager.fts.search(query)

        # سپس مترادف‌ها
        results += self.manager.synonym.search(query)

        return results
