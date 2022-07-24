from PyQt5.QtWidgets import (QWidget, QSlider, QLineEdit, QLabel, QPushButton, QScrollArea,QApplication,
                             QHBoxLayout, QVBoxLayout, QMainWindow)
from PyQt5.QtCore import Qt, QSize
from PyQt5 import QtWidgets, uic
import sys


class ScollWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.scroll = QScrollArea()             # Scroll Area which contains the widgets, set as the centralWidget
        self.widget = QWidget()                 # Widget that contains the collection of Vertical Box
        self.vbox = QVBoxLayout()               # The Vertical Box that contains the Horizontal Boxes of  labels and buttons
        self.mainlayout = QHBoxLayout()          

        self.widget.setLayout(self.vbox)

        #Scroll Area Properties
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)

        # self.setCentralWidget(self.scroll)
        self.mainlayout.addWidget(self.scroll)
        self.setLayout(self.mainlayout)

        self.setGeometry(100, 100, 300, 900)
        self.setWindowTitle('Scroll Area Demonstration')
        self.show()

        return
    def addWidget(self,object):
        self.vbox.addWidget(object)

def main():
    app = QtWidgets.QApplication(sys.argv)
    main = ScollWindow()
    for i in range(1,50):
        object = QLabel("TextLabel Scroll Area which contains the widgets, set as the centralWidget Widget that contains the collection of Vertical Box Widget that contains the collection of Vertical Box Widget that contains the collection of Vertical Box Widget that contains the collection of Vertical Box")
        main.addWidget(object)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()