from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import logging

from app.core.data.data_loader import get_data_loader
from app.core.data.data_validator import get_data_validator

logger = logging.getLogger(__name__)


class DataImporter:
    """
    کلاس واردسازی داده‌ها با اعتبارسنجی
    """

    def __init__(self):
        self.loader = get_data_loader()
        self.validator = get_data_validator()

    def import_data(self, file_path: Union[str, Path], format: str = 'auto', validate: bool = True, rules: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        path = Path(file_path)
        if format == 'auto':
            format = self._detect_format(path)

        if format == 'json':
            data = self.loader.load_json(path)
        elif format == 'csv':
            data = self.loader.load_csv(path, **kwargs)
        elif format == 'excel':
            data = self.loader.load_excel(path, **kwargs)
        elif format == 'yaml':
            data = self.loader.load_yaml(path)
        elif format == 'xml':
            data = self.loader.load_xml(path)
        else:
            logger.error(f"❌ Unsupported format: {format}")
            return {"success": False, "error": f"فرمت {format} پشتیبانی نمی‌شود"}

        if not data:
            return {"success": False, "error": "داده‌ای یافت نشد"}

        if isinstance(data, dict) and not isinstance(data, list):
            data = [data]

        if validate and rules:
            validation_result = self.validator.validate_data(data, rules)
            if validation_result["invalid"]:
                return {
                    "success": False,
                    "error": f"{len(validation_result['invalid'])} رکورد نامعتبر",
                    "invalid": validation_result["invalid"],
                    "valid": validation_result["valid"]
                }

        return {
            "success": True,
            "data": data,
            "count": len(data) if isinstance(data, list) else 1,
            "format": format
        }

    def _detect_format(self, file_path: Path) -> str:
        suffix = file_path.suffix.lower()
        format_map = {
            '.json': 'json', '.jsonl': 'jsonl', '.csv': 'csv',
            '.xlsx': 'excel', '.xls': 'excel',
            '.yaml': 'yaml', '.yml': 'yaml',
            '.xml': 'xml', '.txt': 'text'
        }
        return format_map.get(suffix, 'json')

    def import_from_string(self, data: str, format: str = 'json', validate: bool = True, rules: Optional[Dict] = None) -> Dict[str, Any]:
        loaded = self.loader.load_from_string(data, format)
        if not loaded:
            return {"success": False, "error": "داده‌ای یافت نشد"}
        if isinstance(loaded, dict) and not isinstance(loaded, list):
            loaded = [loaded]
        if validate and rules:
            validation_result = self.validator.validate_data(loaded, rules)
            if validation_result["invalid"]:
                return {
                    "success": False,
                    "error": f"{len(validation_result['invalid'])} رکورد نامعتبر",
                    "invalid": validation_result["invalid"],
                    "valid": validation_result["valid"]
                }
        return {
            "success": True,
            "data": loaded,
            "count": len(loaded) if isinstance(loaded, list) else 1,
            "format": format
        }


_data_importer = None


def get_data_importer() -> DataImporter:
    global _data_importer
    if _data_importer is None:
        _data_importer = DataImporter()
    return _data_importer
