import json
import csv
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import logging
import yaml
import xml.etree.ElementTree as ET
from io import StringIO

logger = logging.getLogger(__name__)


class DataLoader:
    """
    کلاس بارگذاری داده از منابع مختلف
    پشتیبانی از JSON, CSV, Excel, YAML, XML, SQL
    """

    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def load_json(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        path = self._resolve_path(file_path)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"❌ File not found: {path}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON: {e}")
            return {}

    def load_jsonl(self, file_path: Union[str, Path]) -> List[Dict[str, Any]]:
        path = self._resolve_path(file_path)
        data = []
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data.append(json.loads(line))
            return data
        except FileNotFoundError:
            logger.error(f"❌ File not found: {path}")
            return []

    def load_csv(self, file_path: Union[str, Path], delimiter: str = ',', encoding: str = 'utf-8', **kwargs) -> List[Dict[str, Any]]:
        path = self._resolve_path(file_path)
        try:
            with open(path, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f, delimiter=delimiter, **kwargs)
                return list(reader)
        except FileNotFoundError:
            logger.error(f"❌ File not found: {path}")
            return []

    def load_excel(self, file_path: Union[str, Path], sheet_name: Optional[Union[str, int]] = None) -> Union[List[Dict[str, Any]], Dict[str, List[Dict[str, Any]]]]:
        try:
            import pandas as pd
            path = self._resolve_path(file_path)
            if sheet_name is None:
                excel_file = pd.ExcelFile(path)
                result = {}
                for sheet in excel_file.sheet_names:
                    df = pd.read_excel(path, sheet_name=sheet)
                    result[sheet] = df.to_dict('records')
                return result
            else:
                df = pd.read_excel(path, sheet_name=sheet_name)
                return df.to_dict('records')
        except ImportError:
            logger.error("❌ pandas not installed. Install with: pip install pandas openpyxl")
            return []
        except Exception as e:
            logger.error(f"❌ Error loading Excel: {e}")
            return []

    def load_yaml(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        path = self._resolve_path(file_path)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"❌ File not found: {path}")
            return {}
        except yaml.YAMLError as e:
            logger.error(f"❌ Invalid YAML: {e}")
            return {}

    def load_xml(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        path = self._resolve_path(file_path)
        try:
            tree = ET.parse(path)
            return self._xml_to_dict(tree.getroot())
        except FileNotFoundError:
            logger.error(f"❌ File not found: {path}")
            return {}
        except ET.ParseError as e:
            logger.error(f"❌ Invalid XML: {e}")
            return {}

    def load_text(self, file_path: Union[str, Path]) -> str:
        path = self._resolve_path(file_path)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"❌ File not found: {path}")
            return ""

    def load_from_string(self, data: str, format: str = 'json') -> Union[Dict, List, str]:
        if format == 'json':
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return {}
        elif format == 'csv':
            f = StringIO(data)
            reader = csv.DictReader(f)
            return list(reader)
        elif format == 'yaml':
            try:
                return yaml.safe_load(data)
            except yaml.YAMLError:
                return {}
        elif format == 'xml':
            try:
                root = ET.fromstring(data)
                return self._xml_to_dict(root)
            except ET.ParseError:
                return {}
        return data

    def _xml_to_dict(self, element: ET.Element) -> Dict[str, Any]:
        result = {}
        for key, value in element.attrib.items():
            result[f"@{key}"] = value
        if element.text and element.text.strip():
            result["#text"] = element.text.strip()
        for child in element:
            child_data = self._xml_to_dict(child)
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data
        return result if result else None

    def _resolve_path(self, file_path: Union[str, Path]) -> Path:
        path = Path(file_path)
        if not path.is_absolute():
            path = self.data_dir / path
        return path


_data_loader = None


def get_data_loader() -> DataLoader:
    global _data_loader
    if _data_loader is None:
        _data_loader = DataLoader()
    return _data_loader
