from typing import Any


def parse_condition(args: list[str]) -> dict[str, str] | None:
    """Разбирает аргументы условия WHERE.

    Ожидает формат: ['имя_колонки', '=', 'значение']
    """
    if len(args) != 3 or args[1] != "=":
        print("Ошибка: Некорректный формат условия WHERE. Ожидается: <колонка> = <значение>")  # noqa: E501
        return None

    return {"column": args[0], "value": args[2]}


def parse_set_expression(args: list[str]) -> dict[str, str] | None:
    """Разбирает аргументы выражения SET для обновления данных.

    Ожидает формат: ['имя_колонки', '=', 'значение']
    """
    if len(args) != 3 or args[1] != "=":
        print("Ошибка: Некорректный формат выражения SET. Ожидается: <колонка> = <значение>")  # noqa: E501
        return None

    return {"column": args[0], "value": args[2]}


def cast_value(value_str: str, target_type: str) -> Any:
    """Приводит строковое значение к типу данных таблицы.

    Строки (str) валидируются, числа и булевы значения приводятся к системным типам.
    """
    is_quoted = (value_str.startswith('"') and value_str.endswith('"')) or \
                (value_str.startswith("'") and value_str.endswith("'"))

    if target_type == "str":
        if is_quoted:
            return value_str[1:-1]
        return value_str

    if is_quoted:
        raise ValueError(f"значение {value_str} не должно содержать кавычек для типа {target_type}")  # noqa: E501

    if target_type == "int":
        try:
            return int(value_str)
        except ValueError:
            raise ValueError(f"значение '{value_str}' не может быть приведено к типу int")  # noqa: E501

    elif target_type == "bool":
        lowered = value_str.lower()
        if lowered in ("true", "1"):
            return True
        elif lowered in ("false", "0"):
            return False
        else:
            raise ValueError(f"значение '{value_str}' не может быть приведено к типу bool")  # noqa: E501

    return value_str