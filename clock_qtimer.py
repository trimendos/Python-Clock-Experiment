from PyQt5.QtCore import QTimer, QTime, Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout
import sys


# =================================================================================
# Example 2: QTimer clock_qtimer.py
# python -m nuitka --onefile --enable-plugin=pyqt5 --windows-console-mode=disable --lto=yes --output-dir=build_Qtimer clock_qtimer.py
# =================================================================================
class ClockWidget(QWidget):
    """Віджет, що містить QLabel для відображення годинника."""
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        self.clock_label = QLabel("00:00:00")
        font = QFont("Arial", 50, QFont.Bold)
        self.clock_label.setFont(font)
        self.clock_label.setStyleSheet("color: white;")
        
        layout.addWidget(self.clock_label)
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super(MainWindow, self).__init__()
        self.setWindowTitle("Годинник на PyQt5. QTimer")
        self.setGeometry(100, 100, 600, 200)

        self.clock_container = ClockWidget()
        self.clock_container.setStyleSheet("background-color: black;")

        self.setCentralWidget(self.clock_container)
        self.setup_timer()        
        self.update_time()

    def setup_timer(self):
        """Створює та запускає QTimer."""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

    def update_time(self):
        """Отримує поточний час і встановлює його в QLabel."""
        current_time = QTime.currentTime()
        time_text = current_time.toString('hh:mm:ss')
        self.centralWidget().clock_label.setText(time_text)

def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
