import sys
from datetime import datetime
from PyQt5.Qt import Qt
from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import time
from nback import Nback
import multiprocessing as mp
import numpy as np

SAVEPATH = "n-back task/data/"

class Communication(QObject):
    closeapp = pyqtSignal()


def startNback(sequence, q):
    nback = Nback()
    timestampe_arr = nback.play_nback_sequence(sequence)
    q.put(timestampe_arr)


class UI_MainWindow(object):
    def __init__(self):
        super(UI_MainWindow, self).__init__()

    def initUI(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.label = QLabel("Press start to start!", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setGeometry(0, 100, 800, 300)
        self.font = QtGui.QFont()
        self.font.setFamily("Courier New")
        self.font.setPointSize(15)
        self.label.setFont(self.font)

        self.btnStart = QPushButton("Start", self)
        self.btnStart.setGeometry(350,400,100,70)
        self.btnStart.clicked.connect(self.start)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateLabel)

    def start(self):
        self.data = []
        self.startTime = datetime.now()
        datapoint = {"event": "start", "time": self.startTime.timestamp()}
        self.data.append(datapoint)
        self.sequence = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.currentIndex = 0
        # timestamp_arr = self.nback.play_nback_sequence([1, 2, 3, 4, 5, 6, 7, 8, 9])
        q = mp.Queue()
        p = mp.Process(target=startNback, args=(self.sequence, q))
        p.start()
        self.return_val = q.get()
        p.join()

        self.font.setPointSize(30)
        self.label.setFont(self.font)
        self.label.setText(str(self.sequence[self.currentIndex]))
        self.label.show()
        self.timer.start(1500)


    def updateLabel(self):
        if self.currentIndex < len(self.sequence) - 1:
            self.currentIndex += 1
            self.label.setText(str(self.sequence[self.currentIndex]))
            if int(self.label.text()) == 0:
                self.timer.stop()
                # self.label.hide()
        else:
            self.timer.stop()
            for i, v in enumerate(self.return_val):
                datapoint = {"event": self.sequence[i], "time": v}
                self.data.append(datapoint)

            self.saveData()
                

    def keyPressEvent(self, e):
        # if e.key() == Qt.Key_Space:
        self.keyPressHandle(e)

    def keyPressHandle(self, e):
        now = datetime.now()
        datapoint = {"event": e.key(), "time": now.timestamp()}
        self.data.append(datapoint)
        print(datapoint)
        
    def saveData(self):
        with open(SAVEPATH + self.startTime + ".csv", "w") as f:
            for datapoint in self.data:
                f.write(datapoint["time"] + "," + datapoint["event"] + "\n")


class MainWindow(QMainWindow, UI_MainWindow):
    def __init__(self):
        super().__init__()
        self.initUI(self)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, "Message","Are you sure to quit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    demo = MainWindow()
    demo.show()

    sys.exit(app.exec_())
