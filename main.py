import logging
import sys
from pathlib import Path
from validator import validate_registration

def main() -> None:
    log_directory = Path(__file__).resolve().parent / "logs"

    print(log_directory)
    log_directory.mkdir(exist_ok=True)

    log_format = (
        "%(asctime)s | [%(levelname)-7s] | %(message)s"
    )
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=logging.DEBUG,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_directory / "log.txt", encoding="utf-8"),
        ],
        force=True,
    )
    logging.info('Логгер успешно сконфигурирован')

    logging.info("Приложение запущено")

    try:
        login = input("Введите логин: ")
        password = input("Введите пароль: ")
        confirmation = input("Повторите пароль: ")

        result, message = validate_registration(
            login,
            password,
            confirmation,
        )
        print(f"Результат: {result}")
        print(f"Сообщение: {message}")
    except Exception as e:
        logging.exception("Критическая ошибка приложения")
        print("Программа завершилась с ошибкой.")
    finally:
        logging.info("Приложение завершено")

if __name__ == "__main__":
    main()
