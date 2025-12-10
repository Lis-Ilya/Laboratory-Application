from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QComboBox,
    QGroupBox, QFormLayout, QSpinBox, QDialogButtonBox
)
from PyQt5.QtCore import Qt, pyqtSignal
import re
import logging

logger = logging.getLogger(__name__)


class StudentForm(QDialog):
    """Форма для добавления/редактирования студента"""

    student_saved = pyqtSignal(dict)  # сигнал с данными студента

    def __init__(self, db, student_data=None, departments=None):
        super().__init__()
        self.db = db
        self.student_data = student_data or {}
        self.departments = departments or []
        self.is_edit_mode = bool(student_data)

        self.setup_ui()
        self.load_departments()

        if self.is_edit_mode:
            self.load_student_data()

    def setup_ui(self):
        """Настраивает интерфейс формы"""

        title = "Редактирование студента" if self.is_edit_mode else "Добавление студента"
        self.setWindowTitle(title)
        self.setFixedSize(500, 600)

        layout = QVBoxLayout()

        # Группа "Личные данные"
        personal_group = QGroupBox("Личные данные")
        personal_layout = QFormLayout()

        # Фамилия
        self.last_name_input = QLineEdit()
        self.last_name_input.setPlaceholderText("Иванов")
        personal_layout.addRow("Фамилия*:", self.last_name_input)

        # Инициалы
        self.initials_input = QLineEdit()
        self.initials_input.setPlaceholderText("И.И.")
        personal_layout.addRow("Инициалы*:", self.initials_input)

        # Год рождения
        self.birth_year_spin = QSpinBox()
        self.birth_year_spin.setRange(1900, 2100)
        self.birth_year_spin.setValue(2000)
        personal_layout.addRow("Год рождения*:", self.birth_year_spin)

        # Телефон
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("+7 (999) 123-45-67")
        personal_layout.addRow("Телефон*:", self.phone_input)

        # Номер зачетной книжки
        self.record_book_input = QLineEdit()
        self.record_book_input.setPlaceholderText("12345678")
        personal_layout.addRow("Номер зачетной книжки*:", self.record_book_input)

        personal_group.setLayout(personal_layout)
        layout.addWidget(personal_group)

        # Группа "Учебные данные"
        study_group = QGroupBox("Учебные данные")
        study_layout = QFormLayout()

        # Год поступления
        self.admission_year_spin = QSpinBox()
        self.admission_year_spin.setRange(2000, 2100)
        self.admission_year_spin.setValue(2020)
        study_layout.addRow("Год поступления*:", self.admission_year_spin)

        # Группа
        self.group_input = QLineEdit()
        self.group_input.setPlaceholderText("ИВТ-20-1")
        study_layout.addRow("Группа*:", self.group_input)

        # Кафедра
        self.department_combo = QComboBox()
        study_layout.addRow("Кафедра*:", self.department_combo)

        study_group.setLayout(study_layout)
        layout.addWidget(study_group)

        # Группа "Дополнительно"
        extra_group = QGroupBox("Дополнительно")
        extra_layout = QFormLayout()

        # Город проживания до поступления
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Москва")
        extra_layout.addRow("Город проживания до поступления*:", self.city_input)

        extra_group.setLayout(extra_layout)
        layout.addWidget(extra_group)

        # Кнопки
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.validate_and_save)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)

        self.setLayout(layout)

        # Валидация в реальном времени
        self.initials_input.textChanged.connect(self.validate_initials)
        self.phone_input.textChanged.connect(self.validate_phone)

    def load_departments(self):
        """Загружает список кафедр из базы данных"""
        try:
            if not self.departments:
                query = """
                    SELECT d.id, d.code, d.name, i.code as institute_code
                    FROM departments d
                    JOIN institutes i ON d.institute_id = i.id
                    ORDER BY i.code, d.code
                """
                result = self.db.execute_query(query)
                self.departments = result or []

            self.department_combo.clear()
            for dept in self.departments:
                display_text = f"{dept['institute_code']}/{dept['code']} - {dept['name']}"
                self.department_combo.addItem(display_text, dept['id'])

        except Exception as e:
            logger.error(f"Ошибка загрузки кафедр: {e}")

    def load_student_data(self):
        """Загружает данные студента для редактирования"""
        try:
            self.last_name_input.setText(self.student_data.get('last_name', ''))
            self.initials_input.setText(self.student_data.get('initials', ''))
            self.birth_year_spin.setValue(self.student_data.get('birth_year', 2000))
            # Телефон и номер зачётки зашифрованы - не показываем
            self.phone_input.setText("")
            self.record_book_input.setText("")
            self.admission_year_spin.setValue(self.student_data.get('admission_year', 2020))
            self.group_input.setText(self.student_data.get('group_name', ''))
            self.city_input.setText(self.student_data.get('city_before', ''))

            # Устанавливаем кафедру
            dept_id = self.student_data.get('department_id')
            if dept_id:
                for i in range(self.department_combo.count()):
                    if self.department_combo.itemData(i) == dept_id:
                        self.department_combo.setCurrentIndex(i)
                        break

        except Exception as e:
            logger.error(f"Ошибка загрузки данных студента: {e}")

    def validate_initials(self, text):
        """Валидирует инициалы"""
        pattern = r'^[А-ЯЁ]\.\s?[А-ЯЁ]\.$'
        if text and not re.match(pattern, text):
            self.initials_input.setStyleSheet("border: 1px solid red;")
        else:
            self.initials_input.setStyleSheet("")

    def validate_phone(self, text):
        """Валидирует номер телефона"""
        pattern = r'^(\+7|8)\s?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}$'
        if text and not re.match(pattern, text):
            self.phone_input.setStyleSheet("border: 1px solid red;")
        else:
            self.phone_input.setStyleSheet("")

    def validate_form(self):
        """Проверяет корректность заполнения формы"""
        errors = []

        # Проверка обязательных полей
        if not self.last_name_input.text().strip():
            errors.append("Фамилия обязательна для заполнения")

        if not self.initials_input.text().strip():
            errors.append("Инициалы обязательны для заполнения")
        elif not re.match(r'^[А-ЯЁ]\.\s?[А-ЯЁ]\.$', self.initials_input.text()):
            errors.append("Инициалы должны быть в формате 'И.О.'")

        if not self.phone_input.text().strip():
            errors.append("Телефон обязателен для заполнения")
        elif not re.match(r'^(\+7|8)\s?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}$',
                          self.phone_input.text()):
            errors.append("Некорректный формат телефона")

        if not self.record_book_input.text().strip():
            errors.append("Номер зачетной книжки обязателен")

        if not self.group_input.text().strip():
            errors.append("Группа обязательна для заполнения")

        if self.department_combo.currentIndex() == -1:
            errors.append("Выберите кафедру")

        if not self.city_input.text().strip():
            errors.append("Город обязателен для заполнения")

        # Проверка возраста
        birth_year = self.birth_year_spin.value()
        admission_year = self.admission_year_spin.value()
        if admission_year - birth_year < 16:
            errors.append("Студент не может быть младше 16 лет при поступлении")

        return errors

    def validate_and_save(self):
        """Проверяет форму и сохраняет данные"""
        errors = self.validate_form()

        if errors:
            QMessageBox.warning(self, "Ошибки в форме",
                                "Исправьте следующие ошибки:\n\n• " + "\n• ".join(errors))
            return

        # Подготовка данных
        student_data = {
            'last_name': self.last_name_input.text().strip(),
            'initials': self.initials_input.text().strip(),
            'birth_year': self.birth_year_spin.value(),
            'phone': self.phone_input.text().strip(),
            'record_book_number': self.record_book_input.text().strip(),
            'admission_year': self.admission_year_spin.value(),
            'group_name': self.group_input.text().strip(),
            'department_id': self.department_combo.currentData(),
            'city_before': self.city_input.text().strip(),
        }

        # Если это редактирование, добавляем ID
        if self.is_edit_mode and 'id' in self.student_data:
            student_data['id'] = self.student_data['id']

        self.student_saved.emit(student_data)
        self.accept()