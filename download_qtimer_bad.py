import sys
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QProgressBar, QLabel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Example 2: QTimer (НЕПРАВИЛЬНИЙ)")
        self.setGeometry(80, 80, 500, 200)
        # --- UI Setup ---
        self.progress_bar = QProgressBar()
        self.status_label = QLabel("Натисніть для старту. УВАГА: GUI ЗАВИСНЕ!")
        self.start_button = QPushButton("Почати завантаження")
        layout = QVBoxLayout()
        layout.addWidget(self.start_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # --- Logic ---
        self.start_button.clicked.connect(self.start_download_blocking)        
        self.start_download_blocking()

    def start_download_blocking(self):
        """
        !!! АНТИ-ПАТЕРН !!!
        Ця функція виконується в головному потоці GUI.
        Цикл з time.sleep() повністю заблокує цикл подій, і додаток "зависне".
        Оновлення прогрес-бару не будуть видимі до самого кінця.
        """
        self.start_button.setEnabled(False)
        self.status_label.setText("Завантаження... (GUI заморожено)")
        # Оскільки оновлення GUI також відбуваються в циклі подій,
        # ми не побачимо цей текст до завершення блокуючої операції.
        QApplication.processEvents() # Можна примусово обробити події, але це "костиль"

        # Симуляція довготривалої задачі
        for i in range(101):
            time.sleep(0.05)  # Ця лінія ЗАМОРОЖУЄ ВЕСЬ ДОДАТОК
            self.progress_bar.setValue(i) # Це оновлення не буде відмальовано

        # Цей код виконається лише через 5 секунд
        self.status_label.setText("Завантаження завершено!")
        self.start_button.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
