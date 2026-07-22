import json
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import logging
import pandas as pd
from io import StringIO, BytesIO
import zipfile

logger = logging.getLogger(__name__)


class DataExporter:
    """
    کلاس خروجی‌گیری از داده‌ها
    """

    def __init__(self):
        self.export_dir = Path("exports")
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def export_json(self, data: Union[List, Dict], filename: str, indent: int = 2, ensure_ascii: bool = False) -> str:
        file_path = self.export_dir / filename
        if not file_path.suffix:
            file_path = file_path.with_suffix(".json")
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=ensure_ascii, indent=indent)
            logger.info(f"✅ Data exported to: {file_path}")
            return str(file_path)
        except Exception as e:
            logger.error(f"❌ Error exporting JSON: {e}")
            return ""

    def export_csv(self, data: List[Dict[str, Any]], filename: str, delimiter: str = ',', encoding: str = 'utf-8') -> str:
        file_path = self.export_dir / filename
        if not file_path.suffix:
            file_path = file_path.with_suffix(".csv")
        try:
            if not data:
                logger.warning("⚠️ No data to export")
                return ""
            with open(file_path, 'w', encoding=encoding, newline='') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys(), delimiter=delimiter)
                writer.writeheader()
                writer.writerows(data)
            logger.info(f"✅ Data exported to: {file_path}")
            return str(file_path)
        except Exception as e:
            logger.error(f"❌ Error exporting CSV: {e}")
            return ""

    def export_excel(self, data: Union[List[Dict], Dict[str, List[Dict]]], filename: str, sheet_name: str = "Sheet1") -> str:
        file_path = self.export_dir / filename
        if not file_path.suffix:
            file_path = file_path.with_suffix(".xlsx")
        try:
            import pandas as pd
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                if isinstance(data, dict):
                    for sheet, records in data.items():
                        df = pd.DataFrame(records)
                        df.to_excel(writer, sheet_name=sheet, index=False)
                else:
                    df = pd.DataFrame(data)
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            logger.info(f"✅ Data exported to: {file_path}")
            return str(file_path)
        except ImportError:
            logger.error("❌ pandas or openpyxl not installed")
            return ""
        except Exception as e:
            logger.error(f"❌ Error exporting Excel: {e}")
            return ""

    def export_jsonl(self, data: List[Dict[str, Any]], filename: str) -> str:
        file_path = self.export_dir / filename
        if not file_path.suffix:
            file_path = file_path.with_suffix(".jsonl")
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for item in data:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
            logger.info(f"✅ Data exported to: {file_path}")
            return str(file_path)
        except Exception as e:
            logger.error(f"❌ Error exporting JSONL: {e}")
            return ""

    def export_zip(self, files: Dict[str, Union[str, bytes]], filename: str) -> str:
        file_path = self.export_dir / filename
        if not file_path.suffix:
            file_path = file_path.with_suffix(".zip")
        try:
            with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for name, content in files.items():
                    if isinstance(content, bytes):
                        zf.writestr(name, content)
                    else:
                        zf.writestr(name, str(content))
            logger.info(f"✅ ZIP exported to: {file_path}")
            return str(file_path)
        except Exception as e:
            logger.error(f"❌ Error exporting ZIP: {e}")
            return ""


_data_exporter = None


def get_data_exporter() -> DataExporter:
    global _data_exporter
    if _data_exporter is None:
        _data_exporter = DataExporter()
    return _data_exporter
