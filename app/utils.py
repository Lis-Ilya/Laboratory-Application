import sys
import subprocess
from pathlib import Path
import re


def check_requirements():
    """Проверяет установленные пакеты"""

    requirements_file = Path('requirements.txt')
    if not requirements_file.exists():
        print("⚠️  Файл requirements.txt не найден")
        return True

    try:
        with open(requirements_file, 'r', encoding='utf-8') as f:
            required_packages = [
                line.strip() for line in f
                if line.strip() and not line.startswith('#')
            ]

        # Используем importlib.metadata вместо pkg_resources
        try:
            import importlib.metadata
        except ImportError:
            # Для Python < 3.8 используем importlib_metadata (backport)
            import importlib_metadata as importlib_metadata

        missing_packages = []

        for package_spec in required_packages:
            # Извлекаем имя пакета (без версии)
            if '==' in package_spec:
                pkg_name = package_spec.split('==')[0].strip()
            elif '>=' in package_spec:
                pkg_name = package_spec.split('>=')[0].strip()
            elif '<=' in package_spec:
                pkg_name = package_spec.split('<=')[0].strip()
            elif '>' in package_spec:
                pkg_name = package_spec.split('>')[0].strip()
            elif '<' in package_spec:
                pkg_name = package_spec.split('<')[0].strip()
            else:
                pkg_name = package_spec.strip()

            # Проверяем, установлен ли пакет
            try:
                importlib.metadata.version(pkg_name)
            except importlib.metadata.PackageNotFoundError:
                missing_packages.append(package_spec)

        if missing_packages:
            print("❌ Отсутствующие пакеты:")
            for pkg in missing_packages:
                print(f"  - {pkg}")
            print("\nУстановите командой: pip install -r requirements.txt")
            return False

        print("✅ Все пакеты установлены")
        return True

    except Exception as e:
        print(f"⚠️  Ошибка проверки пакетов: {e}")
        return True


def create_directory_structure():
    """Создает необходимые директории"""

    directories = [
        'exports',
        'logs',
        'templates',
        'backups',
    ]

    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 Создана директория: {directory}")


def validate_phone(phone):
    """Валидирует номер телефона"""
    import re

    # Российские номера: +7 XXX XXX-XX-XX, 8 XXX XXX-XX-XX
    pattern = r'^(\+7|8)\s?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}$'

    if re.match(pattern, phone):
        # Нормализуем номер
        normalized = re.sub(r'[^\d]', '', phone)
        if normalized.startswith('8'):
            normalized = '7' + normalized[1:]
        elif normalized.startswith('+7'):
            normalized = '7' + normalized[2:]
        return normalized
    return None


def validate_initials(initials):
    """Валидирует инициалы в формате 'И.О.'"""
    import re

    pattern = r'^[А-ЯЁ]\.\s?[А-ЯЁ]\.$'
    return bool(re.match(pattern, initials))