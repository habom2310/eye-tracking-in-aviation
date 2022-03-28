import sys
from datetime import datetime
from PyQt5.Qt import Qt
from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from nback import Nback
import multiprocessing as mp
import numpy as np
import os
import sound_sequences

icon_path = os.path.join(os.path.dirname(__file__), 'static/icon.png')
nback = Nback()

class Communication(QObject):
    closeapp = pyqtSignal()

class SoundControl(QObject):
    finished = pyqtSignal(str)

    @pyqtSlot()
    def playSound(self, number):
        print("here")
        timestamp = nback.play_sound(number)
        self.finished.emit(f"{number}:{timestamp}")

class SoundThread(QThread):
    def __init__(self, number, parent=None):
        super(SoundThread, self).__init__(parent)
        self.number = number

    def run(self):
        self.timestamp = nback.play_sound(self.number)


class UI_MainWindow(object):
    def __init__(self):
        super(UI_MainWindow, self).__init__()
        self.isrunning = False
        self.sequence = np.array(sound_sequences.SET1)

    def initUI(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowTitle("N-Back Task")
        MainWindow.setWindowIcon(QIcon(icon_path))
        MainWindow.setFixedSize(QSize(800, 600))
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
        self.btnStart.setFocusPolicy(Qt.NoFocus)
        self.btnStart.setGeometry(350,400,100,70)
        self.btnStart.clicked.connect(self.start)

        self.btnSet1 = QPushButton("Set 1", self)
        self.btnSet1.setFocusPolicy(Qt.NoFocus)
        self.btnSet1.setGeometry(100,100,100,70)
        self.btnSet1.clicked.connect(self.chooseSet1)

        self.btnSet2 = QPushButton("Set 2", self)
        self.btnSet2.setFocusPolicy(Qt.NoFocus)
        self.btnSet2.setGeometry(350,100,100,70)
        self.btnSet2.clicked.connect(self.chooseSet2)

        self.btnSet3 = QPushButton("Set 3", self)
        self.btnSet3.setFocusPolicy(Qt.NoFocus)
        self.btnSet3.setGeometry(600,100,100,70)
        self.btnSet3.clicked.connect(self.chooseSet3)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateLabel)
    
    def chooseSet1(self):
        self.sequence = np.array(sound_sequences.SET1)
        self.statusBar().showMessage(f'Set 1 is chosen!{self.sequence}', 5000)
        self.resetBtnColor()
        self.btnSet1.setStyleSheet("background-color:#706a68;")

    def chooseSet2(self):
        self.sequence = np.array(sound_sequences.SET2)
        self.statusBar().showMessage(f'Set 2 is chosen!{self.sequence}', 5000)
        self.resetBtnColor()
        self.btnSet2.setStyleSheet("background-color:#706a68;")

    def chooseSet3(self):
        self.sequence = np.array(sound_sequences.SET3)
        self.statusBar().showMessage(f'Set 3 is chosen!{self.sequence}', 5000)
        self.resetBtnColor()
        self.btnSet3.setStyleSheet("background-color:#706a68;")

    def resetBtnColor(self):
        self.btnSet1.setStyleSheet("background-color:#ffffff;")
        self.btnSet2.setStyleSheet("background-color:#ffffff;")
        self.btnSet3.setStyleSheet("background-color:#ffffff;")

    def setButtonVisibility(self):
        if self.isrunning == True:
            self.btnSet1.setVisible(False)
            self.btnSet2.setVisible(False)
            self.btnSet3.setVisible(False)
            self.btnStart.setVisible(False)
        else:
            self.btnSet1.setVisible(True)
            self.btnSet2.setVisible(True)
            self.btnSet3.setVisible(True)
            self.btnStart.setVisible(True)

    def start(self):
        self.data = []
        self.startTime = datetime.now()
        datapoint = {"event": "start", "time": self.startTime.timestamp()}
        self.data.append(datapoint)
        self.currentIndex = 0
        self.isrunning = True
        self.setButtonVisibility()

        self.font.setPointSize(30)
        self.label.setFont(self.font)
        self.label.setText("Start!")
        self.timer.start(2000)

    @pyqtSlot(str)
    def handle_result(self, return_value):
        v = return_value.split(":")
        number = v[0]
        timestamp = v[1]
        datapoint = {"event": number, "time": timestamp}
        self.data.append(datapoint)

    def updateLabel(self):
        if self.currentIndex < len(self.sequence):
            self.label.setText(str(self.sequence[self.currentIndex]))
            self.st = SoundThread(self.sequence[self.currentIndex]-1)
            self.st.start()
            number = self.sequence[self.currentIndex]
            timestamp = datetime.now().timestamp()
            datapoint = {"event": number, "time": timestamp}
            print(datapoint)
            self.data.append(datapoint)
            self.currentIndex += 1
            
        else:
            self.timer.stop()
            self.saveData()
            self.label.setText("End!")
            self.isrunning = False
            self.setButtonVisibility()

    def keyPressEvent(self, e):
        if self.isrunning == True:
            now = datetime.now()
            datapoint = {"event": "key pressed", "time": now.timestamp()}
            self.data.append(datapoint)
            print(datapoint)
        
    def saveData(self):
        save_path = os.path.join(os.path.dirname(__file__), f"data/{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        with open(save_path, "w+") as f:
            f.write("time,event\n")
            for datapoint in self.data:
                f.write(str(datapoint["time"]) + "," + str(datapoint["event"]) + "\n")

        self.statusBar().showMessage(f'Data has been saved to {save_path}.')
            
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
