from typing import List, Dict, Any, Optional, Callable
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DataSync:
    """
    کلاس همگام‌سازی داده‌ها بین منابع مختلف
    """

    def __init__(self):
        self.sync_log = []

    def sync_data(self, source: List[Dict[str, Any]], target: List[Dict[str, Any]], key: str, on_update: Optional[Callable] = None, on_create: Optional[Callable] = None, on_delete: Optional[Callable] = None) -> Dict[str, Any]:
        result = {"created": 0, "updated": 0, "deleted": 0, "errors": 0}
        target_dict = {item[key]: item for item in target if key in item}

        for source_item in source:
            if key not in source_item:
                result["errors"] += 1
                continue
            source_key = source_item[key]
            if source_key in target_dict:
                if on_update:
                    try:
                        on_update(source_item, target_dict[source_key])
                        result["updated"] += 1
                    except Exception as e:
                        logger.error(f"❌ Error updating {source_key}: {e}")
                        result["errors"] += 1
                else:
                    result["updated"] += 1
            else:
                if on_create:
                    try:
                        on_create(source_item)
                        result["created"] += 1
                    except Exception as e:
                        logger.error(f"❌ Error creating {source_key}: {e}")
                        result["errors"] += 1
                else:
                    result["created"] += 1

        if on_delete:
            source_keys = {item[key] for item in source if key in item}
            for target_item in target:
                if key in target_item and target_item[key] not in source_keys:
                    try:
                        on_delete(target_item)
                        result["deleted"] += 1
                    except Exception as e:
                        logger.error(f"❌ Error deleting {target_item.get(key)}: {e}")
                        result["errors"] += 1

        self.sync_log.append({"timestamp": datetime.utcnow().isoformat(), "result": result})
        logger.info(f"✅ Sync completed: created={result['created']}, updated={result['updated']}, deleted={result['deleted']}")
        return result

    def get_sync_history(self, limit: int = 100) -> List[Dict]:
        return self.sync_log[-limit:]

    def clear_history(self):
        self.sync_log.clear()


_data_sync = None


def get_data_sync() -> DataSync:
    global _data_sync
    if _data_sync is None:
        _data_sync = DataSync()
    return _data_sync
