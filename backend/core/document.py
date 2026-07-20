# core/document.py

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass(slots=True)
class Document:
    """
    مدل استاندارد یک سند در HDP
    """

    node_id: Optional[int] = None

    title: str = ""
    category: str = ""
    content: str = ""

    blocks: List[str] = field(default_factory=list)
    sentences: List[str] = field(default_factory=list)
    tokens: List[List[str]] = field(default_factory=list)

    entities: List[Dict[str, Any]] = field(default_factory=list)
    nodes: List[Dict[str, Any]] = field(default_factory=list)
    links: List[Dict[str, Any]] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):

        if self.node_id is not None and not isinstance(self.node_id, int):
            raise TypeError("node_id must be int or None")

        if not isinstance(self.title, str):
            raise TypeError("title must be str")

        if not isinstance(self.category, str):
            raise TypeError("category must be str")

        if not isinstance(self.content, str):
            raise TypeError("content must be str")

        if self.sentences is None:
            self.sentences = []

        if self.entities is None:
            self.entities = []

        if self.nodes is None:
            self.nodes = []

        if self.links is None:
            self.links = []

        if self.metadata is None:
            self.metadata = {}
