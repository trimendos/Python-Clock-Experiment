import sys
import time
import threading
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QProgressBar, QLabel

# Клас для сигналів, щоб безпечно спілкуватися з головним потоком GUI
class WorkerSignals(QObject):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)

# Функція, яка буде виконуватися в окремому потоці
def download_task(signals: WorkerSignals):
    """
    Симулює довготривале завантаження файлу.
    Приймає об'єкт сигналів для звітування про прогрес.
    """
    try:
        for i in range(101):
            time.sleep(0.05)  # Імітація блокуючої операції I/O
            signals.progress.emit(i)
        signals.finished.emit("Завантаження завершено успішно!")
    except Exception as e:
        signals.finished.emit(f"Помилка: {e}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Example 1: threading.Thread")
        self.setGeometry(80, 80, 500, 200)
        
        # --- UI Setup ---
        self.progress_bar = QProgressBar()
        self.status_label = QLabel("Натисніть для старту.")
        self.start_button = QPushButton("Почати завантаження")
        
        layout = QVBoxLayout()
        layout.addWidget(self.start_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # --- Logic ---
        # self.start_button.clicked.connect(self.start_download)
        
        self.signals = WorkerSignals()
        self.signals.progress.connect(self.update_progress)
        self.signals.finished.connect(self.on_finished)
        self.start_download()

    def start_download(self):
        """Запускає завантаження в новому потоці."""
        self.start_button.setEnabled(False)
        self.status_label.setText("Завантаження...")
        
        # Створюємо та запускаємо потік
        downloader_thread = threading.Thread(target=download_task, args=(self.signals,), daemon=True)
        downloader_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def on_finished(self, message):
        self.status_label.setText(message)
        self.progress_bar.setValue(0)
        self.start_button.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())