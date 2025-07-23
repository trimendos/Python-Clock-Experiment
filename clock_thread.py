from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QGridLayout
from datetime import datetime
import sys
import time
import threading


# =================================================================================
# Example 1: threading.Thread
# python -m nuitka --onefile --enable-plugin=pyqt5 --windows-console-mode=disable --lto=yes --output-dir=build_thread clock_thread.py
# =================================================================================

module = None
states = {"RUN": 0}


class WorkModule(QWidget):
    def __init__(self):
        super(WorkModule, self).__init__()        
        self.grid = QGridLayout()
        self.grid.setContentsMargins(0,0,0,0)
        self.grid.setSpacing(0)
        self.gclock = QLabel("00:00:00")
        font = QFont("Arial", 50, QFont.Bold)
        self.gclock.setFont(font)
        self.gclock.setStyleSheet("color: white;")
        self.ftline = QWidget()
        self.ftl = QGridLayout()
        self.ftl.setContentsMargins(0,0,0,0)
        self.ftl.setSpacing(3)
        self.ftl.addWidget(self.gclock,0,1)
        self.ftline.setLayout(self.ftl)
        self.grid.addWidget(self.ftline, 0,2)
        self.setLayout(self.grid)
        
class MainWindow(QMainWindow):
    time_upd = pyqtSignal(str)

    def __init__(self) -> None:
        super(MainWindow, self).__init__()
        global module
        self.setWindowTitle("Годинник на PyQt5. threading.Thread")
        self.setGeometry(100, 100, 600, 200)
        
        self.sugr = QGridLayout()
        self.sugr.setContentsMargins(0,0,0,0)
        self.sugr.setSpacing(0)

        module = WorkModule()
        self.sugr.addWidget(module,0,0)
        self.time_upd.connect(self.clock_upd)
        self.main_wid = QWidget(self)
        self.main_wid.setLayout(self.sugr)
        self.setCentralWidget(self.main_wid)        
        module.setStyleSheet("background-color: black;")

        clock = threading.Thread(target=self.clock_serv, args=(1,))
        clock.start()
        
    def clock_upd(self,tt):
        module.gclock.setText(tt)

    def clock_serv(self,name):
        while states["RUN"]:
            tt = datetime.now().strftime('%H:%M:%S')
            self.time_upd.emit(tt)
            time.sleep(1)

def main():
    app = QApplication(sys.argv)
    states["RUN"] = 1
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
