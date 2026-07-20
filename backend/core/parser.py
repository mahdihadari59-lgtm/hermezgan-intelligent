# core/parser.py
import re
from typing import Optional, Dict, Any, List
from .document import Document


class TextParser:
    """
    پارسر سطح پایین: متن خام را به ساختار Document تبدیل می‌کند.
    هیچ دانش دامنه‌ای ندارد و فقط عملیات زیر را انجام می‌دهد:
    - پاکسازی متن (تبدیل خطوط جدید، یکسان‌سازی فاصله‌ها)
    - شکستن به پاراگراف (blocks)
    - شکستن به جمله (sentences) با الگوی پیشرفته (فارسی و انگلیسی)
    - توکن‌سازی اولیه (tokens)
    - نگهداری metadata
    """

    def __init__(self):
        self.sentence_splitter = re.compile(
            r'(?<=[\.\!\?؟؛…])\s+'
        )

    def parse(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> Document:
        if not text or not isinstance(text, str):
            raise ValueError("ورودی باید یک رشتهٔ غیرخالی باشد.")

        doc = Document()
        doc.content = text
        doc.metadata = metadata.copy() if metadata else {}

        if metadata:
            doc.node_id = metadata.get('node_id')
            doc.category = metadata.get('category', '')
            doc.title = metadata.get('title', '')

        cleaned_text = self._clean_text(text)

        if not doc.title:
            doc.title = cleaned_text[:100].strip()
            if not doc.title:
                doc.title = "بدون عنوان"

        doc.blocks = self._split_blocks(cleaned_text)
        doc.sentences = self._split_sentences(cleaned_text)
        doc.tokens = self._tokenize_sentences(doc.sentences)

        return doc

    def _clean_text(self, text: str) -> str:
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        return text.strip()

    def _split_blocks(self, text: str) -> List[str]:
        if not text:
            return []
        return [
            block.strip()
            for block in re.split(r"\n\s*\n", text)
            if block.strip()
        ]

    def _split_sentences(self, text: str) -> List[str]:
        if not text:
            return []
        text = text.replace("\n", " ")
        sentences = self.sentence_splitter.split(text)
        return [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

    def _tokenize_sentences(self, sentences: List[str]) -> List[List[str]]:
        tokens = []
        for sent in sentences:
            # حذف علائم نگارشی رایج
            cleaned = re.sub(r"[،؛,:!?؟\.\(\)\[\]«»\"]", " ", sent)
            words = re.split(r"[ \u200c]+", cleaned)
            words = [w for w in words if w]
            tokens.append(words)
        return tokens
