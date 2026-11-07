import json
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