import sys
import time
from concurrent.futures import ThreadPoolExecutor
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QProgressBar, QLabel



class WorkerSignals(QObject):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)

def download_task(signals: WorkerSignals):
    """Симулює довготривале завантаження файлу."""
    try:
        for i in range(101):
            time.sleep(0.05)
            signals.progress.emit(i)
        return "Завантаження завершено успішно!" # Можемо повернути результат
    except Exception as e:
        # У concurrent.futures помилки передаються через об'єкт Future
        raise e

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # print("MainWindow init")
        self.setWindowTitle("Example 4: ThreadPoolExecutor")
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
        self.start_button.clicked.connect(self.start_download)
        self.signals = WorkerSignals()
        self.signals.progress.connect(self.update_progress)
        # Створюємо пул потоків, який буде жити разом з вікном
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.start_download()
        # time.sleep(40)

    def start_download(self):
        self.start_button.setEnabled(False)
        self.status_label.setText("Завантаження...")
        
        # Відправляємо завдання в пул
        future = self.executor.submit(download_task, self.signals)
        # Додаємо функцію, яка виконається, коли завдання буде завершено
        future.add_done_callback(self.on_future_finished)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def on_future_finished(self, future):
        """Цей слот виконується, коли об'єкт Future завершує роботу."""
        try:
            # .result() поверне значення з 'return' або згенерує помилку, що сталася в потоці
            message = future.result()
        except Exception as e:
            message = f"Помилка: {e}"
            
        self.status_label.setText(message)
        self.progress_bar.setValue(0)
        self.start_button.setEnabled(True)

    def closeEvent(self, event):
        """Коректно закриваємо пул потоків при виході."""
        self.executor.shutdown(wait=False)
        event.accept()

if __name__ == "__main__":
    # print("Starting application")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
