import sys
import time
from concurrent.futures import ThreadPoolExecutor
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout

# =================================================================================
# Example 4: concurrent.futures.ThreadPoolExecutor
# python -m nuitka --onefile --enable-plugin=pyqt5 --windows-console-mode=disable --lto=yes --output-dir=build_QThreadPoolExecutor clock_threadpoolexecutor.py
# =================================================================================

class WorkerSignals(QObject):
    time_updated = pyqtSignal(str)

is_running = True
signals = WorkerSignals()

def clock_service():
    """
    Функція, яку ми будемо виконувати в іншому потоці.
    Вона не може бути методом класу MainWindow, бо `submit` потребує просто функцію.
    """
    while is_running:
        current_time = time.strftime('%H:%M:%S', time.localtime())
        signals.time_updated.emit(current_time)
        time.sleep(1)
    return "Clock service stopped"


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Годинник на PyQt5. ThreadPoolExecutor")
        self.setGeometry(100, 100, 600, 200)

        container = QWidget()
        container.setStyleSheet("background-color: black;")
        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignCenter)
        
        self.clock_label = QLabel("00:00:00")
        font = QFont("Arial", 50, QFont.Bold)
        self.clock_label.setFont(font)
        self.clock_label.setStyleSheet("color: white;")
        layout.addWidget(self.clock_label)
        
        self.setCentralWidget(container)

        signals.time_updated.connect(self.update_clock_label)
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.future = self.executor.submit(clock_service)
        self.future.add_done_callback(self.on_task_done)

    def update_clock_label(self, time_text):
        self.clock_label.setText(time_text)
    
    def on_task_done(self, future):
        """Callback, що виконується по завершенню роботи потоку."""
        try:
            result = future.result()
            print(f"Результат з потоку: {result}")
        except Exception as e:
            print(f"В потоці сталася помилка: {e}")

    def closeEvent(self, event):
        global is_running
        is_running = False
        self.executor.shutdown(wait=True)
        event.accept()

def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
