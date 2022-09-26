#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import *
from PyQt5 import QtCore
# from PyQt5.QtGui import QImage, QPixmap, QPalette, QPainter,QPen,QColor
# from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
# from PyQt5.QtWidgets import QLabel, QSizePolicy, QScrollArea, QMessageBox, QMainWindow, QMenu, QAction, \
#     qApp, QFileDialog, QGraphicsSimpleTextItem,QGraphicsEllipseItem
import random
from coordinatesetting import *
from coord_converter import *
from PyQt5.QtGui import *
from PyQt5.QtPrintSupport import *
from PyQt5.QtWidgets import*
import time
from QtImageViewer import QtImageViewer
import numpy as np
point_deviation=-10
point_width=20
def MyInt(v):
    try:     return int(v)
    except:  return 0
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
        # self.parent=parent
    def mySetWidget(self,widget):
        self.scroll.setWidget(widget)


# class GraphicsPathItem(QGraphicsPathItem):
#     # def mousePressEvent(self, event):
#     #     super().mousePressEvent(event)
#     #     print("Local position:", event.pos())
#     #     print("Scene position:", event.scenePos())

#     def setPath(self,path):
#         if self.path() == QPainterPath():
#             return self.path()
#         pen = self.pen()
#         ps = QPainterPathStroker()
#         ps.setCapStyle(pen.capStyle())
#         width = 2 * max(0.00000001, pen.widthF())
#         ps.setWidth(width)
#         ps.setJoinStyle(pen.joinStyle())
#         ps.setMiterLimit(pen.miterLimit())
#         return ps.createStroke(path)

class myListWidget(QListWidget):

   def Clicked(self,item):
      QMessageBox.information(self, "ListWidget", "You clicked: "+item.text())

class ClickableGraphicsPathItem(QGraphicsPathItem):
    def __init__(self, path, pen,name,parent=None):
        super(ClickableGraphicsPathItem, self).__init__(path,None)
        self.setPen(pen)
        self.name=name
        self.parent=parent
        self.color_green=False
        self.type='line'
        # flags can be set all at once using the "|" binary operator
        self.setFlags(self.ItemIsSelectable) #|self.ItemIsMovable

    def mousePressEvent(self, event):
        super(ClickableGraphicsPathItem, self).mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            print(self.name,'item clicked!')   

            if not self.color_green: self.selectItem()
            else: self.deselectItem()
            self.parent.onLineSelect(self.name)
            
        elif event.button() == Qt.RightButton:
            self.setPen(QPen(QColor(Qt.transparent), 10))

    def selectItem(self):
        # if not self.color_green:        
        self.setPen(QPen(QColor("green"), 20))
        self.color_green=True
        # else:
        #     self.setPen(QPen(QColor("red"), 8))
        #     self.color_green=False
    def deselectItem(self):
        self.setPen(QPen(QColor("red"), 8))
        self.color_green=False
class ClickableQGraphicsSimpleTextItem(QGraphicsSimpleTextItem):
    # self.label_position = QGraphicsSimpleTextItem("(%d, %d)" % (pos.x(), pos.y()))
    def __init__(self, name_point):
        pos=name_point[1]
        self.type='text'
        name="SP: %s \n"%name_point[0]
        name+="(%d, %d)" % (pos.x(), pos.y())
        super(QGraphicsSimpleTextItem, self).__init__(name,None)
        size=25
        self.setFont(QFont("Arial",size)) 
        # self.setFlags(self.ItemIsSelectable|self.ItemIsMovable)
        
    # def mousePressEvent(self, event):
    #     super(QGraphicsSimpleTextItem, self).mousePressEvent(event)
    #     if event.button() == Qt.LeftButton:
    #         print('item clicked!')  

class ClickableQGraphicsEllipseItem(QGraphicsEllipseItem):
    changePos = pyqtSignal(QPointF)
    # self.label_position = QGraphicsSimpleTextItem("(%d, %d)" % (pos.x(), pos.y()))
    def __init__(self, name_point,name='',parent=None):
        pos=name_point[1]
        x,y,w,h=pos.x()+point_deviation, pos.y()+point_deviation,point_width,point_width
        super(QGraphicsEllipseItem, self).__init__(x, y, w, h,None)
        self.label_position = ClickableQGraphicsSimpleTextItem(name_point) 
        self.label_position.setPos(pos.x(), pos.y())
        self.type='point'
        # self.text = QGraphicsTextItem('hello')
        # self.text.setTextInteractionFlags(Qt.TextEditorInteraction)

        # self.text.setPos(pos.x(), pos.y()-100)
        self.shotPointNumber=MyInt(name_point[0])

        # self.parent.scene.addItem(self.text)

        self.parent=parent
        self.origx=pos.x() 
        self.origy=pos.y()
        self.name=name
        self.parent.scene.addItem(self.label_position)
        # self.parent.scene.addItem(self.text)
        self.setFlags(self.ItemIsSelectable|self.ItemIsMovable)
        self.initial_pos=(self.pos().x(), self.pos().y())


    def getSPfromdialog(self):
        text, ok = QInputDialog.getText(self.parent.parent, 'Text Input Dialog', 'Enter Shotpoint:')
        if ok:
            return text
        else:
            return ''

    
      
    def mousePressEvent(self, event):
        super(QGraphicsEllipseItem, self).mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            print('item clicked!', self.pos().x(), self.pos().y())    
            self.initial_pos=(self.pos().x(), self.pos().y())
    def mouseDoubleClickEvent(self, event):
        super(QGraphicsEllipseItem, self).mouseDoubleClickEvent(event)
        if event.button() == Qt.LeftButton:
            self.editShotPointnumber()
    def editShotPointnumber(self):
        text=self.getSPfromdialog()
        self.shotPointNumber=MyInt(text)
        self.updateTextLabel()
        self.parent.handleShotpointchange(self.shotPointNumber,self.name)    
        return 0    

    def mouseReleaseEvent(self, event):
        super(QGraphicsEllipseItem, self).mouseReleaseEvent(event)
        # self.scene().itemReleased.emit(self)
        if event.button() == Qt.LeftButton:
            difpoint=QPointF()
            difpoint.setX(-self.initial_pos[0]+self.pos().x())
            difpoint.setY(-self.initial_pos[1]+self.pos().y())
            absdiff=abs(difpoint.x())+abs(difpoint.y())

            print('absdiff ',absdiff)
            if absdiff>1:
                self.parent.handleEllipseItemRelased(difpoint,self.name)
            # self.origx
            print('item release!',self.name, difpoint.x(), difpoint.y()) 
            # print(dir(self.pos()))
            # self.pos().setX(0)
            # self.pos().setY(0)
            # print('pos changed!',self.name, self.pos().x(), self.pos().y())  
    def mymoveTo(self,pos):        
        self.origx=pos[0]
        self.origy=pos[1]
        self.updateTextLabel()
    def updateTextLabel(self):
        name="SP: %d \n" % self.shotPointNumber+"(%d, %d)" % (int(self.origx), int(self.origy))
        self.label_position.setText(name)
        self.label_position.setPos(int(self.origx), int(self.origy))
    def getRemoved(self):
        self.parent.scene.removeItem(self.label_position)
        self.parent.scene.removeItem(self)

 

# def display_line(points,name):
#     path = QPainterPath()
#     if len(points)>1:
#         p=points[0]
#         path.moveTo(p.x(), p.y())
#         for p in points:
#             path.lineTo(p.x(), p.y())
#         # path_item = QGraphicsPathItem(path, None)
#         path_item = ClickableGraphicsPathItem(path, QPen(QColor("red"), 8),name)        
#         return path_item
        
class LineWdget(EmptyLinewidget):
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
        self.parent=parent
    def ondelete(self,indx):
        print(indx,self.parent)
        self.parent.ondelete(indx-1)
    
    def addRow(self,name,pixcoords):
        row = NmaeInputRow4Pixel(self.coordlayout.count()+1,pixcoords,name,parent=self)
        self.line.append([name,pixcoords])
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
            row = NmaeInputRow4Pixel(coordfor+1,pixcoords,name,parent=self)
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
class LineItem:
    def __init__(self,name,scene,parent=None):
        # super().__init__(parent)
        self.labels=[]
        self.circles=[]
        self.line=[]
        self.scene=scene
        self.name=name
        self.parent=parent
        self.path = QPainterPath()
        self.path_item = ClickableGraphicsPathItem(self.path, QPen(QColor("red"), 8),name,parent=self.parent)
        self.scene.addItem(self.path_item)
    def append(self,name_point):
        self.line.append([name_point[0],name_point[1]])
        p=name_point[1]
        self.display_Point(name_point,name=str(len(self.line)) )      

        if len(self.line)>1:
            self.path.lineTo(p.x(), p.y())
        else:
            self.path.moveTo(p.x(), p.y())
        self.path_item.setPath(self.path)
    def appendonNew(self,name_point):
        self.append(name_point)
        self.circles[-1].editShotPointnumber()
        return 0
        # text=self.getSPfromdialog()
        # self.shotPointNumber=int(text)
        # # print('self.shotPointNumber ',self.shotPointNumber)
        # self.updateTextLabel()
        # self.parent.handleShotpointchange(self.shotPointNumber,self.name)

    def display_Point(self, name_point,name=''):
        pen = QPen(QColor(Qt.yellow))
                    
        # self.scene.addItem(label_position)
        # self.labels.append(label_position)

        ellipse=ClickableQGraphicsEllipseItem(name_point,name=name,parent=self)        
        self.scene.addItem(ellipse)
        self.circles.append(ellipse)

    def handleEllipseItemRelased(self,pos,name):       
        for i,point in enumerate(self.circles):
            if point.name == name:
                idx=i 
                break
        posx,posy=self.circles[idx].pos().x(),self.circles[idx].pos().y()       
        newposx,newposy=self.circles[idx].origx+pos.x(),self.circles[idx].origy+pos.y()
        
        self.circles[idx].mymoveTo([newposx,newposy])
        # print('position of circle acc originals',newposx,newposy)
        # self.labels[idx].setPos(int(newposx), int(newposy))
        # name="(%d, %d)" % (int(newposx), int(newposy))
        # self.labels[idx].setText(name)
        self.onPointPositionChange([newposx,newposy],pointindx=idx)
    def handleShotpointchange(self,shotpointnumber,name):       
        for i,point in enumerate(self.circles):
            if point.name == name:
                idx=i 
                break
        
        if idx<len(self.line):
            print(self.line[idx])
            self.line[idx][0]=str(shotpointnumber)
            self.parent.handlePointPositionChange(self.name)
        else:
            print('error idx > line length',idx,len(self.line))
        return 0

    def onPointPositionChange(self,newpos,pointindx=0):
        # print('*********vs*********** \n*********vs***********\n', self.line)
        if len(self.line)>pointindx:
            self.line[pointindx][1].setX(newpos[0])
            self.line[pointindx][1].setY(newpos[1])
            # print('*********vs*********** \n*********vs***********\n', self.line)
            self.reDraw()
            self.parent.handlePointPositionChange(self.name)

    def reDraw(self):
        self.path = QPainterPath()
        if len(self.line)>=1:
            p=self.line[0][1]
            self.path.moveTo(p.x(), p.y())
            for n,p in self.line:
                self.path.lineTo(p.x(), p.y())
        self.path_item.setPath(self.path)
        return self.line

    def ondelete(self,indx):
        del self.line[indx]
        self.circles[indx].getRemoved()
        # self.scene.removeItem(self.circles[indx])
        # self.scene.removeItem(self.labels[indx])
        del self.circles[indx]
        # del self.labels[indx]
           
        return self.reDraw()
    def getLine(self):
        return self.line
    def setLine(self,line):
        self.line=line
        self.reDraw()
        print('redrawn')
    

class PlotDigitizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.linename=''
        self.printer = QPrinter()
        self.scaleFactor = 0.0
        self.projectname=''
        self.lines={}
        self.labels=[]
        self.circles=[]
        self.displayedlabel=False
        self.prevtime=time.time()

        self.editcoordinates= False
        # self.editPoints=False
        # self.notdone_setting=True
        self.iscoordinatesSet=False
        self.lineeditingdone=True
        self.allsaved=True
        self.linename=''     
        self.isnewline=False  
        self.editlines=False
        self.viewer = QtImageViewer()        
        self.coordsettingwdgt=CoordinateSetting(self)
        self.listWidget = myListWidget()
        # self.listWidget.resize(300,150)
        self.listWidget.setFixedWidth(250)
        self.coordsettingwdgt.setFixedWidth(250)

        self.lineWidget=LineWdget(self)
        # self.lineWidget.setFixedWidth(250)

        wgtslayout=QVBoxLayout()
        wgtswidget=QWidget()
        wgtslayout.addWidget(self.coordsettingwdgt)
        wgtslayout.addWidget(self.lineWidget)       
        wgtslayout.addWidget(self.listWidget)    

        self.exportbtn = QPushButton("Export")
        self.exportbtn.clicked.connect(self.exportXls)


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
        self._createToolBars()
        self.statusBar().showMessage('Message in statusbar.')

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
        self.listWidget.itemDoubleClicked.connect(self.listitemDoubleClicked)
    
    # def display_label_new(self, pos):
    #     pen = QPen(QColor(Qt.yellow))
    #     size=25
    #     label_position = ClickableQGraphicsSimpleTextItem(pos)
    #     self.viewer.scene.addItem(label_position)
    #     self.labels.append(label_position)
    #     x,y,w,h=pos.x()-10, pos.y()-10,20,20
    #     ellipse=ClickableQGraphicsEllipseItem(pos,name=str(random.randint(0,90)),parent=self.viewer)        
    #     self.viewer.scene.addItem(ellipse)
    #     self.circles.append(ellipse)
    def display_label(self, pos):
        pen = QPen(QColor(Qt.yellow))
        delta = QtCore.QPoint(30, -15)
        size=25
        self.label_position = QGraphicsSimpleTextItem("(%d, %d)" % (pos.x(), pos.y()))
        self.label_position.setFont(QFont("Arial",size))
        self.viewer.scene.addItem(self.label_position)
        self.label_position.setPos(int(pos.x()), int(pos.y()))
        x,y,w,h=pos.x()+point_deviation, pos.y()+point_deviation,point_width,point_width
        ellipse=QGraphicsEllipseItem(x, y, w, h)
        self.displayedlabel=True
        # ellipse.setPos(x, y)

        # ellipse1.translate(-50, -5)

        self.viewer.scene.addItem(ellipse)
    def sortLineNomessage(self):
        sps=np.array([MyInt(p[0]) for p in self.lines[self.linename]])
        sortindxs=np.argsort(sps)
        newline=[]
        for i in sortindxs:
            if sps[i]!=0:
                newline.append(self.lines[self.linename][i])
        self.lineWidget.setLine(newline)
        self.lines[self.linename]=newline
        self.lineitems[self.linename].setLine(newline)
    def sortLine(self):
        reply = QMessageBox.question(self, 'Message', 
                            'Do you want to sort line? \n'+self.linename, QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            print('yes')
            self.sortLineNomessage()

        else:
            print('no')

    def listitemDoubleClicked(self,item):
        self.sortLine()
        # reply = QMessageBox.question(self, 'Message', 
        #                     'Do you want to sort line? \n'+self.linename, QMessageBox.Yes, QMessageBox.No)

        # if reply == QMessageBox.Yes:
        #     print('yes')
        #     sps=np.array([MyInt(p[0]) for p in self.lines[self.linename]])
        #     sortindxs=np.argsort(sps)
        #     newline=[]self.viewer.scene.items()
        #     for i in sortindxs:
        #         if sps[i]!=0:
        #             newline.append(self.lines[self.linename][i])
        #     self.lineWidget.setLine(newline)
        #     self.lines[self.linename]=newline
        #     self.lineitems[self.linename].setLine(newline)

        # else:
        #     print('no')

    def listitemClicked(self,item):
        line=self.lineWidget.getLine()
        if len(line)>0:
            self.lines[self.linename]=line
        self.lineWidget.clearAll()      
        if item.text() in self.lines:
            self.linename=item.text()
            self.lineWidget.setLine(self.lines[self.linename])
        for sitem in self.viewer.scene.items():
            # if sitem is not self.viewer._pixmapHandle:
            if hasattr(sitem, 'name'):
                # print(sitem.name,self.linename)
                if sitem.type=='line':
                    if sitem.name==self.linename:
                        sitem.selectItem()
                    else:
                        sitem.deselectItem()
                    # break          
        self.statusBar().showMessage('The selected line is: '+self.linename)
    
    def onLineSelect(self,name):
        self.linename=name          
        if self.linename:
            self.statusBar().showMessage('The selected line is: '+self.linename)
        else:
            self.statusBar().showMessage('The selected line is: None')
        # print('self.lineitems.keys() ',list(self.lineitems.keys()))
        idx=np.where(np.array(list(self.lineitems.keys()))==self.linename)[0][0]
        # print(idx)
        self.listWidget.setCurrentRow(idx)
        self.lineWidget.clearAll()
        self.lineWidget.setLine(self.lines[self.linename])
    
    def setcoordinatesEditable(self,mbool):
        # self.editcoordinates=mbool
        self. editCoordsAct.setEnabled(mbool)
        self.iscoordinatesSet=False
        # print('self.iscoordinatesSet,self.editcoordinates in setcoordinatesEditable',self.iscoordinatesSet,self.editcoordinates)
    def ondelete(self,indx):
        print(len(self.lines[self.linename]),self.linename,indx)
        # print(self.lines[self.linename])
        # del self.lines[self.linename][indx]      
        self.lines[self.linename]=self.lineitems[self.linename].ondelete(indx)
        
        self.lineWidget.clearAll()
        self.lineWidget.setLine(self.lines[self.linename])
        # print(self.lines[self.linename])
    
    def clearAll(self):
        for item in self.viewer.scene.items():
            if item is not self.viewer._pixmapHandle:
                self.viewer.scene.removeItem(item)
        self.linename=''

        self.scaleFactor = 0.0
        self.projectname=''
        self.lines={}
        self.lineitems={}
        self.editcoordinates= False
        self.iscoordinatesSet=False
        self.lineeditingdone=True
        self.allsaved=True
        self.linename=''
        self.coordsettingwdgt.clearAll()
        self.lineWidget.clearAll()
        self.listWidget.clear()
    def createLine(self):
        if  len(self.linename)>0:
            self.lines[self.linename]=self.lineWidget.getLine()

        namedlg=getNameDialog()
        try:
            self.linename=namedlg.getName()
            if len(self.linename)>0:
                self.lines[self.linename]=[]
                self.lineitems[self.linename]=LineItem(self.linename,self.viewer.scene,parent=self)
                # print('in createLine after',self.linename)
                self.listWidget.addItem(self.linename)
                # self.editlines= not self.editlines
                # self.editlines=True
                self.isnewline=True
                cursor = Qt.CrossCursor
                self.viewer.setCursor(cursor)
                self.lineeditingdone=False
                self.allsaved=False
                self.lineWidget.clearAll()
        except:
            self.linename=''
            None
    def handlePointPositionChange(self,linename):
        if linename==self.linename:
            self.lineWidget.clearAll()      
            line=self.lineitems[self.linename].getLine()
            self.lineWidget.setLine(line)
            self.lines[self.linename]=line
        if self.editlines:
            self.setCrossCursor()
        return 0


    def handleLeftClick(self, x, y):
        # print('self.iscoordinatesSet,self.editcoordinates in handleLeftClick',self.iscoordinatesSet,self.editcoordinates)
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
            if self.editlines | self.isnewline:
                self.time=time.time()
                # if displayedlabel:
                timediff=self.time-self.prevtime
                print('timediff ',timediff)
                if timediff>4:
                    row = int(x)
                    column = int(y)
                    scenePos = self.viewer.mapToScene(QtCore.QPoint(row, column))
                    # self.lines[self.linename].append(['',scenePos])
                    self.lineitems[self.linename].appendonNew(['',scenePos])
                    self.lines[self.linename]=self.lineitems[self.linename].getLine()
                    # self.lineWidget.addRow('',scenePos)
                self.prevtime=self.time

                if self.editlines:
                    self.sortLineNomessage()
                # self.viewer.scene.addItem(path_item)
                self.editlines= False
                if not self.isnewline:
                    self.setArrowCursor()
                

        else:
            
            None
    def setArrowCursor(self):
        cursor = Qt.ArrowCursor
        self.viewer.setCursor(cursor)
    def handleMiddleClick(self, x, y):        
        self.lineeditingdone=True
        self.setArrowCursor()
        self.isnewline=False
        # print('mid click')
        
    def open_project(self):
        self.clearAll()
        options = QFileDialog.Options()
        
        self.projectname, _ = QFileDialog.getOpenFileName(self, 'QFileDialog.getOpenFileName()', 'D:\Ameyem\Bhugarbho\JOGMEC\ShotpointMap//', 
                                                  'PlotDigi file (*.pd )') #, options=options

        # self.projectname='D:/Ameyem/Bhugarbho/JOGMEC/ShotpointMap/Vietnam/North.pd'
        print(self.projectname)
        if self.projectname:
            file = open(self.projectname,'r')
            text=file.read().split('\n')
            # print(text)
            impath=text[0]
            self.coordspath=text[1]
            linespath=''
            if len(text)>=3:
                linespath=text[2]
            self.open(filename=impath)
            if len(self.coordspath)>2:                
                self.coordsettingwdgt.loadCoords(self.coordspath)
                # self.coordinates=self.coordsettingwdgt.getCoordinates()
                self.iscoordinatesSet=True
                self.editCoordsAct.setEnabled(False)
                self.createlineAct.setEnabled(True)
            if len(linespath)<2:
                linespath=self.projectname.replace('.pd','') +'/lines.npy'

            self.lines=np.load(linespath,allow_pickle=True).item()
            newlines={}
            # print('self.lines ',self.lines)
            for self.linename in self.lines.keys():
                self.listWidget.addItem(self.linename)
                # print(self.linename)
                self.lineitems[self.linename]=LineItem(self.linename,self.viewer.scene,parent=self)
                newlines[self.linename]=[]
                for name,scenePos in self.lines[self.linename]:
                    self.lineitems[self.linename].append([name,scenePos])
                    newlines[self.linename].append([name,scenePos])
            self.lines=newlines

                # self.viewer.scene.addItem(path_item)
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
        self.scaleImage(0.5)
        

    def zoomOut(self):
        self.scaleImage(1.5)
    def zoomOnLine(self):
        print('zoomOnLine')
        for sitem in self.viewer.scene.items():
            # if sitem is not self.viewer._pixmapHandle:
            if hasattr(sitem, 'name'):
                print(sitem.name,self.linename)
                if sitem.name==self.linename:
                    sitem.selectItem()
                    rect=sitem.boundingRect()
                    print('item found')
                    self.viewer.zoomStack.append(rect)
                    self.viewer.updateViewer()
                    break
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
        self.zoomOnLineAct = QAction("Zoom on Line", self, shortcut="Ctrl+@", enabled=False, triggered=self.zoomOnLine)
        self.normalSizeAct = QAction("&Normal Size", self, shortcut="Ctrl+N", enabled=False, triggered=self.normalSize)
        self.fitToWindowAct = QAction("&Fit to Window", self, enabled=False, checkable=False, shortcut="Ctrl+F",
                                      triggered=self.fitToWindow)
        self.aboutAct = QAction("&About", self, triggered=self.about)
        self.aboutQtAct = QAction("About &Qt", self, triggered=qApp.aboutQt)

        self.editCoordsAct =QAction("&Enter Coords", self,enabled=False, checkable=False, shortcut="Ctrl+E", triggered=self.editCoords )
        self.createlineAct =QAction("&Start Line", self,enabled=False, checkable=False, shortcut="Ctrl+L", triggered=self.createLine )
        self.editPointsAct =QAction("&Enter Points", self,enabled=False, checkable=False, shortcut="Ctrl+T", triggered=self.editPoints )
        self.sortLineAct =QAction("&Sort", self,enabled=False, checkable=False, shortcut="Ctrl+^", triggered=self.sortLine )
    def _createToolBars(self):
        # File toolbar
        fileToolBar = self.addToolBar("File")
        fileToolBar.addAction(self.openProjectAct)
        fileToolBar.addAction(self.saveAct)
        # fileToolBar.addAction(self.saveAction)
        # Edit toolbar
        editToolBar = QToolBar("Edit", self)
        self.addToolBar(editToolBar)
        editToolBar.addAction(self.editCoordsAct)
        editToolBar.addAction(self.createlineAct)
        editToolBar.addAction(self.editPointsAct)
        editToolBar.addAction(self.sortLineAct)
        
        

        zoomToolBar = QToolBar("Zoom", self)
        self.addToolBar(zoomToolBar)
        zoomToolBar.addAction(self.zoomInAct)
        zoomToolBar.addAction(self.zoomOutAct)
        zoomToolBar.addAction(self.fitToWindowAct)
        zoomToolBar.addAction(self.zoomOnLineAct)

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
        self.zoomOnLineAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.normalSizeAct.setEnabled(not self.fitToWindowAct.isChecked())
        self. editCoordsAct.setEnabled(True)
        self. editPointsAct.setEnabled(True)

    def scaleImage(self, factor):

        self.scaleFactor = factor

        # self.viewer.scale(self.scaleFactor, self.scaleFactor)
        # self.viewer.updateViewer()
        self.viewer.applyZoom(self.scaleFactor)
        # self.imageLabel.resize(self.scaleFactor * self.imageLabel.pixmap().size())

        # self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
        # self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)
        
        # self.zoomInAct.setEnabled(self.scaleFactor < 3.0)
        # self.zoomOutAct.setEnabled(self.scaleFactor > 0.333)

    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value()
                               + ((factor - 1) * scrollBar.pageStep() / 2)))


    def editCoords(self):
        if not self.iscoordinatesSet:
            self.editcoordinates= not self.editcoordinates
            self.setCrossCursor()
            # cursor = Qt.CrossCursor
            # self.viewer.setCursor(cursor)
            self.allsaved=False
    def setCrossCursor(self):
        cursor = Qt.CrossCursor
        self.viewer.setCursor(cursor)
        
    def editPoints(self):
        if len(self.linename)>0:
        # if not self.iscoordinatesSet:
            # self.editPoints= not self.editPoints
            self.lineeditingdone=False
            self.editlines=True
            self.setCrossCursor()
            self.allsaved=False
            
        else:
            displayMessageBox('First create a line')
    def print(self):
        print('in print ',self.linename)
        for line in self.lines:
            print(line)
            for p in self.lines[line]:
                print('        ',p)

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


