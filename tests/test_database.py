# tests/test_database.py
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import Database
from config.settings import load_config


def test_database_connection():
    """Тестирует подключение к базе данных"""

    print("🔍 Тестирование подключения к PostgreSQL...")

    try:
        # Загружаем конфигурацию
        config = load_config()
        print(f"✅ Конфигурация загружена:")
        print(f"   Хост: {config['database']['host']}")
        print(f"   База: {config['database']['name']}")
        print(f"   Пользователь: {config['database']['user']}")

        # Создаем объект БД
        db = Database(config['database'])

        # Тестируем подключение
        if db.test_connection():
            print("✅ Подключение к PostgreSQL успешно!")

            # Получаем список студентов
            students = db.get_students(limit=5)
            print(f"✅ Получено студентов: {len(students)}")

            if students:
                print("\nПример данных:")
                for student in students[:3]:
                    print(f"  - {student['last_name']} {student.get('initials', '')}")

            return True
        else:
            print("❌ Не удалось подключиться к PostgreSQL")
            return False

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


if __name__ == "__main__":
    success = test_database_connection()
    sys.exit(0 if success else 1)