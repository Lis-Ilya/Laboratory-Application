#!/usr/bin/env python3
"""Простой тест настройки проекта"""

import os
import sys


def test_project_structure():
    """Проверяет структуру проекта"""

    print("🔍 Проверка структуры проекта...")

    required_dirs = ['app', 'config', 'gui', 'templates', 'tests']
    required_files = [
        '.env.example',
        'requirements.txt',
        'main.py',
        'app/__init__.py',
        'config/__init__.py',
        'gui/__init__.py',
        'tests/__init__.py'
    ]

    all_ok = True

    for directory in required_dirs:
        if os.path.exists(directory) and os.path.isdir(directory):
            print(f"  ✅ Папка '{directory}' существует")
        else:
            print(f"  ❌ Папка '{directory}' отсутствует")
            all_ok = False

    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ Файл '{file}' существует")
        else:
            print(f"  ❌ Файл '{file}' отсутствует")
            all_ok = False

    return all_ok


def test_imports():
    """Проверяет возможность импорта модулей"""

    print("\n🔍 Проверка импортов...")

    try:
        import PyQt5
        print("  ✅ PyQt5 установлен")
    except ImportError:
        print("  ❌ PyQt5 не установлен")
        return False

    try:
        import psycopg2
        print("  ✅ psycopg2 установлен")
    except ImportError:
        print("  ❌ psycopg2 не установлен")
        return False

    try:
        from app import database
        print("  ✅ Модуль app.database доступен")
    except ImportError as e:
        print(f"  ❌ Ошибка импорта app.database: {e}")
        return False

    return True


def test_env_file():
    """Проверяет наличие .env файла"""

    print("\n🔍 Проверка конфигурации...")

    if os.path.exists('.env'):
        print("  ✅ Файл .env существует")
        return True
    else:
        print("  ⚠️  Файл .env отсутствует")
        print("     Скопируйте .env.example в .env и заполните настройки БД")
        return False


def main():
    print("=" * 50)
    print("ТЕСТ НАСТРОЙКИ ПРОЕКТА")
    print("=" * 50)

    # Проверяем структуру
    if not test_project_structure():
        print("\n❌ Структура проекта неполная")
        return 1

    # Проверяем импорты
    if not test_imports():
        print("\n❌ Ошибки импорта")
        return 1

    # Проверяем .env
    test_env_file()

    print("\n" + "=" * 50)
    print("✅ ПРОЕКТ НАСТРОЕН КОРРЕКТНО")
    print("=" * 50)
    print("\nСледующие шаги:")
    print("1. Скопируйте .env.example в .env")
    print("2. Заполните .env своими настройками PostgreSQL")
    print("3. Запустите: python main.py")

    return 0


if __name__ == "__main__":
    sys.exit(main())