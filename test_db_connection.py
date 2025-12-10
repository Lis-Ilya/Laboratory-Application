
import sys
import os
sys.path.append(os.path.dirname(__file__))

from config.settings import load_config
from app.database import Database

def test_student_data():
    """Тестирует загрузку данных студентов"""

    print("🔍 Тестирование загрузки данных студентов...")

    config = load_config()
    db = Database(config['database'])

    try:
        db.connect()

        # Тест 1: Проверяем структуру таблицы
        print("\n1. Проверяем структуру таблицы students:")
        db.cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'students' 
            ORDER BY ordinal_position;
        """)

        columns = db.cursor.fetchall()
        for col in columns:
            print(f"  - {col['column_name']}: {col['data_type']}")

        # Тест 2: Получаем несколько студентов
        print("\n2. Тестируем загрузку студентов:")
        query = """
            SELECT 
                s.id,
                s.last_name,
                s.initials,
                s.birth_year,
                s.admission_year,
                s.group_name,
                s.city_before,
                d.code as department_code,
                d.name as department_name,
                i.code as institute_code,
                i.name as institute_name
            FROM students s
            JOIN departments d ON s.department_id = d.id
            JOIN institutes i ON d.institute_id = i.id
            ORDER BY s.last_name 
            LIMIT 5
        """

        db.cursor.execute(query)
        students = db.cursor.fetchall()

        print(f"Найдено студентов: {len(students)}")
        for student in students:
            print(f"\n  Студент #{student['id']}:")
            print(f"    Фамилия: {student['last_name']}")
            print(f"    Инициалы: {student['initials']}")
            print(f"    Год рождения: {student['birth_year']}")
            print(f"    Год поступления: {student['admission_year']}")
            print(f"    Группа: {student['group_name']}")
            print(f"    Кафедра: {student['department_name']}")
            print(f"    Институт: {student['institute_name']}")
            print(f"    Город: {student['city_before']}")

        # Тест 3: Проверяем задачи поиска из ТЗ
        print("\n3. Тестируем задачи поиска из ТЗ:")

        # Задача 1: По году поступления
        db.cursor.execute("SELECT COUNT(*) FROM students WHERE admission_year = 2020;")
        count = db.cursor.fetchone()['count']
        print(f"   Задача 1: Поступили в 2020 году - {count} студентов")

        # Задача 2: По кафедре
        db.cursor.execute("""
            SELECT COUNT(*) 
            FROM students s 
            JOIN departments d ON s.department_id = d.id 
            WHERE d.code = 'ВТ';
        """)
        count = db.cursor.fetchone()['count']
        print(f"   Задача 2: На кафедре 'ВТ' - {count} студентов")

        # Задача 3: По городу (не из Москвы)
        db.cursor.execute("SELECT COUNT(*) FROM students WHERE city_before != 'Москва';")
        count = db.cursor.fetchone()['count']
        print(f"   Задача 3: Не из Москвы - {count} студентов")

        db.disconnect()
        print("\n✅ Все тесты пройдены успешно!")
        return True

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if test_student_data():
        print("\n🎉 База данных настроена правильно!")
    else:
        print("\n❌ Есть проблемы с базой данных")