# h_layout.py

"""Horizontal layout example."""

import sys

import get_info_test

from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QPushButton,
    QWidget,
    QLabel,
    QMainWindow,


)

from PyQt6.QtCore import pyqtSlot, QTimer

# app = QApplication([])
# window = QWidget()
# window.setWindowTitle("QHBoxLayout")

# layout = QHBoxLayout()
# a = 0
# b = 0
# c = 0
# d = 0
# volt1 = layout.addWidget(QLabel("V1:" + str(a)))
# volt2 = layout.addWidget(QLabel("V2:" + str(b)))
# volt3 = layout.addWidget(QLabel("V3:" + str(c)))
# volt4 = layout.addWidget(QLabel("V4:" + str(d)))

# layout.addWidget(QPushButton("update info(doesnt work)"))
# window.setLayout(layout)

# def update():
#     cur_volt_a = 1 # copy paste(get this somewhere)
#      #grrr addwidget





class main(QMainWindow):
    def __init__(self):

        super().__init__()
        self.setWindowTitle("RSX BMS")

        self.volt1 = QLabel("V1: " + "what?") # repeat for 4 voltages

        self.button = QPushButton("update info(doesnt work)")
        self.button.clicked.connect(self.button_clicked)

        layout = QHBoxLayout() # repeat for 4 voltages
        layout.addWidget(self.volt1)
        layout.addWidget(self.button)

        container = QWidget()
        container.setLayout(layout)

        # setup timer for getting infor from main loop
        self.timer=QTimer()
        self.timer.setInterval(0)
        self.timer.timeout.connect(self.button_clicked) # we connect to button_clicked


        self.setCentralWidget(container)

    # doesnt work(who knew)
    def button_clicked(self):
        print("hi")
        # self.timer.start(1000)
        self.volt1.setText("V1: " + str(get_info_test.test))#data is not continous
        self.volt1.repaint()
        # self.timer.stop()


#a = 0 # get info somewhere
app = QApplication(sys.argv)

window = main()
window.show()

app.exec()
