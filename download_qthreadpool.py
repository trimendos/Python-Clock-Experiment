import sys
import time
from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QProgressBar, QLabel

# Клас для сигналів - такий самий, як у першому прикладі
class WorkerSignals(QObject):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)

# Клас-працівник, який інкапсулює нашу задачу
class DownloadWorker(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()

    def run(self):
        """Логіка, яка виконується в фоновому потоці."""
        try:
            for i in range(101):
                time.sleep(0.05)
                self.signals.progress.emit(i)
            self.signals.finished.emit("Завантаження завершено успішно!")
        except Exception as e:
            self.signals.finished.emit(f"Помилка: {e}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Example 3: QThreadPool")
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
        self.thread_pool = QThreadPool.globalInstance() # Отримуємо доступ до глобального пулу потоків
        self.start_download()

    def start_download(self):
        self.start_button.setEnabled(False)
        self.status_label.setText("Завантаження...")
        
        # Створюємо працівника
        worker = DownloadWorker()
        # Підключаємо його сигнали до слотів GUI
        worker.signals.progress.connect(self.update_progress)
        worker.signals.finished.connect(self.on_finished)
        
        # Відправляємо працівника на виконання в пул потоків
        self.thread_pool.start(worker)

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