"""
Модуль шифрования данных для приложения
Использует симметричное шифрование (Fernet) из библиотеки cryptography
"""

import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)


class DataEncryptor:
    """Класс для шифрования и дешифрования данных"""

    def __init__(self, key=None, password=None, salt=None):
        """
        Инициализация шифратора

        Args:
            key: готовый ключ Fernet (если None, будет сгенерирован)
            password: пароль для генерации ключа (если нет готового ключа)
            salt: соль для генерации ключа
        """
        if key:
            self.key = key
        elif password:
            self.key = self.generate_key_from_password(password, salt)
        else:
            self.key = Fernet.generate_key()

        self.cipher = Fernet(self.key)

    @staticmethod
    def generate_key_from_password(password, salt=None):
        """
        Генерирует ключ из пароля

        Args:
            password: строка с паролем
            salt: соль (если None, будет сгенерирована)

        Returns:
            bytes: ключ Fernet
        """
        if salt is None:
            salt = os.urandom(16)

        # Используем PBKDF2 для генерации ключа из пароля
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )

        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    @staticmethod
    def load_or_create_key(key_file='secret.key', password=None):
        """
        Загружает ключ из файла или создаёт новый

        Args:
            key_file: путь к файлу с ключом
            password: пароль для генерации ключа (опционально)

        Returns:
            tuple: (ключ, был_ли_создан_новый)
        """
        if os.path.exists(key_file):
            try:
                with open(key_file, 'rb') as f:
                    key = f.read()
                logger.info(f"Ключ загружен из {key_file}")
                return key, False
            except Exception as e:
                logger.error(f"Ошибка загрузки ключа: {e}")

        # Создаём новый ключ
        if password:
            encryptor = DataEncryptor(password=password)
        else:
            encryptor = DataEncryptor()

        encryptor.save_key(key_file)
        logger.info(f"Создан новый ключ в {key_file}")
        return encryptor.key, True

    def encrypt(self, data):
        """
        Шифрует строку данных

        Args:
            data: строка для шифрования

        Returns:
            str: зашифрованная строка в base64
        """
        if data is None:
            return None

        try:
            encrypted = self.cipher.encrypt(data.encode('utf-8'))
            return base64.b64encode(encrypted).decode('utf-8')
        except Exception as e:
            logger.error(f"Ошибка шифрования: {e}")
            return None

    def decrypt(self, encrypted_data):
        """
        Дешифрует строку данных

        Args:
            encrypted_data: зашифрованная строка в base64

        Returns:
            str: расшифрованная строка или None при ошибке
        """
        if not encrypted_data:
            return None

        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted = self.cipher.decrypt(encrypted_bytes)
            return decrypted.decode('utf-8')
        except Exception as e:
            logger.error(f"Ошибка дешифрования: {e}")
            return None

    def encrypt_fields(self, data_dict, fields_to_encrypt):
        """
        Шифрует указанные поля в словаре

        Args:
            data_dict: словарь с данными
            fields_to_encrypt: список полей для шифрования

        Returns:
            dict: словарь с зашифрованными полями
        """
        result = data_dict.copy()

        for field in fields_to_encrypt:
            if field in result and result[field]:
                encrypted = self.encrypt(result[field])
                if encrypted:
                    result[f"{field}_encrypted"] = encrypted
                # Удаляем оригинальное поле после шифрования
                result.pop(field, None)

        return result

    def decrypt_fields(self, data_dict, encrypted_fields):
        """
        Дешифрует указанные поля в словаре

        Args:
            data_dict: словарь с зашифрованными данными
            encrypted_fields: список зашифрованных полей

        Returns:
            dict: словарь с расшифрованными полями
        """
        result = data_dict.copy()

        for field in encrypted_fields:
            encrypted_field = f"{field}_encrypted"
            if encrypted_field in result and result[encrypted_field]:
                decrypted = self.decrypt(result[encrypted_field])
                if decrypted:
                    result[field] = decrypted

        return result

    def save_key(self, filename='secret.key'):
        """
        Сохраняет ключ в файл

        Args:
            filename: путь к файлу
        """
        try:
            with open(filename, 'wb') as f:
                f.write(self.key)
            logger.info(f"Ключ сохранён в {filename}")
        except Exception as e:
            logger.error(f"Ошибка сохранения ключа: {e}")

    def get_key(self):
        """
        Возвращает текущий ключ

        Returns:
            bytes: ключ шифрования
        """
        return self.key


# Создаём глобальный экземпляр шифратора
_encryptor = None


def get_encryptor(key_file='secret.key'):
    """
    Возвращает глобальный экземпляр шифратора

    Args:
        key_file: путь к файлу с ключом

    Returns:
        DataEncryptor: экземпляр шифратора
    """
    global _encryptor

    if _encryptor is None:
        key, _ = DataEncryptor.load_or_create_key(key_file)
        _encryptor = DataEncryptor(key=key)

    return _encryptor


# Функции для удобства использования
def encrypt_data(data):
    """Шифрует строку данных"""
    encryptor = get_encryptor()
    return encryptor.encrypt(data)


def decrypt_data(encrypted_data):
    """Дешифрует строку данных"""
    encryptor = get_encryptor()
    return encryptor.decrypt(encrypted_data)