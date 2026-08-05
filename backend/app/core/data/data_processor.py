from typing import List, Dict, Any, Optional, Callable, Union
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DataProcessor:
    """
    کلاس پردازش و تبدیل داده‌ها
    """

    def filter_data(self, data: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        result = []
        for item in data:
            match = True
            for key, value in filters.items():
                if key not in item:
                    match = False
                    break
                if isinstance(value, dict):
                    if "like" in value:
                        if not re.search(value["like"], str(item[key])):
                            match = False
                            break
                    elif "in" in value:
                        if item[key] not in value["in"]:
                            match = False
                            break
                    elif "gt" in value:
                        if item[key] <= value["gt"]:
                            match = False
                            break
                    elif "lt" in value:
                        if item[key] >= value["lt"]:
                            match = False
                            break
                    elif "gte" in value:
                        if item[key] < value["gte"]:
                            match = False
                            break
                    elif "lte" in value:
                        if item[key] > value["lte"]:
                            match = False
                            break
                else:
                    if item[key] != value:
                        match = False
                        break
            if match:
                result.append(item)
        return result

    def sort_data(self, data: List[Dict[str, Any]], sort_by: Union[str, List[str]], reverse: bool = False) -> List[Dict[str, Any]]:
        if isinstance(sort_by, str):
            sort_by = [sort_by]

        def key_func(item):
            keys = []
            for field in sort_by:
                value = item.get(field, 0)
                if isinstance(value, str):
                    value = value.lower()
                keys.append(value)
            return tuple(keys)

        return sorted(data, key=key_func, reverse=reverse)

    def group_data(self, data: List[Dict[str, Any]], group_by: Union[str, List[str]]) -> Dict[str, List[Dict[str, Any]]]:
        if isinstance(group_by, str):
            group_by = [group_by]
        result = {}
        for item in data:
            key_parts = []
            for field in group_by:
                key_parts.append(str(item.get(field, "")))
            key = "||".join(key_parts)
            if key not in result:
                result[key] = []
            result[key].append(item)
        return result

    def aggregate_data(self, data: List[Dict[str, Any]], group_by: Optional[str] = None, aggregations: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        if group_by is None:
            result = {}
            for item in data:
                for field, func in (aggregations or {}).items():
                    if field not in result:
                        result[field] = []
                    result[field].append(item.get(field))
            return [self._apply_aggregation(result, aggregations)]

        grouped = self.group_data(data, group_by)
        result = []
        for key, group in grouped.items():
            row = {"_group_key": key}
            key_parts = key.split("||")
            for i, field in enumerate(group_by):
                row[field] = key_parts[i]
            for field, func in (aggregations or {}).items():
                values = [item.get(field) for item in group if item.get(field) is not None]
                if values:
                    row[f"{field}_{func}"] = self._apply_aggregation_func(values, func)
                else:
                    row[f"{field}_{func}"] = None
            result.append(row)
        return result

    def _apply_aggregation(self, data: Dict, aggregations: Dict) -> Dict:
        result = {}
        for field, values in data.items():
            func = aggregations.get(field)
            if func and values:
                result[field] = self._apply_aggregation_func(values, func)
        return result

    def _apply_aggregation_func(self, values: List, func: str) -> Any:
        try:
            if func == "sum":
                return sum(values)
            elif func == "avg":
                return sum(values) / len(values)
            elif func == "count":
                return len(values)
            elif func == "min":
                return min(values)
            elif func == "max":
                return max(values)
            elif func == "first":
                return values[0]
            elif func == "last":
                return values[-1]
            else:
                return values
        except Exception:
            return None

    def transform_data(self, data: List[Dict[str, Any]], transformations: Dict[str, Callable]) -> List[Dict[str, Any]]:
        result = []
        for item in data:
            transformed = item.copy()
            for field, func in transformations.items():
                if field in transformed:
                    transformed[field] = func(transformed[field])
            result.append(transformed)
        return result

    def normalize_data(self, data: List[Dict[str, Any]], fields: List[str]) -> List[Dict[str, Any]]:
        result = []
        for item in data:
            normalized = item.copy()
            for field in fields:
                if field in normalized:
                    value = normalized[field]
                    if isinstance(value, str):
                        value = ' '.join(value.split())
                        value = value.lower()
                        normalized[field] = value
                    elif isinstance(value, datetime):
                        normalized[field] = value.isoformat()
            result.append(normalized)
        return result

    def deduplicate_data(self, data: List[Dict[str, Any]], keys: Union[str, List[str]]) -> List[Dict[str, Any]]:
        if isinstance(keys, str):
            keys = [keys]
        seen = set()
        result = []
        for item in data:
            key_parts = []
            for k in keys:
                key_parts.append(str(item.get(k, "")))
            key = "||".join(key_parts)
            if key not in seen:
                seen.add(key)
                result.append(item)
        return result

    def merge_data(self, data1: List[Dict[str, Any]], data2: List[Dict[str, Any]], key: str, how: str = 'inner') -> List[Dict[str, Any]]:
        dict2 = {item[key]: item for item in data2 if key in item}
        if how == 'inner':
            result = []
            for item in data1:
                if key in item and item[key] in dict2:
                    result.append({**item, **dict2[item[key]]})
        elif how == 'left':
            result = []
            for item in data1:
                if key in item and item[key] in dict2:
                    result.append({**item, **dict2[item[key]]})
                else:
                    result.append(item.copy())
        elif how == 'right':
            result = []
            for item in data2:
                if key in item and any(d.get(key) == item[key] for d in data1):
                    for d1 in data1:
                        if d1.get(key) == item[key]:
                            result.append({**d1, **item})
                            break
                else:
                    result.append(item.copy())
        else:
            all_keys = set()
            for item in data1:
                if key in item:
                    all_keys.add(item[key])
            for item in data2:
                if key in item:
                    all_keys.add(item[key])
            result = []
            for k in all_keys:
                d1 = next((x for x in data1 if x.get(key) == k), {})
                d2 = next((x for x in data2 if x.get(key) == k), {})
                merged = {**d1, **d2}
                if merged:
                    result.append(merged)
        return result


_data_processor = None


def get_data_processor() -> DataProcessor:
    global _data_processor
    if _data_processor is None:
        _data_processor = DataProcessor()
    return _data_processor
