from typing import List, Dict, Any, Optional, Union, Callable
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DataValidator:
    """
    کلاس اعتبارسنجی داده‌ها
    """

    def validate_data(self, data: List[Dict[str, Any]], rules: Dict[str, Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        valid = []
        invalid = []
        for i, item in enumerate(data):
            errors = self.validate_item(item, rules)
            if errors:
                invalid.append({"index": i, "data": item, "errors": errors})
            else:
                valid.append(item)
        return {"valid": valid, "invalid": invalid}

    def validate_item(self, item: Dict[str, Any], rules: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
        errors = {}
        for field, field_rules in rules.items():
            value = item.get(field)
            for rule_name, rule_value in field_rules.items():
                error = self._apply_rule(field, value, rule_name, rule_value)
                if error:
                    if field not in errors:
                        errors[field] = []
                    errors[field].append(error)
        return errors

    def _apply_rule(self, field: str, value: Any, rule_name: str, rule_value: Any) -> Optional[str]:
        if rule_name == "required":
            if value is None or value == "":
                return "این فیلد الزامی است"
        elif rule_name == "type":
            if value is not None:
                if rule_value == "string" and not isinstance(value, str):
                    return "باید رشته باشد"
                elif rule_value == "number" and not isinstance(value, (int, float)):
                    return "باید عدد باشد"
                elif rule_value == "integer" and not isinstance(value, int):
                    return "باید عدد صحیح باشد"
                elif rule_value == "boolean" and not isinstance(value, bool):
                    return "باید بولین باشد"
                elif rule_value == "date" and not isinstance(value, datetime):
                    return "باید تاریخ باشد"
                elif rule_value == "list" and not isinstance(value, list):
                    return "باید لیست باشد"
        elif rule_name == "min":
            if value is not None:
                if isinstance(value, (int, float)) and value < rule_value:
                    return f"باید حداقل {rule_value} باشد"
                if isinstance(value, str) and len(value) < rule_value:
                    return f"باید حداقل {rule_value} کاراکتر باشد"
                if isinstance(value, list) and len(value) < rule_value:
                    return f"باید حداقل {rule_value} آیتم باشد"
        elif rule_name == "max":
            if value is not None:
                if isinstance(value, (int, float)) and value > rule_value:
                    return f"باید حداکثر {rule_value} باشد"
                if isinstance(value, str) and len(value) > rule_value:
                    return f"باید حداکثر {rule_value} کاراکتر باشد"
                if isinstance(value, list) and len(value) > rule_value:
                    return f"باید حداکثر {rule_value} آیتم باشد"
        elif rule_name == "pattern":
            if value is not None and isinstance(value, str):
                if not re.match(rule_value, value):
                    return "فرمت نامعتبر است"
        elif rule_name == "email":
            if value is not None and isinstance(value, str):
                pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(pattern, value):
                    return "ایمیل نامعتبر است"
        elif rule_name == "phone":
            if value is not None and isinstance(value, str):
                pattern = r'^09\d{9}$'
                if not re.match(pattern, value):
                    return "شماره تلفن نامعتبر است"
        elif rule_name == "in":
            if value is not None and value not in rule_value:
                return f"باید یکی از {rule_value} باشد"
        elif rule_name == "not_in":
            if value is not None and value in rule_value:
                return f"نمی‌تواند یکی از {rule_value} باشد"
        return None

    def validate_required_fields(self, data: List[Dict[str, Any]], fields: List[str]) -> List[Dict[str, Any]]:
        valid = []
        for item in data:
            missing = [f for f in fields if f not in item or item[f] is None]
            if not missing:
                valid.append(item)
        return valid

    def validate_schema(self, data: List[Dict[str, Any]], schema: Dict[str, str]) -> List[Dict[str, Any]]:
        valid = []
        for item in data:
            if all(field in item for field in schema):
                valid.append(item)
        return valid

    def check_for_duplicates(self, data: List[Dict[str, Any]], key: str) -> List[Dict[str, Any]]:
        seen = set()
        duplicates = []
        for item in data:
            if key in item:
                value = item[key]
                if value in seen:
                    duplicates.append(item)
                else:
                    seen.add(value)
        return duplicates


_data_validator = None


def get_data_validator() -> DataValidator:
    global _data_validator
    if _data_validator is None:
        _data_validator = DataValidator()
    return _data_validator
