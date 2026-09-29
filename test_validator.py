import unittest

from validator import mask_password, validate_registration


class RegistrationValidatorTests(unittest.TestCase):
    def test_valid_username(self):
        self.assertEqual(
            validate_registration(
                "student_1",
                "Пароль1!",
                "Пароль1!",
            ),
            (True, ""),
        )

    def test_valid_phone(self):
        result, message = validate_registration(
            "+7-923-123-4567",
            "Секрет2#",
            "Секрет2#",
        )
        self.assertTrue(result)
        self.assertEqual(message, "")

    def test_valid_email(self):
        result, _ = validate_registration(
            "student@example.com",
            "Защита3$",
            "Защита3$",
        )
        self.assertTrue(result)

    def test_empty_login(self):
        result, message = validate_registration(
            "",
            "Пароль1!",
            "Пароль1!",
        )
        self.assertFalse(result)
        self.assertIn("пустым", message)

    def test_blacklisted_login(self):
        result, message = validate_registration(
            "admin",
            "Пароль1!",
            "Пароль1!",
        )
        self.assertFalse(result)
        self.assertIn("запрещен", message)

    def test_short_username(self):
        result, message = validate_registration(
            "user",
            "Пароль1!",
            "Пароль1!",
        )
        self.assertFalse(result)
        self.assertIn("Некорректный логин", message)

    def test_invalid_username_character(self):
        result, message = validate_registration(
            "user-name",
            "Пароль1!",
            "Пароль1!",
        )
        self.assertFalse(result)
        self.assertIn("Некорректный логин", message)

    def test_short_password(self):
        result, message = validate_registration(
            "student",
            "Па1!",
            "Па1!",
        )
        self.assertFalse(result)
        self.assertIn("7 символов", message)

    def test_latin_letter_in_password(self):
        result, message = validate_registration(
            "student",
            "ПарольA1!",
            "ПарольA1!",
        )
        self.assertFalse(result)
        self.assertIn("латинские", message)

    def test_missing_uppercase(self):
        result, message = validate_registration(
            "student",
            "пароль1!",
            "пароль1!",
        )
        self.assertFalse(result)
        self.assertIn("заглавную", message)

    def test_missing_lowercase(self):
        result, message = validate_registration(
            "student",
            "ПАРОЛЬ1!",
            "ПАРОЛЬ1!",
        )
        self.assertFalse(result)
        self.assertIn("строчную", message)

    def test_missing_digit(self):
        result, message = validate_registration(
            "student",
            "Пароль!",
            "Пароль!",
        )
        self.assertFalse(result)
        self.assertIn("цифру", message)

    def test_missing_special_character(self):
        result, message = validate_registration(
            "student",
            "Пароль123",
            "Пароль123",
        )
        self.assertFalse(result)
        self.assertIn("спецсимвол", message)

    def test_passwords_do_not_match(self):
        result, message = validate_registration(
            "student",
            "Пароль1!",
            "Пароль2!",
        )
        self.assertFalse(result)
        self.assertIn("не совпадают", message)

    def test_password_masks_are_deterministic(self):
        self.assertEqual(
            mask_password("Пароль1!"),
            mask_password("Пароль1!"),
        )
        self.assertNotEqual(
            mask_password("Пароль1!"),
            mask_password("Пароль2!"),
        )


if __name__ == "__main__":
    unittest.main()