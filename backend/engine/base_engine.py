from abc import ABC, abstractmethod

class BaseEngine(ABC):
    """
    کلاس پایه تمام موتورهای HDP

    همه موتورهای جستجو باید از این کلاس ارث‌بری کنند.
    """

    def __init__(self, name, weight=1.0):
        self.name = name
        self.weight = weight

    @abstractmethod
    def search(self, query, context=None):
        """
        باید لیستی از نتایج برگرداند.

        خروجی استاندارد:

        [
            {
                "id": 123,
                "score": 0.92,
                "source": "graph",
                "title": "...",
                "content": "...",
                "metadata": {}
            }
        ]
        """
        pass

    def normalize_score(self, score):
        """
        محدود کردن امتیاز بین صفر و یک
        """
        if score < 0:
            return 0.0

        if score > 1:
            return 1.0

        return float(score)

    def build_result(
        self,
        doc_id,
        score,
        title="",
        content="",
        metadata=None
    ):
        """
        ساخت خروجی استاندارد
        """

        if metadata is None:
            metadata = {}

        return {
            "doc_id": doc_id,
            "id": doc_id,          # برای سازگاری با کدهای قدیمی
            "score": self.normalize_score(score),
            "source": self.name,
            "title": title,
            "content": content,
            "metadata": metadata
        }

    def __repr__(self):
        return f"<Engine {self.name} weight={self.weight}>"
