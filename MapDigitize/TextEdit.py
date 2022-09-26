from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Calendar(object):
#    def printDate(self, qDate):
#        date =('{0}-{1}-{2}'.format(qDate.month(), qDate.day(), qDate.year()))
#        #print(date)
#        self.setupUi.textedit.setText(self.date.toStrings())

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(395, 310)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.calendarWidget = QtWidgets.QCalendarWidget(self.centralwidget)
        self.calendarWidget.setGeometry(QtCore.QRect(0, 0, 392, 236))
        self.calendarWidget.setObjectName("calendarWidget")
        #self.calendarWidget.clicked.connect(lambda dateval:print(dateval))
#        self.calendarWidget.clicked.connect(self.printDate)
        
        MainWindow.setCentralWidget(self.centralwidget)
        
        self.textedit = QtWidgets.QLineEdit(self.centralwidget)
        self.textedit.setGeometry(QtCore.QRect(20,245,80,30))
        self.textedit.setObjectName("textedit")
        #self.printDate(self.label.setText(date))
        
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        #self.label.setText(_translate("Mainwindow","date"))


class Calendar(QtWidgets.QMainWindow, Ui_Calendar):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.calendarWidget.clicked.connect(self.printDate)

    def printDate(self, qDate):
        date =('{0}-{1}-{2}'.format(qDate.month(), qDate.day(), qDate.year()))
        
#        self.setupUi.textedit.setText(self.date.toStrings())
        self.textedit.setText(date)
        

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
#    MainWindow = QtWidgets.QMainWindow()
#    ui = Ui_Calendar()
#    ui.setupUi(MainWindow)
#    MainWindow.show()

    w = Calendar()
    w.show()
    sys.exit(app.exec_())