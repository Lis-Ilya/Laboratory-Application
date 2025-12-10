#!/usr/bin/env python3
"""
Главный файл приложения "База данных студентов"
Версия 1.0
"""

import sys
import os

# Добавляем путь к плагинам PyQt5 в переменные окружения
if sys.platform == 'win32':
    # Для Windows: находим путь к плагинам в виртуальном окружении
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Ищем плагины в нескольких возможных местах
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
    else:
        print("⚠️  Путь к плагинам Qt не найден")

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QCoreApplication

# Добавляем путь к папке app в sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from config.settings import load_config, setup_logging
from gui.main_window import MainWindow
from app.database import Database
from app.utils import check_requirements


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

    # Проверка подключения к БД
    try:
        db = Database(config['database'])
        if not db.test_connection():
            print("❌ Не удалось подключиться к базе данных")
            return 1
    except Exception as e:
        print(f"❌ Ошибка базы данных: {e}")
        return 1

    # Создание GUI приложения
    app = QApplication(sys.argv)

    # Настройка шрифтов (опционально)
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Создание и отображение главного окна
    window = MainWindow(config, db)
    window.show()

    logger.info("Приложение запущено успешно")

    # Запуск основного цикла
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())