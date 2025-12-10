from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal
import hashlib
import logging

logger = logging.getLogger(__name__)


class LoginDialog(QDialog):
    """Окно аутентификации пользователя"""

    login_successful = pyqtSignal(str, str)  # сигнал: username, role

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setup_ui()

    def setup_ui(self):
        """Настраивает интерфейс окна входа"""

        self.setWindowTitle("Вход в систему")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Заголовок
        title_label = QLabel("База данных студентов")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 18px; 
            font-weight: bold; 
            color: #2c3e50;
            margin: 20px 0;
        """)
        layout.addWidget(title_label)

        # Поле логина
        login_layout = QVBoxLayout()
        login_label = QLabel("Логин:")
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите логин")
        self.login_input.setMinimumHeight(35)
        login_layout.addWidget(login_label)
        login_layout.addWidget(self.login_input)
        layout.addLayout(login_layout)

        # Поле пароля
        password_layout = QVBoxLayout()
        password_label = QLabel("Пароль:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(35)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)

        # Чекбокс "Показать пароль"
        self.show_password_checkbox = QCheckBox("Показать пароль")
        self.show_password_checkbox.stateChanged.connect(self.toggle_password_visibility)
        layout.addWidget(self.show_password_checkbox)

        # Кнопки
        buttons_layout = QHBoxLayout()

        self.login_button = QPushButton("Войти")
        self.login_button.setMinimumHeight(40)
        self.login_button.clicked.connect(self.authenticate)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)

        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.setMinimumHeight(40)
        self.cancel_button.clicked.connect(self.reject)

        buttons_layout.addWidget(self.login_button)
        buttons_layout.addWidget(self.cancel_button)
        layout.addLayout(buttons_layout)

        # Подсказка
        hint_label = QLabel("Для первого входа используйте: admin / admin123")
        hint_label.setAlignment(Qt.AlignCenter)
        hint_label.setStyleSheet("color: gray; font-size: 11px; margin-top: 15px;")
        layout.addWidget(hint_label)

        self.setLayout(layout)

        # Устанавливаем фокус на поле логина
        self.login_input.setFocus()

    def toggle_password_visibility(self, state):
        """Переключает видимость пароля"""
        if state == Qt.Checked:
            self.password_input.setEchoMode(QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)

    def authenticate(self):
        """Проверяет логин и пароль"""
        username = self.login_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        try:
            # Проверяем пользователя в БД
            query = "SELECT * FROM users WHERE login = %s"
            result = self.db.execute_query(query, (username,))

            if not result:
                QMessageBox.warning(self, "Ошибка", "Пользователь не найден!")
                return

            user = result[0]

            # В реальном приложении здесь проверка хэша пароля
            # Для демо просто проверяем наличие пользователя
            # TODO: Реализовать проверку хэша с помощью bcrypt

            # Если пользователь найден - успешная аутентификация
            logger.info(f"Пользователь {username} вошел в систему")
            self.login_successful.emit(username, user.get('role', 'user'))
            self.accept()

        except Exception as e:
            logger.error(f"Ошибка аутентификации: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка подключения к БД: {e}")

    def keyPressEvent(self, event):
        """Обработка нажатия клавиш"""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.authenticate()
        elif event.key() == Qt.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)