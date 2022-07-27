# from PyQt5.QtGui import *
# from PyQt5.QtPrintSupport import *
# from PyQt5.QtWidgets import*
from PyQt5.QtCore import *
# from PyQt5.QtGui import QImage, QPixmap, QPalette, QPainter,QPen,QColor
# from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtWidgets import QLabel, QMessageBox, QMainWindow, QDialog,QWidget,QHBoxLayout,QVBoxLayout, \
QDialogButtonBox,QLineEdit,QPushButton,QRadioButton,QScrollArea
# QMenu, QAction, \
    # qApp, 
    # QFileDialog, 
    # QGraphicsSimpleTextItem,QGraphicsEllipseItem
import numpy as np

def displayMessageBox(message):
    msg=QMessageBox()
    msg.setText(message)
    msg.exec_()
class getNameDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Line name!")
        self.name=QLineEdit(self)
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.name)
        self.layout.addWidget(self.buttonBox)        
        self.setLayout(self.layout)
    def getName(self):
        if self.exec_() == QDialog.Accepted:
            return self.name.text()

class ChangeNameDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("HELLO!")
        # self.coordedit=QLineEdit(self)
        # self.coordedit.setText('0')
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        # print(dir(Qt))

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        # message = QLabel("Something happened, is that OK?")
        # self.layout.addWidget(message)
        # self.layout.addWidget(self.coordedit)
        self.layout.addWidget(self.buttonBox)

        radiolayout= QHBoxLayout()        
        self.radioButton_x1 = QRadioButton('X1')
        self.radioButton_x2 = QRadioButton('X2')
        self.radioButton_y1 = QRadioButton('Y1')
        self.radioButton_y2 = QRadioButton('Y2')
        for btn in [self.radioButton_x1,self.radioButton_x2,self.radioButton_y1,self.radioButton_y2]:            
            radiolayout.addWidget(btn)
        self.radioButton_x1.toggled.connect(lambda:self.btnstate(self.radioButton_x1))
        self.radioButton_x2.toggled.connect(lambda:self.btnstate(self.radioButton_x2))
        self.radioButton_y1.toggled.connect(lambda:self.btnstate(self.radioButton_y1))
        self.radioButton_y2.toggled.connect(lambda:self.btnstate(self.radioButton_y2))
        # self.radioButton_x1.toggled
        # radiolayout.addWidget(self.radioButton_x2)
        radiowidget=QWidget()
        radiowidget.setLayout(radiolayout)
        self.layout.addWidget(radiowidget)
        self.setLayout(self.layout)
        self.coordinatefor = 'X1'

    def btnstate(self,btn):
        print(self.coordinatefor,btn.text())
        self.coordinatefor=btn.text()

    def getAxisnPointanme(self):
        if self.exec_() == QDialog.Accepted:
            # return self.coordinatefor,self.coordedit.text()
            return self.coordinatefor
        else:
            return None
class CoordInputRow(QWidget):
    def __init__(self,coordfor,parent=None):
        super().__init__(parent)
        inputlayout= QVBoxLayout()  
        radiolayout= QHBoxLayout()    
        self.pixelcoords=QPoint(0,0)    
        self.coordinatefor=coordfor if type(coordfor)==str else str(coordfor)
        self.pixelinfo_label=QLabel(self.coordinatefor+': ')
        self.coordedit=QLineEdit(self)
        self.pixelinfo_label.setStyleSheet("""QLabel {    
        margin:2px;        padding:2px;        }        """)
        self.coordedit.setStyleSheet("""QLineEdit {    
        border-radius: 5px;    
        text-align: center;
        border: 2px solid #8f8f91;
        border-radius: 6px;
        background-color: #fdfdfd;
        min-width: 40px;        }        """)        

        # radiolayout.addWidget(self.pixelinfo_label)
        radiolayout.addWidget(self.coordedit)

        self.changebtn = QPushButton("Change")
        self.changebtn.clicked.connect(self.ChangeName)
        # self.changebtn.setFixedHeight(40)
        self.changebtn.setStyleSheet("""QPushButton {    
        border-radius: 5px;    
        text-align: center;
        border: 2px solid #8f8f91;
        border-radius: 6px;
        background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #f6f7fa, stop: 1 #dadbde);
        min-width: 40px;        }        """)
        radiolayout.addWidget(self.changebtn)
        self.coordedit.setEnabled(False)
        self.changebtn.setEnabled(False)
        

        radiowidget=QWidget(parent)
        radiowidget.setLayout(radiolayout)
        # radiowidget.show()
        # radiowidget.setFixedWidth(150)
        inputlayout.addWidget(self.pixelinfo_label)
        inputlayout.addWidget(radiowidget)
        self.pixelinfo_label.setFixedHeight(20)
        radiowidget.setFixedHeight(35)
        self.setFixedHeight(58)
        self.setLayout(inputlayout)
    def clearAll(self):
        # print('in row clearAll')
        self.coordedit.setEnabled(False)
        self.changebtn.setEnabled(False)
        self.pixelcoords=QPoint(0,0) 
        self.pixelinfo_label.setText(self.coordinatefor+': ')
        self.setCoord(0)
        # self.setCoordName(row['name'])
    def ChangeName(self):
        if self.isPixelSet():
            cname=ChangeNameDialog()
            self.coordinatefor=cname.getAxisnPointanme()
            if self.coordinatefor:
                print(self.coordinatefor)
                self.pixelinfo_label.setText(self.coordinatefor+': '+ '('+str(int(self.pixelcoords.x()))+', '+str(int(self.pixelcoords.y()))+')')
        else:
            msg=QMessageBox()
            msg.setText('First pick the pixel!!!')
            msg.exec_()
    def btnstate(self,btn):
        self.coordinatefor=btn.text()
    def getCoordinates(self):
        if len(self.coordinatefor) and len(self.coordedit.text()):
            return {'name':self.coordinatefor,'pixel_loc':self.pixelcoords ,'value':float(self.coordedit.text())}
        else:
            print('Coordinates not set')
            return None
    def setCoord(self,value):
        self.coordedit.setText(str(value))
    def getCoordName(self):
        if len(self.coordinatefor):
            return self.coordinatefor
        else:
            return None
    def setCoordName(self,name):
        self.coordinatefor=name

    # def setCoordName(self,name):
    #     self.coordinatefor=name


    def setPixelCoords(self,point):
        
        self.pixelcoords=point
        # print('point in setPixelCoords',point)
        if point.x():
            self.pixelinfo_label.setText(self.coordinatefor+': '+ '('+str(int(self.pixelcoords.x()))+', '+str(int(self.pixelcoords.y()))+')')
            self.changebtn.setEnabled(True)
            self.coordedit.setEnabled(True)
        else:
            print('point in setPixelCoords else',point)
            # self.pixelinfo_label.setText(self.coordinatefor+': ')

    def getPixelCoords(self):
        if self.pixelcoords.x():
            return self.pixelcoords
        else:
            print('Pixel not set')
            return 0
    def isPixelSet(self):
        print('in isPixelSet self.pixelcoords.x() ',self.pixelcoords.x())
        if self.pixelcoords.x():
            return True
        else:
            return False
    def isValueset(self):
        try:
            float(self.coordedit.text())
            return True
        except:
            return False
        #    msg= QMessageBox('Please set value for '+self.coordinatefor)
        #    msg.exec_()
class NmaeInputRow4Pixel(QWidget):
    def __init__(self,coordfor,pixcoords,name,parent=None):
        super().__init__(parent)
        # inputlayout= QVBoxLayout()  
        inputlayout= QHBoxLayout()    
        self.parent=parent
        self.pixelcoords=pixcoords   
        self.coordinatefor=coordfor if type(coordfor)==str else str(coordfor)
        self.pixelinfo_label=QLabel(str(self.coordinatefor)+': ')
        self.coordedit=QLineEdit(self)
        self.coordedit.setText(name)
        self.coordedit.textChanged.connect(self.onTextChange)
        self.pixelinfo_label.setStyleSheet("""QLabel {    
        margin:0px;        padding:0px;     font-size: 8pt;   }        """)
        self.coordedit.setStyleSheet("""QLineEdit {    
        border-radius: 3px;    
        text-align: center;
        border: 2px solid #8f8f91;
        background-color: #fdfdfd;
        min-width: 40px;        }        """)    
        self.setPixelCoords()    
        inputlayout.addWidget(self.pixelinfo_label)
        inputlayout.addWidget(self.coordedit)

        self.pixelinfo_label.setFixedHeight(20)
        self.setFixedHeight(58)
        self.setLayout(inputlayout)
    def onTextChange(self):
        self.parent.onTextChange(self.coordinatefor)

    def clearAll(self):
        # print('in row clearAll')
        self.pixelcoords=QPoint(0,0) 
        self.pixelinfo_label.setText(str(self.coordinatefor)+': ')
        self.setCoord('')
        # self.setCoordName(row['name'])
    def getCoordinates(self):
        # if len(self.coordedit.text()):
        return (self.coordedit.text(),self.pixelcoords )
            # return {'name':self.coordinatefor,'pixel_loc':self.pixelcoords ,'value':float(self.coordedit.text())}
        # else:
        #     print('Coordinates not set')
        #     return None
    def getCoordName(self):
        if len(self.coordinatefor):
            return self.coordinatefor
        else:
            return None
    def setPixelCoords(self):        
        # self.pixelcoords=point
        # print('point in setPixelCoords',point)
        if self.pixelcoords.x():
            self.pixelinfo_label.setText(self.coordinatefor+': '+ '('+str(int(self.pixelcoords.x()))+', '+str(int(self.pixelcoords.y()))+')')
        else:
            print('point in setPixelCoords else',self.pixelcoords)


    def getPixelCoords(self):
        if self.pixelcoords.x():
            return self.pixelcoords
        else:
            print('Pixel not set')
            return 0
    def isPixelSet(self):
        # print('in isPixelSet self.pixelcoords.x() ',self.pixelcoords.x())
        if self.pixelcoords.x():
            return True
        else:
            return False
    def isValueset(self):
        try:
            float(self.coordedit.text())
            return True
        except:
            return False

class EmptyLinewidget(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.scroll = QScrollArea()   
        #Scroll Area Properties

        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setWidgetResizable(True)
        # self.scroll.setWidget(self.widget)
        self.mylayout= QVBoxLayout() 
        self.mylayout.addWidget(self.scroll)
        self.setLayout(self.mylayout)
        self.setFixedHeight(350)
    def mySetWidget(self,widget):
        self.scroll.setWidget(widget)
    # def clear():
    #     for i in reversed(range(self.mylayout.count())): 
    #         self.coordlayout.itemAt(i).widget().setParent(None)

# class DigitizedLine(QWidget):
class DigitizedLine(EmptyLinewidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        # self.allcoords=[]
        # scrollwidget=EmptyLinewidget()
        mwidget=QWidget()
        self.coordlayout= QVBoxLayout() 
        mwidget.setLayout(self.coordlayout)
        self.line=[]
        # self.setFixedHeight(350)
        self.mySetWidget(mwidget)
    def addRow(self,name,pixcoords):
        row = NmaeInputRow4Pixel(self.coordlayout.count()+1,pixcoords,name,parent=self)
        self.line.append((name,pixcoords))
        self.coordlayout.addWidget(row)
    def clearAll(self):
        self.line=[]
        for i in reversed(range(self.coordlayout.count())): 
            self.coordlayout.itemAt(i).widget().setParent(None)

    def setLine(self,line):
        self.clearAll()  
        self.line=line            
        done=False
        for coordfor,(name,pixcoords) in enumerate(self.line):
            row = NmaeInputRow4Pixel(coordfor,pixcoords,name,parent=self)
            self.coordlayout.addWidget(row)
        return True

    def isAllvaluesSet(self):
        allset=True
        for i in range(self.coordlayout.count()): 
            if not self.coordlayout.itemAt(i).widget().isValueset():
                return False
        return allset
    def onTextChange(self,coordinatefor):
        for i in reversed(range(self.coordlayout.count())): 
            if self.coordlayout.itemAt(i).widget().coordinatefor==coordinatefor:
                self.line[i]=self.coordlayout.itemAt(i).widget().getCoordinates()
                # print(self.line[i])
    
    def getLine(self):
        return self.line
    def getCoordinates(self):
        if self.isAllvaluesSet(): 
            print('self.allcoords in coordsetting.py ',self.allcoords)
            return self.allcoords
        else:
            msg = QMessageBox("Set all the values")
            msg.exec_()
            return []    
    def loadCoords(self,coordpath):
        # coordinates=np.load(coordpath) 
        rows=np.load(coordpath,allow_pickle=True)
        self.allcoords=rows
        for row,objrow in zip(rows,self.allrows):
            # print(row['name'],row['pixel_loc'],row['value'])
            # coordinatefor
            objrow.setCoordName(row['name'])
            objrow.setPixelCoords(row['pixel_loc'])
            objrow.setCoord(str(row['value']))
            objrow.changebtn.setEnabled(True)
            objrow.coordedit.setEnabled(True)
        self.freezcoordinatesetting=True
        self.unfreezebtn.setEnabled(True)
        
    def unfreeze(self):
        qm = QMessageBox()
        ret=qm.question(self,'', "Are you sure to reset all the values?", qm.Yes | qm.No)
        if ret == qm.Yes:
            self.clearAll()
            self.parent.setcoordinatesEditable(True)    

class CoordinateSetting(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.allcoords=[]
        self.freezcoordinatesetting =False
        self.parent=parent
        # self.isAllvaluesSet=False
        coordlayout= QVBoxLayout()   
        self.x1c=CoordInputRow('X1')
        self.x2c=CoordInputRow('X2')
        self.y1c=CoordInputRow('Y1')
        self.y2c=CoordInputRow('Y2')
        self.allrows=[self.x1c,self.x2c,self.y1c,self.y2c]
        for row in self.allrows:
            coordlayout.addWidget(row)


        self.setbtn = QPushButton("Set Map Coordinates")
        self.setbtn.clicked.connect(self.setCoordinates)
        self.unfreezebtn = QPushButton("Unfreez")
        self.unfreezebtn.clicked.connect(self.unfreeze)

        self.exportbtn = QPushButton("Export")
        # self.exportbtn.clicked.connect(self.ExportCoordinates)

        coordlayout.addWidget(self.setbtn)
        coordlayout.addWidget(self.unfreezebtn)
        self.setLayout(coordlayout)
        self.setFixedHeight(310)
        self.setbtn.setEnabled(False)
        self.unfreezebtn.setEnabled(False)
    def clearAll(self):
        print('in wgt clearAll')
        self.setbtn.setEnabled(False)
        self.unfreezebtn.setEnabled(False)
        for row in self.allrows:
            row.clearAll()
            # row.setCoord(0)
    
    def setPixelCoords(self,point): 
        
        done=False
        for row in self.allrows:
            print(row.isPixelSet())
            if not row.isPixelSet():
                row.setPixelCoords(point)
                done=True
                break
        if self.isAllpixelsSet():
            self.setbtn.setEnabled(True)
            # self.deactivateSetpixel=True
            return False
        return True
    def isAllpixelsSet(self):
        allset=True
        for row in self.allrows:
            if not row.isPixelSet():
                allset=False
        return allset
    def isAllvaluesSet(self):
        allset=True
        for row in self.allrows:
            if not row.isValueset():
                allset=False
        # if not allset:
        #     msg= QMessageBox('Please set all values'+self.coordinatefor)
        #     msg.exec_()
        return allset
    def setCoordinates(self):
        if self.isNamesUnique():
            if self.isAllvaluesSet():
                self.allcoords=[]
                for row in self.allrows:
                    if row.isValueset():
                        self.allcoords.append(row.getCoordinates())
                self.freezcoordinatesetting=True
                self.setbtn.setEnabled(False)
                self.unfreezebtn.setEnabled(True)
                displayMessageBox('Set coordinates. Now you can export them')
            else:
                displayMessageBox('First set all the values!!!')
        else:
            displayMessageBox('Names repeating. Set them right')


        return True

    def isNamesUnique(self):
        allnames=[row.getCoordName() for row in self.allrows]
        names=np.unique(allnames)
        if len(allnames)==len(names):
            return True
        else:
            return False




    def getCoordinates(self):
        if self.isAllvaluesSet(): 
            # print('self.allcoords in coordsetting.py ',self.allcoords)
            return self.allcoords
        else:
            return []    
    def loadCoords(self,coordpath):
        # coordinates=np.load(coordpath) 
        rows=np.load(coordpath,allow_pickle=True)
        # rows
        self.allcoords=rows
        for row,objrow in zip(rows,self.allrows):
            # print(row['name'],row['pixel_loc'],row['value'])
            # coordinatefor
            objrow.setCoordName(row['name'])
            objrow.setPixelCoords(row['pixel_loc'])
            objrow.setCoord(str(row['value']))
            objrow.changebtn.setEnabled(True)
            objrow.coordedit.setEnabled(True)
        self.freezcoordinatesetting=True
        self.unfreezebtn.setEnabled(True)
        
    def unfreeze(self):
        qm = QMessageBox()
        ret=qm.question(self,'', "Are you sure to reset all the values?", qm.Yes | qm.No)
        if ret == qm.Yes:
            self.clearAll()
            self.parent.setcoordinatesEditable(True)    

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    imageViewer = CoordinateSetting()
    imageViewer.show()
    sys.exit(app.exec_())
