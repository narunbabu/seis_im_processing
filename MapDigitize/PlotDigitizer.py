#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import *
from PyQt5 import QtCore
# from PyQt5.QtGui import QImage, QPixmap, QPalette, QPainter,QPen,QColor
# from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
# from PyQt5.QtWidgets import QLabel, QSizePolicy, QScrollArea, QMessageBox, QMainWindow, QMenu, QAction, \
#     qApp, QFileDialog, QGraphicsSimpleTextItem,QGraphicsEllipseItem

from coordinatesetting import *
from coord_converter import *
from PyQt5.QtGui import *
from PyQt5.QtPrintSupport import *
from PyQt5.QtWidgets import*

from QtImageViewer import QtImageViewer
import numpy as np

class myListWidget(QListWidget):

   def Clicked(self,item):
      QMessageBox.information(self, "ListWidget", "You clicked: "+item.text())


class PlotDigitizer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.printer = QPrinter()
        self.scaleFactor = 0.0
        self.projectname=''
        self.lines={}

        # self.imageLabel = QLabel()
        # self.imageLabel.setBackgroundRole(QPalette.Base)
        # self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        # self.imageLabel.setScaledContents(True)
        self.editcoordinates= False
        # self.editPoints=False
        # self.notdone_setting=True
        self.iscoordinatesSet=False
        self.lineeditingdone=True
        self.allsaved=True
        self.linename=''
        

        self.viewer = QtImageViewer()
        
        self.coordsettingwdgt=CoordinateSetting(self)

        self.listWidget = myListWidget()
        # self.listWidget.resize(300,150)
        self.listWidget.setFixedWidth(150)
        self.coordsettingwdgt.setFixedWidth(150)

        self.lineWidget=DigitizedLine(self)
        # self.lineWidget.setFixedWidth(250)

        wgtslayout=QVBoxLayout()
        wgtswidget=QWidget()
        wgtslayout.addWidget(self.coordsettingwdgt)
        wgtslayout.addWidget(self.lineWidget)       
        wgtslayout.addWidget(self.listWidget)    

        self.exportbtn = QPushButton("Export")

        self.exportbtn.clicked.connect(self.exportXls)
        # self.changebtn.setFixedHeight(40)
        # self.changebtn.setStyleSheet("""QPushButton {    
        # border-radius: 5px;    
        # text-align: center;
        # border: 2px solid #8f8f91;
        # border-radius: 6px;
        # background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #f6f7fa, stop: 1 #dadbde);
        # min-width: 40px;        }        """)


        wgtslayout.addWidget(self.exportbtn)    
        wgtswidget.setLayout(wgtslayout)
        wgtswidget.setFixedWidth(210)

        hlayout=QHBoxLayout()
        hwidget=QWidget()
        hlayout.addWidget(self.viewer)
        hlayout.addWidget(wgtswidget)
        hwidget.setLayout(hlayout)

        self.setCentralWidget(hwidget)

        self.createActions()
        self.createMenus()

        self.setWindowTitle("Image Viewer")
        self.resize(800, 600)

        # self.mydialog=CustomDialog()

        self.video_label = QLabel()
        self.video_label.setStyleSheet("background-color: green; border: 1px solid black")
        # self.editlines.setEnabled(False)
        self.label_position = QLabel(
            self.video_label, alignment=Qt.AlignCenter
        )
        self.label_position.setStyleSheet('background-color: white; border: 1px solid black')
        self.listWidget.itemClicked.connect(self.listitemClicked)
    def listitemClicked(self,item):
        line=self.lineWidget.getLine()
        if len(line)>0:
            self.lines[self.linename]=line
        self.lineWidget.clearAll()
        # print('prevline ',self.linename,self.lines)
        # if len(self.linename)>0:

            # print('in listitemClicked prevline',self.linename)
            # for line in self.lines:
            #     for p in self.lines[line]:
            #         print('        ',p)
       
        if item.text() in self.lines:
            self.linename=item.text()
            self.lineWidget.setLine(self.lines[self.linename])
            

            # self.lines[self.linename]=[]
        # print('present ',item.text(),self.lines[self.linename])

            # print('in listitemClicked present line',self.linename)
            # for p in self.lines[self.linename]:
            #     print('        ',p)
            #     mstr+='P{}: ({},{}) \n'.format(i+1,int(point.x()),int(point.x()))
            # QMessageBox.information(self, "ListWidget", "You clicked: "+item.text()+'\n'+mstr)
        # else:
        #     QMessageBox.information(self, "ListWidget", "You clicked: "+item.text())
    
    def setcoordinatesEditable(self,mbool):
        # self.editcoordinates=mbool
        self. editCoordsAct.setEnabled(mbool)
        self.iscoordinatesSet=False
        print('self.iscoordinatesSet,self.editcoordinates in setcoordinatesEditable',self.iscoordinatesSet,self.editcoordinates)
    def open_project(self):
        options = QFileDialog.Options()
        self.listWidget.clear()
        # self.fileName = QFileDialog.getOpenFileName(self, "Open File", QDir.currentPath())
        self.projectname, _ = QFileDialog.getOpenFileName(self, 'QFileDialog.getOpenFileName()', '', 
                                                  'PlotDigi file (*.pd )') #, options=options
        print(self.projectname)
        if self.projectname:
            file = open(self.projectname,'r')
            text=file.read().split('\n')
            # print(text)
            impath=text[0]
            coordspath=text[1]
            linespath=''
            if len(text)>=3:
                linespath=text[2]
            self.open(filename=impath)
            if len(coordspath)>2:                
                self.coordsettingwdgt.loadCoords(coordspath)
                # self.coordinates=self.coordsettingwdgt.getCoordinates()
                self.iscoordinatesSet=True
                self.editCoordsAct.setEnabled(False)
                self.createlineAct.setEnabled(True)
            if len(linespath)>2:
                linesfile=self.projectname.replace('.pd','') +'/lines.npy'
                self.lines=np.load(linesfile,allow_pickle=True).item()
                # print('self.lines ',self.lines)
                for self.linename in self.lines.keys():
                    self.listWidget.addItem(self.linename)
                    print(self.linename)
                    for name,scenePos in self.lines[self.linename]:
                        print('   ',name,scenePos)
                        self.display_label(scenePos)
            # file.close()
            # image = QImage(self.fileName)
            # if image.isNull():
            #     QMessageBox.information(self, "Image Viewer", "Cannot load %s." % self.fileName)
            #     return
                                        #    PJ-038-1006_00051270-1 
    def open(self,filename=''):
        options = QFileDialog.Options()
        # self.fileName = QFileDialog.getOpenFileName(self, "Open File", QDir.currentPath())
        if filename:
            self.fileName=filename
        else:
            self.fileName, _ = QFileDialog.getOpenFileName(self, 'QFileDialog.getOpenFileName()', 'D:\Ameyem\Bhugarbho\JOGMEC\ShotpointMap//',
                                                  'Images (*.png *.jpeg *.jpg *.bmp *.gif *.tif)', options=options)
        if self.fileName:
            image = QImage(self.fileName)
            if image.isNull():
                QMessageBox.information(self, "Image Viewer", "Cannot load %s." % self.fileName)
                return

            # self.imageLabel.setPixmap(QPixmap.fromImage(image))
            self.viewer.setImage(image)

            self.viewer.aspectRatioMode = Qt.KeepAspectRatio

            self.viewer.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.viewer.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            
            # Allow zooming with right mouse button.
            # Drag for zoom box, doubleclick to view full image.
            self.viewer.canZoom = True
            
            # Allow panning with left mouse button.
            self.viewer.canPan = True


            self.scaleFactor = 1.0

            self.viewer.leftMouseButtonPressed.connect(self.handleLeftClick)
            self.viewer.middleMouseButtonPressed.connect(self.handleMiddleClick)

            # self.scrollArea.setVisible(True)
            # self.printAct.setEnabled(True)
            self.fitToWindowAct.setEnabled(True)
            self.updateActions()

            # if not self.fitToWindowAct.isChecked():
            #     self.imageLabel.adjustSize()
    def exportXls(self):
        if self.iscoordinatesSet & (len(self.lines)>0):
            coordinates=self.coordsettingwdgt.getCoordinates()  
            converter=CoordConverter(coordinates,self.lines)
            df=converter.getLineCoords()
            excel_filename,_ = QFileDialog.getSaveFileName(self, 'Save File','','Xls file (*.xlsx )')
            df[['lno','shotpoint','X-Coord','Y-Coord']].to_excel(excel_filename)
            displayMessageBox('Successfully Exported to \n'+excel_filename)
            return 1
        else:
            displayMessageBox('No proper data to be converted and exported')
            return 0
            
        
    def save(self):
        text = self.fileName +'\n'
        # print('self.linename in save ',self.linename)
        # self.print()
        # # self.lines[self.linename]=self.lineWidget.getLine()
        # print('self.linename in save after',self.linename)
        # self.print()
        if self.iscoordinatesSet:
            coordinates=self.coordsettingwdgt.getCoordinates()               
            coordfile=self.projectname.replace('.pd','') +'/coordinates.npy'
            np.save(coordfile,coordinates)     
             
            text=text+ coordfile+'\n' 
        else:
            displayMessageBox('Please set coordinates first')
        if len(self.lines)>0:
            linesfile=self.projectname.replace('.pd','') +'/lines.npy'
            np.save(linesfile,self.lines) 
            text=text+ linesfile+'\n'

        file = open(self.projectname.replace('.pd','')+'.pd' ,'w')
        file.write(text)
        file.close()
        self.allsaved=True
        displayMessageBox('Your project is saved..')  

    def file_save_as(self):
        import os
        self.projectname = QFileDialog.getSaveFileName(self, 'Save File','D:\Ameyem\Bhugarbho\JOGMEC\ShotpointMap//','PlotDigi file (*.pd )')
        self.projectname=self.projectname[0]
        try:
            os.makedirs(self.projectname.replace('.pd','')  )
        except:
            displayMessageBox('Project already exist give different name')
            return self.file_save_as()
        self.save()
       
        # text = self.fileName +'\n'
        # if self.iscoordinatesSet:
        #     coordinates=self.coordsettingwdgt.getCoordinates()
        #     print(coordinates)
            
        #     coordfile=self.projectname +'/coordinates.npy'
        #     # coordfile='./coordinates.npy'
        #     np.save(coordfile,coordinates)            
        #     text=text+ coordfile+'\n'

        # file = open(self.projectname.replace('.pd','')+'.pd' ,'w')
        # file.write(text)
        # file.close()
    def file_save(self):
        import os
        if not self.projectname:
            self.file_save_as()
            return 0
        if len(self.projectname)<2:
            self.file_save_as()
        else:
            self.save()
            
    def print_(self):
        dialog = QPrintDialog(self.printer, self)
        if dialog.exec_():
            painter = QPainter(self.printer)
            rect = painter.viewport()
            size = self.imageLabel.pixmap().size()
            size.scale(rect.size(), Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(self.imageLabel.pixmap().rect())
            painter.drawPixmap(0, 0, self.imageLabel.pixmap())

    def zoomIn(self):
        self.scaleImage(1.25)

    def zoomOut(self):
        self.scaleImage(0.8)

    def normalSize(self):
        # self.imageLabel.adjustSize()
        self.scaleFactor = 1.0

    def fitToWindow(self):
        self.viewer.myfitInView( scale=True)
        # fitToWindow = self.fitToWindowAct.isChecked()
        # self.scrollArea.setWidgetResizable(fitToWindow)
        # if not fitToWindow:
        #     self.normalSize()

        # self.updateActions()

    def about(self):
        QMessageBox.about(self, "About Image Viewer",
                          "<p>The <b>Image Viewer</b> example shows how to combine "
                          "QLabel and QScrollArea to display an image. QLabel is "
                          "typically used for displaying text, but it can also display "
                          "an image. QScrollArea provides a scrolling view around "
                          "another widget. If the child widget exceeds the size of the "
                          "frame, QScrollArea automatically provides scroll bars.</p>"
                          "<p>The example demonstrates how QLabel's ability to scale "
                          "its contents (QLabel.scaledContents), and QScrollArea's "
                          "ability to automatically resize its contents "
                          "(QScrollArea.widgetResizable), can be used to implement "
                          "zooming and scaling features.</p>"
                          "<p>In addition the example shows how to use QPainter to "
                          "print an image.</p>")
    

    def createActions(self):
        self.openProjectAct = QAction("&OpenProject...", self, shortcut="Ctrl+P", triggered=self.open_project)
        self.openAct = QAction("&Open...", self, shortcut="Ctrl+O", triggered=self.open)
        
        self.saveAct = QAction("&Save...", self, shortcut="Ctrl+S", triggered=self.file_save)
        self.saveasAct = QAction("&Save As...", self, shortcut="Ctrl+A", triggered=self.file_save_as)
        self.printAct = QAction("&Print...", self, shortcut="Ctrl+P", enabled=False, triggered=self.print_)
        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q", triggered=self.close)
        self.zoomInAct = QAction("Zoom &In (25%)", self, shortcut="Ctrl++", enabled=False, triggered=self.zoomIn)
        self.zoomOutAct = QAction("Zoom &Out (25%)", self, shortcut="Ctrl+-", enabled=False, triggered=self.zoomOut)
        self.normalSizeAct = QAction("&Normal Size", self, shortcut="Ctrl+N", enabled=False, triggered=self.normalSize)
        self.fitToWindowAct = QAction("&Fit to Window", self, enabled=False, checkable=True, shortcut="Ctrl+F",
                                      triggered=self.fitToWindow)
        self.aboutAct = QAction("&About", self, triggered=self.about)
        self.aboutQtAct = QAction("About &Qt", self, triggered=qApp.aboutQt)

        self.editCoordsAct =QAction("&Enter Coords", self,enabled=False, checkable=True, shortcut="Ctrl+E", triggered=self.editCoords )
        self.createlineAct =QAction("&Edit Line", self,enabled=False, checkable=True, shortcut="Ctrl+L", triggered=self.createLine )
        self.editPointsAct =QAction("&Enter Points", self,enabled=False, checkable=True, shortcut="Ctrl+T", triggered=self.editPoints )

    def createMenus(self):
        self.fileMenu = QMenu("&File", self)
        self.fileMenu.addAction(self.openProjectAct)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addAction(self.saveasAct)
        self.fileMenu.addAction(self.printAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.editMenu = QMenu("&Edit", self)
        self.editMenu.addAction(self.editPointsAct)
        self.editMenu.addAction(self.editCoordsAct)
        self.editMenu.addAction(self.createlineAct)
        self.viewMenu = QMenu("&View", self)
        self.viewMenu.addAction(self.zoomInAct)
        self.viewMenu.addAction(self.zoomOutAct)
        self.viewMenu.addAction(self.normalSizeAct)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.fitToWindowAct)

        

        self.editMenu.addSeparator()
        self.viewMenu.addAction(self.fitToWindowAct)

        self.helpMenu = QMenu("&Help", self)
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.editMenu)
        self.menuBar().addMenu(self.viewMenu)
        self.menuBar().addMenu(self.helpMenu)

    def updateActions(self):
        self.zoomInAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.zoomOutAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.normalSizeAct.setEnabled(not self.fitToWindowAct.isChecked())
        self. editCoordsAct.setEnabled(True)
        self. editPointsAct.setEnabled(True)

    def scaleImage(self, factor):
        self.scaleFactor *= factor
        # self.imageLabel.resize(self.scaleFactor * self.imageLabel.pixmap().size())

        self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)

        self.zoomInAct.setEnabled(self.scaleFactor < 3.0)
        self.zoomOutAct.setEnabled(self.scaleFactor > 0.333)

    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value()
                               + ((factor - 1) * scrollBar.pageStep() / 2)))


    def display_label(self, pos):
        pen = QPen(QColor(Qt.yellow))
        delta = QtCore.QPoint(30, -15)
        size=25
        self.label_position = QGraphicsSimpleTextItem("(%d, %d)" % (pos.x(), pos.y()))
        self.label_position.setFont(QFont("Arial",size))
        self.viewer.scene.addItem(self.label_position)

        self.label_position.setPos(int(pos.x()), int(pos.y()))
        x,y,w,h=pos.x()-10, pos.y()-10,20,20
        ellipse=QGraphicsEllipseItem(x, y, w, h)
        # ellipse.setPos(x, y)

        # ellipse1.translate(-50, -5)

        self.viewer.scene.addItem(ellipse)
    def editCoords(self):
        if not self.iscoordinatesSet:
            self.editcoordinates= not self.editcoordinates
            cursor = Qt.CrossCursor
            self.viewer.setCursor(cursor)
            self.allsaved=False
    def editPoints(self):
        if len(self.linename)>0:
        # if not self.iscoordinatesSet:
            # self.editPoints= not self.editPoints
            self.lineeditingdone=False
            self.editlines=True
            cursor = Qt.CrossCursor
            self.viewer.setCursor(cursor)
            self.allsaved=False
        else:
            displayMessageBox('First create a line')
    def print(self):
        print('in print ',self.linename)
        for line in self.lines:
            print(line)
            for p in self.lines[line]:
                print('        ',p)
    def createLine(self):
        if len(self.linename)>0:
            self.lines[self.linename]=self.lineWidget.getLine()

        namedlg=getNameDialog()
        self.linename=namedlg.getName()
        
        self.lines[self.linename]=[]
        # print('in createLine after',self.linename)
        self.listWidget.addItem(self.linename)
        # self.editlines= not self.editlines
        self.editlines=True
        cursor = Qt.CrossCursor
        self.viewer.setCursor(cursor)
        self.lineeditingdone=False
        self.allsaved=False
        self.lineWidget.clearAll()

    def handleLeftClick(self, x, y):
        print('self.iscoordinatesSet,self.editcoordinates in handleLeftClick',self.iscoordinatesSet,self.editcoordinates)
        if not self.iscoordinatesSet:
            if self.editcoordinates:
                # coorddict=self.mydialog.getResults()
                # print('self.mydialog.getResults()',coorddict)
                row = int(x)
                column = int(y)
                # print("Pixel (row="+str(row)+", column="+str(column)+")")

                scenePos = self.viewer.mapToScene(QtCore.QPoint(row, column))
                self.iscoordinatesSet=  not self.coordsettingwdgt.setPixelCoords(scenePos)
                if self.iscoordinatesSet: self. createlineAct.setEnabled(True)
                # print("scenePos handleLeftClick self.iscoordinatesSet",scenePos,self.iscoordinatesSet)
                # pos= QtCore.QPoint(int(scenePos.x()), int(scenePos.y()))
                self.display_label(scenePos)
                self.editcoordinates= not self.editcoordinates
                cursor = Qt.ArrowCursor
                self.viewer.setCursor(cursor)
        elif not self.lineeditingdone:
            if self.editlines:
                row = int(x)
                column = int(y)
                scenePos = self.viewer.mapToScene(QtCore.QPoint(row, column))
                self.lines[self.linename].append(('',scenePos))
                self.lineWidget.addRow('',scenePos)
                self.display_label(scenePos)
                # self.editcoordinates= not self.editcoordinates
                
                # print(self.lines[self.linename])
        else:
            
            None

    def handleMiddleClick(self, x, y):        
        self.lineeditingdone=True
        cursor = Qt.ArrowCursor
        self.viewer.setCursor(cursor)
        # print(self.lines)
        # print('mid click')
        
    def closeEvent(self, event):
        if not self.allsaved:
            quit_msg = "Your changes will not be saved? Do you still want to exit"
            reply = QMessageBox.question(self, 'Message', 
                            quit_msg, QMessageBox.Yes, QMessageBox.No)
        else:
            quit_msg = "Do you want to exit Digitizer?"
            reply = QMessageBox.question(self, 'Message', 
                            quit_msg, QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    imageViewer = PlotDigitizer()
    imageViewer.show()
    sys.exit(app.exec_())
    # TODO QScrollArea support mouse
    # base on https://github.com/baoboa/pyqt5/blob/master/examples/widgets/imageviewer.py
