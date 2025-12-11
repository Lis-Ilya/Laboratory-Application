#!/usr/bin/env python3
"""Генерация ключа шифрования для приложения"""

import os
from cryptography.fernet import Fernet


def generate_encryption_key():
    """Генерирует и сохраняет ключ шифрования"""

    key_file = '../secret.key'

    if os.path.exists(key_file):
        print(f"⚠️  Файл {key_file} уже существует")
        response = input("Перезаписать? (y/n): ")
        if response.lower() != 'y':
            print("Отменено")
            return

    # Генерируем новый ключ
    key = Fernet.generate_key()

    # Сохраняем в файл
    with open(key_file, 'wb') as f:
        f.write(key)

    print(f"✅ Ключ шифрования сохранён в {key_file}")
    print(f"🔑 Ключ: {key.decode()}")
    print("\n⚠️  Сохраните этот ключ в безопасном месте!")
    print("   Без него невозможно будет расшифровать данные.")


if __name__ == "__main__":
    generate_encryption_key()