import prompt


def welcome() -> None:
    """Отображает приветствие и запускает базовый интерактивный цикл команд."""
    print("Первая попытка запустить проект!\n")

    while True:
        print("***")
        print("<command> exit - выйти из программы")
        print("<command> help - справочная информация")

        command = prompt.string("Введите команду: ")
        print()

        if command == "exit":
            break
        elif command == "help":
            continue