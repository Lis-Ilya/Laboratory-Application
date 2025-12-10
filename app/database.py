# app/database.py
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
import logging

logger = logging.getLogger(__name__)


class Database:
    """Класс для работы с базой данных PostgreSQL"""

    def __init__(self, config):
        self.config = config
        self.connection = None
        self.cursor = None

    def connect(self):
        """Устанавливает соединение с базой данных"""
        try:
            self.connection = psycopg2.connect(
                host=self.config['host'],
                port=self.config['port'],
                database=self.config['name'],
                user=self.config['user'],
                password=self.config['password'],
                cursor_factory=RealDictCursor  # Возвращает словари вместо кортежей
            )
            self.cursor = self.connection.cursor()
            logger.info(f"Подключение к БД {self.config['name']} успешно")
            return True
        except Exception as e:
            logger.error(f"Ошибка подключения к БД: {e}")
            return False

    def disconnect(self):
        """Закрывает соединение с базой данных"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("Соединение с БД закрыто")

    def test_connection(self):
        """Тестирует подключение к базе данных"""
        try:
            if not self.connect():
                return False

            self.cursor.execute("SELECT version();")
            version = self.cursor.fetchone()
            logger.info(f"PostgreSQL версия: {version['version']}")

            # Проверяем существование таблиц
            self.cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = self.cursor.fetchall()
            logger.info(f"Найдено таблиц: {len(tables)}")

            self.disconnect()
            return True

        except Exception as e:
            logger.error(f"Ошибка тестирования подключения: {e}")
            return False

    def execute_query(self, query, params=None, fetch=True):
        """Выполняет SQL запрос"""
        try:
            if not self.connection or self.connection.closed:
                self.connect()

            self.cursor.execute(query, params or ())

            if fetch and self.cursor.description:
                result = self.cursor.fetchall()
            else:
                result = None
                self.connection.commit()

            return result

        except Exception as e:
            logger.error(f"Ошибка выполнения запроса: {e}")
            if self.connection:
                self.connection.rollback()
            raise

    def get_students(self, limit=100):
        """Получает список студентов"""
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
            LIMIT %s
        """
        return self.execute_query(query, (limit,))

    def add_student(self, student_data):
        """Добавляет нового студента"""
        query = """
            INSERT INTO students 
            (last_name, initials, birth_year, phone_encrypted, 
             record_book_number_encrypted, admission_year, group_name,
             department_id, city_before, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        return self.execute_query(query, student_data, fetch=True)