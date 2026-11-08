import shlex

from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    info,
    insert,
    select,
    update,
)
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

DB_META_FILE = "db_meta.json"


def print_help() -> None:
    """Выводит справочную информацию по командам."""
    print("\n***Работа с таблицей***")
    print("\nСоздание и удаление таблицы:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> .. - создать таблицу")  # noqa: E501
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("\nCRUD-операции:")
    print("<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...) - создать запись.")  # noqa: E501
    print("<command> select from <имя_таблицы> where <столбец> = <значение> - прочитать записи по условию.")  # noqa: E501
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print("<command> update <имя_таблицы> set <столбец1> = <новое_значение1> where <столбец_условия> = <значение_условия> - обновить запись.")  # noqa: E501
    print("<command> delete from <имя_таблицы> where <столбец> = <значение> - удалить запись.")  # noqa: E501
    print("\nОбщие команды:")
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация.\n")


def run() -> None:
    """Главный интерактивный цикл программы (REPL)."""
    print_help()

    while True:
        try:
            user_input = input(">>> Введите команду: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nВыход из программы.")
            break

        if not user_input:
            continue

        try:
            args = shlex.split(user_input)
        except ValueError:
            print("Ошибка: Некорректный синтаксический ввод (проверьте кавычки).\n")
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
                print("База данных пуста (нет созданных таблиц).\n")
            for table in metadata:
                print(f"- {table}")
            print()

        elif command == "create_table":
            if len(args) < 2:
                print("Ошибка: Не указано имя таблицы.\n")
                continue
            table_name = args[1]
            metadata = load_metadata(DB_META_FILE)
            updated_meta = create_table(metadata, table_name, args[2:])
            if updated_meta is not None:
                save_metadata(DB_META_FILE, updated_meta)
            print()

        elif command == "drop_table":
            if len(args) < 2:
                print("Ошибка: Не указано имя таблицы.\n")
                continue
            table_name = args[1]
            metadata = load_metadata(DB_META_FILE)
            updated_meta = drop_table(metadata, table_name)
            if updated_meta is not None:
                save_metadata(DB_META_FILE, updated_meta)
            print()

        elif command in ("insert", "select", "update", "delete", "info"):
            metadata = load_metadata(DB_META_FILE)

            # ПАРСИНГ ИМЕНИ ТАБЛИЦЫ
            if command == "insert":
                if len(args) < 3 or args[1].lower() != "into":
                    print("Ошибка: Некорректный синтаксис INSERT. Ожидается: insert into <таблица> values (...)\n")  # noqa: E501
                    continue
                table_name = args[2]
            elif command in ("select", "delete"):
                if len(args) < 3 or args[1].lower() != "from":
                    print(f"Ошибка: Некорректный синтаксис {command.upper()}. Ожидается: {command} from <таблица> ...\n")  # noqa: E501
                    continue
                table_name = args[2]
            else:
                if len(args) < 2:
                    print(f"Ошибка: Не указано имя таблицы для команды {command}.\n")
                    continue
                table_name = args[1]

            if table_name not in metadata:
                print(f"Ошибка: Таблица '{table_name}' не существует.")
                continue

            table_meta = metadata[table_name]
            table_data = load_table_data(table_name)

            # ВЫПОЛНЕНИЕ КОМАНД
            if command == "info":
                info(table_name, table_meta, table_data)
                print()

            elif command == "insert":
                if len(args) < 5 or args[3].lower() != "values":
                    print("Ошибка: Некорректный синтаксис INSERT. Ожидается ключевое слово values.")  # noqa: E501
                    continue
                values_args = args[4:]
                cleaned_values = []
                for val in values_args:
                    val = val.lstrip("(").rstrip("),")
                    if val:
                        cleaned_values.append(val)
                
                updated_data = insert(table_name, table_meta, cleaned_values, table_data)  # noqa: E501
                if updated_data is not None:
                    save_table_data(table_name, updated_data)
                print()

            elif command == "select":
                where_args = []
                if len(args) > 3:
                    if args[3].lower() == "where":
                        where_args = args[4:]
                    else:
                        print("Ошибка: Некорректный синтаксис SELECT. Ожидается ключевое слово WHERE.")  # noqa: E501
                        continue
                select(table_name, table_meta, where_args, table_data)
                print()

            elif command == "update":
                try:
                    set_idx = [x.lower() for x in args].index("set")
                except ValueError:
                    print("Ошибка: В команде UPDATE отсутствует обязательное ключевое слово SET.")  # noqa: E501
                    continue

                where_idx = None
                if "where" in [x.lower() for x in args]:
                    where_idx = [x.lower() for x in args].index("where")

                if where_idx is not None:
                    set_args = args[set_idx + 1:where_idx]
                    where_args = args[where_idx + 1:]
                else:
                    set_args = args[set_idx + 1:]
                    where_args = []

                updated_data = update(table_name, table_meta, set_args, where_args, table_data)  # noqa: E501
                if updated_data is not None:
                    save_table_data(table_name, updated_data)
                print()

            elif command == "delete":
                where_args = []
                if len(args) > 3:
                    if args[3].lower() == "where":
                        where_args = args[4:]
                    else:
                        print("Ошибка: Некорректный синтаксис DELETE. Ожидается ключевое слово WHERE.")  # noqa: E501
                        continue
                updated_data = delete(table_name, table_meta, where_args, table_data)
                if updated_data is not None:
                    save_table_data(table_name, updated_data)
                print()

        else:
            print(f"Функции <{command}> нет. Попробуйте снова.")