# HDP Copilot v4 Wiring

## Source of truth
- KnowledgeProvider -> `data/hdp_v2.db`
- GraphProvider -> `knowledge_nodes` / `knowledge_edges`
- VectorProvider -> `knowledge_embeddings` / `semantic_relations`
- CopilotGateway -> Providerها
- chat_service.py -> CopilotGateway

## Flow
User Query -> chat_service -> CopilotGateway -> SearchPipeline -> Ranker -> Final Answer

## Notes
- هیچ JSON fallback نباید در مسیر پاسخ‌گویی متن فعال باشد.
- Bandari Engine فقط برای intent / detect / translate استفاده می‌شود.
- SearchPipeline فقط از دیتای اصلی دانش بخواند.
