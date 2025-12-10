import os
import logging
from pathlib import Path
from dotenv import load_dotenv


def load_config():
    """Загружает конфигурацию из .env файла"""

    # Определяем путь к .env файлу
    env_path = Path('.') / '.env'

    if not env_path.exists():
        # Создаём пример .env файла, если его нет
        example_path = Path('.') / '.env.example'
        if example_path.exists():
            import shutil
            shutil.copy(example_path, env_path)
            print("📄 Создан файл .env из примера. Заполните его!")
        else:
            print("⚠️  Файл .env не найден. Использую значения по умолчанию")

    # Загружаем переменные окружения
    load_dotenv()

    config = {
        'database': {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 5432)),
            'name': os.getenv('DB_NAME', 'student_db_2024'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', ''),
        },
        'encryption': {
            'key_file': os.getenv('ENCRYPTION_KEY_FILE', 'secret.key'),
        },
        'app': {
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            'export_dir': os.getenv('EXPORT_DIR', 'exports'),
        }
    }

    return config


def setup_logging():
    """Настраивает логирование"""

    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()

    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    return logging.getLogger(__name__)