from typing import Any

# Список поддерживаемых типов данных
SUPPORTED_TYPES = {"int", "str", "bool"}


def create_table(
    metadata: dict[str, Any], table_name: str, columns: list[str]
) -> dict[str, Any] | None:
    """Создает новую таблицу в метаданных.

    Автоматически добавляет ID:int в начало списка столбцов,
    только если он не был явно задан пользователем.
    """
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return None

    # Сначала проверяем, задал ли пользователь ID самостоятельно (в любом регистре)
    user_has_id = any(col.lower().startswith("id:") for col in columns)

    # Если пользователь НЕ задал ID, генерируем его в начале
    parsed_columns: dict[str, str] = {}
    if not user_has_id:
        parsed_columns["ID"] = "int"

    # Парсим и валидируем остальные колонки пользователя
    for col in columns:
        if ":" not in col:
            print(f"Некорректное значение: {col}. Попробуйте снова.")
            return None

        col_name, col_type = col.split(":", 1)
        if col_type not in SUPPORTED_TYPES:
            print(f"Некорректное значение: {col}. Попробуйте снова.")
            return None

        # Сохраняем имя столбца в исходном регистре (например, ID или id)
        parsed_columns[col_name] = col_type

    # Сохраняем структуру таблицы в метаданные
    metadata[table_name] = {"columns": parsed_columns}
    
    # Формируем строку колонок для красивого вывода успеха
    col_strings = [f"{k}:{v}" for k, v in parsed_columns.items()]
    print(
        f'Таблица "{table_name}" успешно создана '
        f'со столбцами: {", ".join(col_strings)}'
    )
    return metadata


def drop_table(metadata: dict[str, Any], table_name: str) -> dict[str, Any] | None:
    """Удаляет информацию о таблице из метаданных."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return None

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata