import json
import os
from typing import Any


def load_metadata(filepath: str) -> dict[str, Any]:
    """Загружает данные из JSON-файла.

    Если файл не найден, возвращает пустой словарь {}.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_metadata(filepath: str, data: dict[str, Any]) -> None:
    """Сохраняет переданные данные в JSON-файл."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_table_data(table_name: str) -> list[dict[str, Any]]:
    """Загружает записи таблицы из файла data/<table_name>.json.

    Если папка или файл не существуют, возвращает пустой список [].
    """
    filepath = os.path.join("data", f"{table_name}.json")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_table_data(table_name: str, data: list[dict[str, Any]]) -> None:
    """Сохраняет записи таблицы в файл data/<table_name>.json.

    Автоматически создает директорию data/, если она отсутствует.
    """
    os.makedirs("data", exist_ok=True)
    
    filepath = os.path.join("data", f"{table_name}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
