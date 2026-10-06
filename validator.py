import hashlib
import logging
import  re
import string

blacklist = {
    'admin',
    'administrator',
    'root',
    'support',
    'test_user',
}

phone_pattern  = re.compile(r'^\+\d-\d{3}-\d{3}-\d{4}$')

email_pattern = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$"
)

username_pattern = re.compile(r"^[A-Za-z0-9_]+$")

cyrillic_pattern = re.compile(r"[А-Яа-яЁё]")

cyrillic_up_pattern =  re.compile(r"[А-ЯЁ]")

cyrillic_low_pattern = re.compile(r"[а-яё]")

special_characters = set(string.punctuation)

def mask_password(password: str) -> str:
    if not isinstance(password, str):
        return "<invalid-password>"
    digest = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return f"<sha256:{digest[:12]}>"


def _is_valid_login_format(login: str) -> bool:
    if phone_pattern.fullmatch(login):
        return True

    if email_pattern.fullmatch(login):
        return True

    return (
        len(login) >= 5 and username_pattern.fullmatch(login) is not None
    )

def _failure(login: object, message: str) -> tuple[bool, str]:
    logging.warning(
        "Регистрация отклонена: login=%r, result=False, error=%r",
        login,
        message,)
    return False, message

def validate_registration(
    login: str,
    password: str,
    password_confirmation: str,
) -> tuple[bool, str]:
    masked_password = mask_password(password)
    masked_confirmation = mask_password(password_confirmation)
    logging.info(
        "Получен запрос регистрации: login=%r, "
        "password=%s, password_confirmation=%s",
        login,
        masked_password,
        masked_confirmation,
    )
    try:
        if not isinstance(login, str):
            return _failure(
                login,
                "Логин должен быть строкой.",
            )

        if not isinstance(password, str):
            return _failure(
                login,
            "Пароль должен быть строкой.",
            )

        if not isinstance(password_confirmation, str):
            return _failure(
                login,
            "Подтверждение пароля должно быть строкой.",
            )

        if login == "":
            return _failure(
                login,
                "Логин не должен быть пустым.",
            )

        if password == "":
            return _failure(
                login,
                "Пароль не должен быть пустым.",
            )

        if login.lower() in blacklist:
            return _failure(
                login,
                "Этот логин запрещен.",
            )

        if not _is_valid_login_format(login):
            return _failure(
                login,
                "Некорректный логин: используйте телефон вида "
                "+x-xxx-xxx-xxxx, email или строку длиной не менее "
                "5 символов из латинских букв, цифр и '_'.",
            )

        if len(password) < 7:
            return _failure(
                login,
                "Пароль должен содержать не менее 7 символов.",
            )

        if re.search(r"[A-Za-z]", password):
            return _failure(
                login,
                "Пароль не должен содержать латинские буквы.",
            )

        for character in password:
            is_cyrillic = (
                cyrillic_pattern.fullmatch(character) is not None
            )
            is_digit = character.isdigit()
            is_special = character in special_characters

            if not (is_cyrillic or is_digit or is_special):
                return _failure(
                    login,
                    "Пароль содержит запрещенные символы.",
                )

        if cyrillic_up_pattern.search(password) is None:
            return _failure(
                login,
                "Пароль должен содержать хотя бы одну "
                "заглавную кириллическую букву.",
            )

        if cyrillic_low_pattern.search(password) is None:
            return _failure(
                login,
                "Пароль должен содержать хотя бы одну "
                "строчную кириллическую букву.",
            )

        if re.search(r"\d", password) is None:
            return _failure(
                login,
                "Пароль должен содержать хотя бы одну цифру.",
            )
        if not any(
                character in special_characters
                for character in password
        ):
            return _failure(
                login,
                "Пароль должен содержать хотя бы один спецсимвол.",
            )

        if password != password_confirmation:
            return _failure(
                login,
                "Пароль и подтверждение пароля не совпадают.",
            )

        logging.info(
            "Регистрация успешно проверена: "
            "login=%r, result=True",
            login,
        )
        return True, ""

    except Exception:
        logging.exception(
            "Непредвиденный сбой проверки: login=%r, "
            "password=%s, password_confirmation=%s",
            login,
            masked_password,
            masked_confirmation,
        )
        return False, "Внутренняя ошибка программы."
