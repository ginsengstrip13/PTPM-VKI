"""ЛР3: три интеграционных теста и два теста с заглушками."""

import runpy
import sqlite3
import unittest
from unittest.mock import Mock, patch

from lab3 import (
    ConsoleUserInterface, Controller, Database, ExternalService,
    RegistrationValidator, UserInterface,
)


DATA = ("student_1", "Пароль1!", "Пароль1!")
SUCCESS = "Регистрация успешна."


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        # Настоящая SQLite в памяти: рабочий файл БД не меняется.
        self.database = Database(":memory:")
        self.addCleanup(self.database.close)
        self.validator = RegistrationValidator()
        self.ui = Mock(spec=UserInterface)
        self.ui.get_data.return_value = DATA
        self.sender = Mock(spec=ExternalService)
        self.controller = Controller(
            self.validator, self.database, self.ui, self.sender,
        )

    def test_new_registration_through_whole_program(self):
        # Интеграция всех реальных классов, включая запуск программы.
        # Подменяем ввод и вывод, а SQLite направляем в память.
        connection = sqlite3.connect(":memory:")
        with patch("sqlite3.connect", return_value=connection), \
                patch("builtins.input", side_effect=DATA), \
                patch("builtins.print") as output:
            runpy.run_module("lab3", run_name="__main__")
        output.assert_called_once_with(f"Имитация отправки на сервер: {SUCCESS}")
        # main() обязан закрыть соединение после выполнения.
        with self.assertRaises(sqlite3.ProgrammingError):
            connection.execute("SELECT 1")

    def test_existing_record_is_used_without_validation(self):
        # Контроллер, валидатор и БД настоящие; ввод и отправка — заглушки.
        self.assertEqual(self.controller.run(), SUCCESS)
        self.assertEqual(self.database.get(*DATA), (True, ""))
        # Любой повторный вызов валидатора уронит тест.
        with patch.object(self.validator, "validate", side_effect=AssertionError):
            self.assertEqual(self.controller.run(), SUCCESS)
        self.assertEqual(self.sender.send.call_count, 2)
        self.sender.send.assert_called_with(SUCCESS)
        count = self.database.connection.execute(
            "SELECT COUNT(*) FROM registrations"
        ).fetchone()[0]
        self.assertEqual(count, 1)

    def test_failed_registration_is_saved_and_deleted(self):
        # Проверяем передачу отказа через контроллер и БД, а не правила ЛР2.
        data = (DATA[0], DATA[1], "Другой1!")
        self.ui.get_data.return_value = data
        error = "Пароль и подтверждение пароля не совпадают."
        self.assertEqual(self.controller.run(), f"Ошибка: {error}")
        self.assertEqual(self.database.get(*data), (False, error))
        self.sender.send.assert_called_once_with(f"Ошибка: {error}")
        self.database.delete(*data)
        self.assertIsNone(self.database.get(*data))


class IsolationTests(unittest.TestCase):
    def test_console_input_with_stub(self):
        # Вместо ручного ввода input() по очереди получает три готовые строки.
        with patch("builtins.input", side_effect=DATA) as user_input:
            self.assertEqual(ConsoleUserInterface().get_data(), DATA)
        self.assertEqual(user_input.call_count, 3)

    def test_controller_with_stubs(self):

        validator = Mock(spec=RegistrationValidator)
        database = Mock(spec=Database)
        ui = Mock(spec=UserInterface)
        sender = Mock(spec=ExternalService)
        ui.get_data.return_value = DATA
        database.get.return_value = None
        validator.validate.return_value = (True, "")
        controller = Controller(validator, database, ui, sender)E
        self.assertEqual(controller.run(), SUCCESS)
        ui.get_data.assert_called_once_with()
        database.get.assert_called_once_with(*DATA)
        validator.validate.assert_called_once_with(*DATA)
        database.add.assert_called_once_with(*DATA, True, "")
        sender.send.assert_called_once_with(SUCCESS)

