class IntentEngine:

    def detect(self, query):

        q = query.strip()

        if "تصادف" in q:
            return "accident"

        if "وکیل" in q:
            return "lawyer"

        if "دوربین" in q:
            return "camera"

        if "پلیس" in q:
            return "police"

        if "بیمارستان" in q:
            return "hospital"

        return "general"
