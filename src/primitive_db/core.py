from typing import Any

from prettytable import PrettyTable

from primitive_db.constants import SUPPORTED_TYPES
from primitive_db.decorators import confirm_action, handle_db_errors, log_time
from primitive_db.parser import cast_value, parse_condition, parse_set_expression


@handle_db_errors
def create_table(
    metadata: dict[str, Any], table_name: str, columns: list[str]
) -> dict[str, Any] | None:
    """Создает новую таблицу в метаданных."""
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return None

    user_has_id = any(col.lower().startswith("id:") for col in columns)
    parsed_columns: dict[str, str] = {}
    if not user_has_id:
        parsed_columns["ID"] = "int"

    for col in columns:
        if ":" not in col:
            print(f"Некорректное значение: {col}. Попробуйте снова.")
            return None

        col_name, col_type = col.split(":", 1)
        if col_type not in SUPPORTED_TYPES:
            print(f"Некорректное значение: {col}. Попробуйте снова.")
            return None
        parsed_columns[col_name] = col_type

    metadata[table_name] = {"columns": parsed_columns}
    col_strings = [f"{k}:{v}" for k, v in parsed_columns.items()]
    print(f'Таблица "{table_name}" успешно создана со столбцами: {", ".join(col_strings)}')  # noqa: E501
    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata: dict[str, Any], table_name: str) -> dict[str, Any] | None:
    """Удаляет информацию о таблице из метаданных."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return None
    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


@handle_db_errors
@log_time
def insert(
    table_name: str, table_meta: dict[str, Any], columns_args: list[str], table_data: list[dict[str, Any]]  # noqa: E501
) -> list[dict[str, Any]] | None:
    """Добавляет новую запись в таблицу после полной предварительной валидации."""
    columns_dict = table_meta["columns"]
    user_columns = [col for col in columns_dict.keys() if col != "ID"]

    if len(columns_args) != len(user_columns):
        print(f"Ошибка: Неверное количество значений. Ожидается: {len(user_columns)}, передано: {len(columns_args)}")  # noqa: E501
        return None

    validated_fields: dict[str, Any] = {}
    for col_name, val_str in zip(user_columns, columns_args):
        target_type = columns_dict[col_name]
        validated_fields[col_name] = cast_value(val_str, target_type)

    new_id = max([row["ID"] for row in table_data], default=0) + 1
    new_row: dict[str, Any] = {"ID": new_id}
    new_row.update(validated_fields)
    table_data.append(new_row)
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return table_data


@handle_db_errors
@log_time
def select(
    table_name: str, table_meta: dict[str, Any], where_args: list[str], table_data: list[dict[str, Any]]  # noqa: E501
) -> None:
    """Выводит данные таблицы в виде ASCII-таблицы."""
    columns_dict = table_meta["columns"]
    filtered_data = table_data

    if where_args:
        cond = parse_condition(where_args)
        if not cond:
            return
        
        col_name = cond["column"]
        val_str = cond["value"]

        if col_name not in columns_dict:
            print(f"Ошибка: Столбец '{col_name}' не существует в таблице '{table_name}'.")  # noqa: E501
            return

        target_val = cast_value(val_str, columns_dict[col_name])
        filtered_data = [row for row in table_data if row.get(col_name) == target_val]

    if not filtered_data:
        print("Таблица пуста или нет записей, соответствующих условию.")
        return

    table = PrettyTable()
    table.field_names = list(columns_dict.keys())
    for row in filtered_data:
        table.add_row([row.get(col) for col in columns_dict.keys()])
    print(table)


@handle_db_errors
def update(
    table_name: str, table_meta: dict[str, Any], set_args: list[str], where_args: list[str], table_data: list[dict[str, Any]]  # noqa: E501
) -> list[dict[str, Any]] | None:
    """Обновляет значения в таблице по условию WHERE."""
    columns_dict = table_meta["columns"]
    
    set_expr = parse_set_expression(set_args)
    if not set_expr:
        return None
        
    set_col = set_expr["column"]
    set_val_str = set_expr["value"]

    if set_col not in columns_dict:
        print(f"Ошибка: Столбец '{set_col}' не существует.")
        return None
    if set_col == "ID":
        print("Ошибка: Изменение столбца ID запрещено.")
        return None

    new_value = cast_value(set_val_str, columns_dict[set_col])

    filter_col = None
    filter_val = None
    if where_args:
        cond = parse_condition(where_args)
        if not cond:
            return None
        filter_col = cond["column"]
        if filter_col not in columns_dict:
            print(f"Ошибка: Столбец '{filter_col}' не существует.")
            return None
        filter_val = cast_value(cond["value"], columns_dict[filter_col])

    updated_count = 0
    for row in table_data:
        if filter_col is None or row.get(filter_col) == filter_val:
            row[set_col] = new_value
            updated_count += 1
            print(f'Запись с ID={row["ID"]} в таблице "{table_name}" успешно обновлена.')  # noqa: E501

    if updated_count == 0:
        print("Записей для обновления не найдено.")
    return table_data


@handle_db_errors
@confirm_action("удаление записей")
def delete(
    table_name: str, table_meta: dict[str, Any], where_args: list[str], table_data: list[dict[str, Any]]  # noqa: E501
) -> list[dict[str, Any]] | None:
    """Удаляет записи из таблицы по условию WHERE."""
    columns_dict = table_meta["columns"]

    if not where_args:
        for row in table_data:
            print(f'Запись с ID={row["ID"]} успешно удалена из таблицы "{table_name}".')
        return []

    cond = parse_condition(where_args)
    if not cond:
        return None

    filter_col = cond["column"]
    if filter_col not in columns_dict:
        print(f"Ошибка: Столбец '{filter_col}' не существует.")
        return None

    filter_val = cast_value(cond["value"], columns_dict[filter_col])
    to_delete = [row for row in table_data if row.get(filter_col) == filter_val]
    for row in to_delete:
        print(f'Запись с ID={row["ID"]} успешно удалена из таблицы "{table_name}".')

    new_table_data = [row for row in table_data if row.get(filter_col) != filter_val]
    return new_table_data


@handle_db_errors
def info(table_name: str, table_meta: dict[str, Any], table_data: list[dict[str, Any]]) -> None:  # noqa: E501
    """Выводит подробную информацию о таблице."""
    print(f"Таблица: {table_name}")
    columns_dict = table_meta["columns"]
    col_strings = [f"{col_name}:{col_type}" for col_name, col_type in columns_dict.items()]  # noqa: E501
    print(f"Столбцы: {', '.join(col_strings)}")
    print(f"Количество записей: {len(table_data)}")