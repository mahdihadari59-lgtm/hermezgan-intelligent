from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class KnowledgeRecord:

    id: Optional[int] = None

    title: str = ""

    content: str = ""

    category: str = "general"

    subcategory: str = ""

    topic: str = ""

    subtopic: str = ""

    city: str = ""

    province: str = "هرمزگان"

    source: str = "knowledge_json"

    priority: int = 5

    confidence: float = 1.0

    verified: bool = False

    entity_type: str = ""

    intent: str = ""

    main_intent: str = ""

    sub_intent: str = ""

    keywords: List[str] = field(default_factory=list)

    tags: List[str] = field(default_factory=list)

    entities: List[str] = field(default_factory=list)

    relations: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):

        return self.__dict__
