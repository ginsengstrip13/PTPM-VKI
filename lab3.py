

from abc import ABC, abstractmethod
import sqlite3

from validator import validate_registration


class RegistrationValidator:
    # Метод использует готовую проверку из ЛР1. Правила не дублируем.
    def validate(self, login, password, confirmation):
        return validate_registration(login, password, confirmation)


class Database:
    def __init__(self, path):
        self.connection = sqlite3.connect(path)
        # Ключ составной: другой пароль или подтверждение — другая запись.
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS registrations (
                login TEXT NOT NULL,
                password TEXT NOT NULL,
                confirmation TEXT NOT NULL,
                result INTEGER NOT NULL,
                error TEXT NOT NULL,
                PRIMARY KEY (login, password, confirmation)
            )
        """)
        self.connection.commit()

    def add(self, login, password, confirmation, result, error):
        # Знаки ? передают значения отдельно от SQL-запроса.
        with self.connection:
            self.connection.execute(
                "INSERT INTO registrations VALUES (?, ?, ?, ?, ?)",
                (login, password, confirmation, result, error),
            )

    def get(self, login, password, confirmation):
        row = self.connection.execute(
            "SELECT result, error FROM registrations "
            "WHERE login = ? AND password = ? AND confirmation = ?",
            (login, password, confirmation),
        ).fetchone()
        # None означает отсутствие записи, а (False, ошибка) — сохранённый отказ.
        if row is None:
            return None
        return bool(row[0]), row[1]

    def delete(self, login, password, confirmation):
        with self.connection:
            self.connection.execute(
                "DELETE FROM registrations "
                "WHERE login = ? AND password = ? AND confirmation = ?",
                (login, password, confirmation),
            )

    def close(self):
        self.connection.close()


class UserInterface(ABC):
    # ABC задаёт обязательный метод. Сам интерфейс создавать нельзя.
    @abstractmethod
    def get_data(self):
        """Вернуть логин, пароль и подтверждение."""


class ConsoleUserInterface(UserInterface):
    def get_data(self):
        return (
            input("Введите логин: "),
            input("Введите пароль: "),
            input("Повторите пароль: "),
        )


class ExternalService(ABC):
    @abstractmethod
    def send(self, message):
        """Передать строку с результатом."""


class FakeExternalService(ExternalService):
    def send(self, message):
        # Только имитация: никаких подключений к настоящему серверу.
        print(f"Имитация отправки на сервер: {message}")


class Controller:
    def __init__(self, validator, database, user_interface, external_service):
        # Получаем зависимости снаружи, чтобы в тестах их легко подменить.
        self.validator = validator
        self.database = database
        self.user_interface = user_interface
        self.external_service = external_service

    def run(self):
        data = self.user_interface.get_data()
        result = self.database.get(*data)
        if result is None:
            result = self.validator.validate(*data)
            self.database.add(*data, *result)

        success, error = result
        message = "Регистрация успешна." if success else f"Ошибка: {error}"
        self.external_service.send(message)
        return message


def main():
    database = Database("registration.db")
    try:
        controller = Controller(
            RegistrationValidator(), database,
            ConsoleUserInterface(), FakeExternalService(),
        )
        return controller.run()
    finally:
        # Соединение закрывается даже при ошибке ввода или отправки.
        database.close()


if __name__ == "__main__":
    main()
