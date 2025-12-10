from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QMenuBar, QMenu, QStatusBar,
    QLabel, QSplitter, QHeaderView, QTabWidget
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon
import logging

from gui.student_form import StudentForm
from app.encryption import get_encryptor

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Главное окно приложения"""

    def __init__(self, config, db):
        super().__init__()
        self.config = config
        self.db = db

        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_statusbar()

        # Загружаем данные
        QTimer.singleShot(100, self.load_data)

    def setup_ui(self):
        """Настраивает интерфейс"""

        # Основные параметры окна
        self.setWindowTitle("База данных студентов")
        self.setGeometry(100, 100, 1200, 700)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Основной layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Панель управления
        control_panel = self.create_control_panel()
        main_layout.addLayout(control_panel)

        # Таблица студентов
        self.table = self.create_students_table()
        main_layout.addWidget(self.table)

        # Статистика
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("color: gray; font-size: 12px;")
        main_layout.addWidget(self.stats_label)

    def create_control_panel(self):
        """Создает панель управления"""

        layout = QHBoxLayout()

        # Кнопки
        buttons = [
            ("➕ Добавить", self.add_student, "Добавить нового студента"),
            ("✏️ Редактировать", self.edit_student, "Редактировать выбранного студента"),
            ("🗑️ Удалить", self.delete_student, "Удалить выбранного студента"),
            ("🔍 Поиск", self.show_search_dialog, "Поиск студентов"),
            ("📤 Экспорт", self.export_data, "Экспорт данных"),
            ("🔄 Обновить", self.load_data, "Обновить данные"),
        ]

        for text, slot, tooltip in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(slot)
            btn.setToolTip(tooltip)
            layout.addWidget(btn)

        layout.addStretch()

        return layout

    def create_students_table(self):
        """Создает таблицу для отображения студентов"""

        table = QTableWidget()
        table.setColumnCount(10)

        # Изменяем заголовки - вместо "Имя" используем "Инициалы"
        headers = [
            "ID", "Фамилия", "Инициалы", "Год рождения",
            "Год поступления", "Группа", "Институт", "Кафедра",
            "Город", "Телефон"
        ]

        table.setHorizontalHeaderLabels(headers)

        # Настройка таблицы
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Автоматическое растяжение колонок
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Фамилия
        header.setSectionResizeMode(9, QHeaderView.Stretch)  # Телефон

        return table

    def setup_menu(self):
        """Настраивает меню"""

        menubar = self.menuBar()

        # Меню Файл
        file_menu = menubar.addMenu("Файл")
        file_menu.addAction("Экспорт в Word", self.export_to_word)
        file_menu.addAction("Экспорт в Excel", self.export_to_excel)
        file_menu.addSeparator()
        file_menu.addAction("Выход", self.close)

        # Меню Данные
        data_menu = menubar.addMenu("Данные")
        data_menu.addAction("Добавить студента", self.add_student)
        data_menu.addAction("Редактировать студента", self.edit_student)
        data_menu.addAction("Удалить студента", self.delete_student)
        data_menu.addSeparator()
        data_menu.addAction("Обновить данные", self.load_data)

        # Меню Поиск
        search_menu = menubar.addMenu("Поиск")
        search_menu.addAction("По году поступления", lambda: self.search_by_field('admission_year'))
        search_menu.addAction("По кафедре", lambda: self.search_by_field('department_code'))
        search_menu.addAction("По городу", lambda: self.search_by_field('city_before'))
        search_menu.addSeparator()
        search_menu.addAction("Расширенный поиск", self.show_advanced_search)

        # Меню Справка
        help_menu = menubar.addMenu("Справка")
        help_menu.addAction("О программе", self.show_about)
        help_menu.addAction("Справка", self.show_help)

    def setup_toolbar(self):
        """Настраивает панель инструментов"""

        toolbar = self.addToolBar("Основная")
        toolbar.setMovable(False)

        actions = [
            ("➕ Добавить", self.add_student, "add.png"),
            ("✏️ Редактировать", self.edit_student, "edit.png"),
            ("🗑️ Удалить", self.delete_student, "delete.png"),
            ("🔍 Поиск", self.show_search_dialog, "search.png"),
            ("📤 Экспорт", self.export_data, "export.png"),
            ("🔄 Обновить", self.load_data, "refresh.png"),
        ]

        for text, slot, icon in actions:
            # Вместо иконок используем текст
            action = toolbar.addAction(text)
            action.triggered.connect(slot)

    def setup_statusbar(self):
        """Настраивает строку состояния"""

        self.statusBar().showMessage("Готово")

        # Добавляем постоянные виджеты в статусбар
        self.db_status = QLabel("БД: ❌")
        self.record_count = QLabel("Записей: 0")

        self.statusBar().addPermanentWidget(self.db_status)
        self.statusBar().addPermanentWidget(self.record_count)

    def load_data(self):
        """Загружает данные из базы"""

        try:
            students = self.db.get_students(limit=100)

            self.table.setRowCount(len(students))

            for row, student in enumerate(students):
                # Используем initials вместо first_name
                self.table.setItem(row, 0, QTableWidgetItem(str(student['id'])))
                self.table.setItem(row, 1, QTableWidgetItem(student['last_name']))
                self.table.setItem(row, 2, QTableWidgetItem(student['initials']))
                self.table.setItem(row, 3, QTableWidgetItem(str(student['birth_year'])))
                self.table.setItem(row, 4, QTableWidgetItem(str(student['admission_year'])))
                self.table.setItem(row, 5, QTableWidgetItem(student['group_name']))
                self.table.setItem(row, 6, QTableWidgetItem(student['institute_name']))
                self.table.setItem(row, 7, QTableWidgetItem(student['department_name']))
                self.table.setItem(row, 8, QTableWidgetItem(student['city_before']))

                # Телефон показываем как "зашифровано" или пустое
                phone_item = QTableWidgetItem("***")
                phone_item.setToolTip("Телефон зашифрован")
                self.table.setItem(row, 9, phone_item)

            # Обновляем статистику
            self.record_count.setText(f"Записей: {len(students)}")
            self.db_status.setText("БД: ✅")
            self.statusBar().showMessage(f"Загружено {len(students)} записей", 3000)

            logger.info(f"Загружено {len(students)} студентов")

        except Exception as e:
            logger.error(f"Ошибка загрузки данных: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {e}")

    # Методы-заглушки для кнопок (реализуем позже)
    def add_student(self):
        """Открывает форму добавления нового студента"""
        try:
            # Загружаем список кафедр
            departments = self.db.execute_query("""
                SELECT d.id, d.code, d.name, i.code as institute_code
                FROM departments d
                JOIN institutes i ON d.institute_id = i.id
                ORDER BY i.code, d.code
            """)

            form = StudentForm(self.db, departments=departments)

            if form.exec_() == QDialog.Accepted:
                # Получаем данные из формы
                student_data = form.student_data

                # Получаем шифратор
                encryptor = get_encryptor()

                # Добавляем студента в БД
                student_id = self.db.add_student_with_encryption(student_data, encryptor)

                if student_id:
                    QMessageBox.information(self, "Успех",
                                            f"Студент успешно добавлен (ID: {student_id})")
                    self.load_data()  # Обновляем таблицу
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось добавить студента")

        except Exception as e:
            logger.error(f"Ошибка добавления студента: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка добавления: {e}")

    def edit_student(self):
        """Открывает форму редактирования выбранного студента"""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Предупреждение", "Выберите студента для редактирования")
            return

        try:
            # Получаем ID студента
            student_id_item = self.table.item(selected_row, 0)
            if not student_id_item:
                return

            student_id = int(student_id_item.text())

            # Загружаем данные студента
            query = """
                SELECT 
                    s.*,
                    d.code as department_code,
                    i.code as institute_code
                FROM students s
                JOIN departments d ON s.department_id = d.id
                JOIN institutes i ON d.institute_id = i.id
                WHERE s.id = %s
            """

            result = self.db.execute_query(query, (student_id,))
            if not result:
                QMessageBox.warning(self, "Ошибка", "Студент не найден")
                return

            student_data = result[0]

            # Загружаем список кафедр
            departments = self.db.execute_query("""
                SELECT d.id, d.code, d.name, i.code as institute_code
                FROM departments d
                JOIN institutes i ON d.institute_id = i.id
                ORDER BY i.code, d.code
            """)

            # Создаем форму редактирования
            form = StudentForm(self.db, student_data=student_data, departments=departments)

            if form.exec_() == QDialog.Accepted:
                # Получаем обновленные данные
                updated_data = form.student_data

                # Получаем шифратор
                encryptor = get_encryptor()

                # Обновляем студента в БД
                success = self.db.update_student_with_encryption(
                    student_id, updated_data, encryptor
                )

                if success:
                    QMessageBox.information(self, "Успех", "Данные студента обновлены")
                    self.load_data()  # Обновляем таблицу
                else:
                    QMessageBox.critical(self, "Ошибка", "Не удалось обновить данные")

        except Exception as e:
            logger.error(f"Ошибка редактирования студента: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка редактирования: {e}")

    def delete_student(self):
        """Удаляет выбранного студента"""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Предупреждение", "Выберите студента для удаления")
            return

        try:
            # Получаем ID студента
            student_id_item = self.table.item(selected_row, 0)
            if not student_id_item:
                return

            student_id = int(student_id_item.text())

            # Получаем информацию о студенте для подтверждения
            last_name = self.table.item(selected_row, 1).text()
            initials = self.table.item(selected_row, 2).text()

            # Запрашиваем подтверждение
            reply = QMessageBox.question(
                self, "Подтверждение удаления",
                f"Вы уверены, что хотите удалить студента:\n{last_name} {initials}?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # Удаляем студента
                query = "DELETE FROM students WHERE id = %s"
                self.db.execute_query(query, (student_id,), fetch=False)

                QMessageBox.information(self, "Успех", "Студент удален")
                self.load_data()  # Обновляем таблицу

        except Exception as e:
            logger.error(f"Ошибка удаления студента: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка удаления: {e}")
            
    def show_search_dialog(self):
        QMessageBox.information(self, "Поиск", "Функция поиска")

    def export_data(self):
        QMessageBox.information(self, "Экспорт", "Функция экспорта")

    def search_by_field(self, field):
        QMessageBox.information(self, "Поиск", f"Поиск по полю: {field}")

    def show_advanced_search(self):
        QMessageBox.information(self, "Расширенный поиск", "Функция расширенного поиска")

    def export_to_word(self):
        QMessageBox.information(self, "Экспорт", "Экспорт в Word")

    def export_to_excel(self):
        QMessageBox.information(self, "Экспорт", "Экспорт в Excel")

    def show_about(self):
        QMessageBox.about(self, "О программе",
                          "База данных студентов\n\n"
                          "Версия 1.0\n"
                          "Разработано в рамках курсового проекта\n"
                          "Тема: Учет персональных данных студентов")

    def show_help(self):
        QMessageBox.information(self, "Справка",
                                "Для начала работы:\n"
                                "1. Убедитесь, что PostgreSQL запущен\n"
                                "2. Настройте подключение в файле .env\n"
                                "3. Используйте кнопки для управления данными")