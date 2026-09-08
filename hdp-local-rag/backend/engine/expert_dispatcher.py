from engine.experts.medical_engine import MedicalEngine


class ExpertDispatcher:

    def __init__(self, manager):
        self.manager = manager

        self.engines = {
            "medical": MedicalEngine(manager)
        }

    def dispatch(self, intent_results):

        if not intent_results:
            return None

        intent = intent_results[0]["title"]

        return self.engines.get(intent)
