import shlex

from primitive_db.core import create_table, drop_table
from primitive_db.utils import load_metadata, save_metadata

DB_META_FILE = "db_meta.json"


def print_help() -> None:
    """Выводит справочную информацию по командам режима работы с таблицами."""
    print("\n***Процесс работы с таблицей***")
    print("\nФункции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> .. - создать таблицу")  # noqa: E501
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run() -> None:
    """Главный интерактивный цикл программы (REPL)."""
    print_help()

    while True:
        try:
            user_input = input(">>>Введите команду: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nВыход из программы.")
            break

        if not user_input:
            continue

        try:
            args = shlex.split(user_input)
        except ValueError:
            print("Ошибка: Некорректный синтаксический ввод (проверьте кавычки).")
            continue

        command = args[0]

        if command == "exit":
            break

        elif command == "help":
            print_help()
            continue

        elif command == "list_tables":
            metadata = load_metadata(DB_META_FILE)
            if not metadata:
                print("База данных пуста (нет созданных таблиц).")
            for table in metadata:
                print(f"- {table}")
            print()

        elif command == "create_table":
            if len(args) < 2:
                print("Ошибка: Не указано имя таблицы.")
                continue
            
            table_name = args[1]
            columns = args[2:]
            
            metadata = load_metadata(DB_META_FILE)
            updated_meta = create_table(metadata, table_name, columns)
            if updated_meta is not None:
                save_metadata(DB_META_FILE, updated_meta)
            print()

        elif command == "drop_table":
            if len(args) < 2:
                print("Ошибка: Не указано имя таблицы.")
                continue
            
            table_name = args[1]
            metadata = load_metadata(DB_META_FILE)
            updated_meta = drop_table(metadata, table_name)
            if updated_meta is not None:
                save_metadata(DB_META_FILE, updated_meta)
            print()

        else:
            print(f"Функции <{command}> нет. Попробуйте снова.")
            print()