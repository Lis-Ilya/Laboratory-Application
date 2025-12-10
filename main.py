#!/usr/bin/env python3
"""
Главный файл приложения "База данных студентов"
Версия 1.0
"""

import sys
import os

# ========== ИСПРАВЛЕНИЕ ОШИБКИ QT ==========
if sys.platform == 'win32':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    possible_plugin_paths = [
        os.path.join(base_dir, '.venv', 'Lib', 'site-packages', 'PyQt5', 'Qt5', 'plugins'),
        os.path.join(base_dir, '.venv', 'Lib', 'site-packages', 'PyQt5', 'Qt', 'plugins'),
        os.path.join(sys.prefix, 'Lib', 'site-packages', 'PyQt5', 'Qt5', 'plugins'),
        os.path.join(sys.prefix, 'Lib', 'site-packages', 'PyQt5', 'Qt', 'plugins'),
    ]

    for plugin_path in possible_plugin_paths:
        if os.path.exists(plugin_path):
            os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path
            print(f"✅ Найден путь к плагинам Qt: {plugin_path}")
            break
# ========== КОНЕЦ ИСПРАВЛЕНИЯ ==========

import logging
from PyQt5.QtWidgets import QApplication, QMessageBox, QDialog
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QCoreApplication

# Добавляем путь к папке app в sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from config.settings import load_config, setup_logging
from gui.main_window import MainWindow
from gui.login_dialog import LoginDialog
from app.database import Database
from app.utils import check_requirements, create_directory_structure


def initialize_database():
    """Инициализирует базу данных тестовыми данными"""

    # Создаём тестового пользователя, если его нет
    query = """
        INSERT INTO users (login, password_hash, full_name, is_active)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (login) DO NOTHING
    """

    # В реальном приложении пароль должен быть хэширован!
    # Для демо используем простой пароль
    test_user = ('admin', 'admin123', 'Администратор', True)

    return test_user


def main():
    """Основная функция запуска приложения"""

    # Настройка приложения
    QCoreApplication.setOrganizationName("University")
    QCoreApplication.setApplicationName("Student Database System")
    QCoreApplication.setApplicationVersion("1.0.0")

    # Загрузка конфигурации
    config = load_config()

    # Настройка логирования
    logger = setup_logging()

    # Проверка зависимостей
    if not check_requirements():
        print("❌ Требуемые пакеты не установлены. Установите из requirements.txt")
        return 1

    # Создание директорий
    create_directory_structure()

    # Создание приложения
    app = QApplication(sys.argv)

    # Настройка шрифтов
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Проверка подключения к БД
    try:
        db = Database(config['database'])
        if not db.test_connection():
            QMessageBox.critical(None, "Ошибка",
                                 "Не удалось подключиться к базе данных.\n"
                                 "Проверьте настройки в файле .env")
            return 1
    except Exception as e:
        QMessageBox.critical(None, "Ошибка",
                             f"Ошибка подключения к БД: {e}\n"
                             "Убедитесь, что PostgreSQL запущен.")
        return 1

    # Показываем окно входа
    login_dialog = LoginDialog(db)

    if login_dialog.exec_() == QDialog.Accepted:
        # Инициализируем базу данных тестовыми данными
        initialize_database()

        # Создание и отображение главного окна
        window = MainWindow(config, db)
        window.show()

        logger.info("Приложение запущено успешно")

        # Запуск основного цикла
        return app.exec_()
    else:
        # Пользователь отменил вход
        print("Вход отменен")
        return 0


if __name__ == "__main__":
    sys.exit(main())