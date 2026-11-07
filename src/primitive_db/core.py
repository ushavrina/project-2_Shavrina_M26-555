from typing import Any

# Список поддерживаемых типов данных
SUPPORTED_TYPES = {"int", "str", "bool"}


def create_table(
    metadata: dict[str, Any], table_name: str, columns: list[str]
) -> dict[str, Any] | None:
    """Создает новую таблицу в метаданных.

    Автоматически добавляет ID:int в начало списка столбцов.
    Проверяет дубликаты таблиц и корректность типов данных.
    """
    # 1. Проверка на дубликат таблицы
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return None

    # 2. Инициализация структуры и автоматическое добавление ID
    parsed_columns: dict[str, str] = {"ID": "int"}

    # 3. Парсинг и валидация колонок пользователя
    for col in columns:
        if ":" not in col:
            print(f"Некорректное значение: {col}. Попробуйте снова.")
            return None

        col_name, col_type = col.split(":", 1)
        
        if col_type not in SUPPORTED_TYPES:
            print(f"Некорректное значение: {col}. Попробуйте снова.")
            return None

        parsed_columns[col_name] = col_type

    # 4. Сохранение в общий словарь метаданных
    metadata[table_name] = {"columns": parsed_columns}
    
    # 5. Вывод об успешном завершении
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