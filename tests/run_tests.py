#!/usr/bin/env python3
"""Тестовый запуск всех компонентов"""

import sys
import os

# Проверяем версию Python
if sys.version_info < (3, 8):
    print("❌ Требуется Python 3.8 или выше")
    sys.exit(1)

# Добавляем путь к папке проекта
sys.path.append(os.path.dirname(__file__))

from config.settings import load_config
from app.database import Database
from app.utils import check_requirements, create_directory_structure


def run_tests():
    """Запускает тесты всех компонентов"""

    print("=" * 50)
    print("ТЕСТИРОВАНИЕ КОМПОНЕНТОВ ПРОЕКТА")
    print("=" * 50)

    # 1. Проверка пакетов
    print("\n1. Проверка установленных пакетов...")
    if not check_requirements():
        return False
    print("✅ Все пакеты установлены")

    # 2. Создание директорий
    print("\n2. Создание структуры директорий...")
    create_directory_structure()
    print("✅ Директории созданы")

    # 3. Загрузка конфигурации
    print("\n3. Загрузка конфигурации...")
    try:
        config = load_config()
        print(f"✅ Конфигурация загружена:")
        print(f"   БД: {config['database']['name']}")
        print(f"   Пользователь: {config['database']['user']}")
    except Exception as e:
        print(f"❌ Ошибка загрузки конфигурации: {e}")
        return False

    # 4. Тестирование подключения к БД
    print("\n4. Тестирование подключения к PostgreSQL...")
    try:
        db = Database(config['database'])
        if db.test_connection():
            print("✅ Подключение к PostgreSQL успешно")
        else:
            print("❌ Не удалось подключиться к PostgreSQL")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

    # 5. Проверка файла ключа шифрования
    print("\n5. Проверка ключа шифрования...")
    key_file = config['encryption']['key_file']
    if os.path.exists(key_file):
        print(f"✅ Ключ шифрования найден: {key_file}")
    else:
        print(f"⚠️  Ключ шифрования не найден. Создайте файл {key_file}")
        print("   Команда: python -c \"from cryptography.fernet import Fernet; "
              "key = Fernet.generate_key(); open('secret.key', 'wb').write(key)\"")

    print("\n" + "=" * 50)
    print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    print("=" * 50)

    return True


if __name__ == "__main__":
    if run_tests():
        print("\n🎉 Проект готов к запуску!")
        print("Запустите: python main.py")
        sys.exit(0)
    else:
        print("\n❌ Тесты не пройдены. Исправьте ошибки.")
        sys.exit(1)