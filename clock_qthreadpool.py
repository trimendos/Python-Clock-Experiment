import sys
import time
from PyQt5.QtCore import (QObject, QRunnable, pyqtSignal, QThreadPool, Qt)
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout


# =================================================================================
# Example 3: QThreadPool & QRunnable
# python -m nuitka --onefile --enable-plugin=pyqt5 --windows-console-mode=disable --lto=yes --output-dir=build_QThreadPool clock_qthreadpool.py
# =================================================================================

class WorkerSignals(QObject):
    """
    Визначає сигнали, доступні з робочого потоку.
    Успадкування від QObject є обов'язковим для механізму сигналів.
    """
    time_updated = pyqtSignal(str)


class ClockWorker(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()
        self.is_running = True

    def run(self):
        """Логіка, яка буде виконуватися в окремому потоці."""
        while self.is_running:
            current_time = time.strftime('%H:%M:%S', time.localtime())
            self.signals.time_updated.emit(current_time)
            time.sleep(1)

    def stop(self):
        """Метод для зупинки циклу."""
        self.is_running = False


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Годинник на PyQt5. QThreadPool")
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
        self.thread_pool = QThreadPool.globalInstance()
        print(f"Максимальна кількість потоків у пулі: {self.thread_pool.maxThreadCount()}")
        self.worker = ClockWorker()
        self.worker.signals.time_updated.connect(self.update_clock_label)
        self.thread_pool.start(self.worker)

    def update_clock_label(self, time_text):
        self.clock_label.setText(time_text)

    def closeEvent(self, event):
        print("Вікно закривається, зупиняємо працівника...")
        self.worker.stop()
        self.thread_pool.waitForDone(500) 
        event.accept()


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()