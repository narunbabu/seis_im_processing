import sys
import argparse
import codecs
import os.path
import platform
import shutil
import pathlib
import qimage2ndarray
from pathlib import Path
from PIL.ImageQt import ImageQt
from PIL import Image
from skimage.transform import resize

# import pytesseract
import cv2
# pytesseract.pytesseract.tesseract_cmd ='C:\Program Files (x86)\Tesseract-OCR/tesseract.exe'
import pandas as pd
try:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    # needed for py3+qt4
    # Ref:
    # http://pyqt.sourceforge.net/Docs/PyQt4/incompatible_apis.html
    # http://stackoverflow.com/questions/21217399/pyqt4-qtcore-qvariant-object-instead-of-a-string
    if sys.version_info.major >= 3:
        import sip
        sip.setapi('QVariant', 2)
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *
from libs.resources import *
from libs.constants import *
from libs.utils import *
from libs.labelFile import LabelFile
# from detect import CreateDetectionModel
# sys.path.append( '../yolov5')

from utils.plots import Annotator, colors, save_one_box
from utils.general import increment_path

# from ImageFields import CanvasMainWindow as FieldCanvasMainWindow
from ImageBig import CanvasMainWindow as BigCanvasMainWindow
import numpy as np
__appname__ = 'DocDigi'

class PredictedList(QWidget):
    techdata_folder=r'D:\Ameyem\python\Digitization\TechMahindra\TechMData\\'

    def __init__(self,fields,parent=None):
        super().__init__(parent=parent)
        self.title = 'Predictions'
        self.result_layout=QVBoxLayout()
        self.final_layout=QVBoxLayout()
        # self.result_layout.setSpacing(5)
        # self.result_layout.setContentsMargins(0,0,0,0)
        self.final_layout.addLayout(self.result_layout)
        self.setLayout(self.final_layout)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.rows=[]
        self.fields=fields

        addbutton=QPushButton(self)
        addbutton.setText("Add +")
        addbutton.setStyleSheet("background-color : grey")
        self.final_layout.addWidget(addbutton)
        addbutton.clicked.connect(self.addField)

        button=QPushButton(self)
        button.setText("Accept")
        button.setStyleSheet("background-color : green")
        self.final_layout.addWidget(button)
        button.clicked.connect(self.getTable)
    def addList(self,textlist):
        for kv in textlist:
            # print('kv ',kv)
            self.addKeyValpair(kv[0],kv[1])

    def addField(self):
        self.addKeyValpair('','')
    def addKeyValpair(self,key,val):
        keyline = QLineEdit(self)
        keyline.setText(key)
        valline = QLineEdit(self)
        valline.setText(val)
        cb = QComboBox()
        for c in self.fields:
            cb.addItem(c)
        self.rows.append([keyline,cb,valline])

        keyval_layout=QHBoxLayout()        
        keyval_layout.addWidget(keyline)
        keyval_layout.addWidget(cb)
        keyval_layout.addWidget(valline)
        self.result_layout.addLayout(keyval_layout)

    def getTable(self):
        table=[]
        for row in self.rows:
            table.append([row[0].text(),row[1].currentText(),row[2].text()])
        table=np.array(table)
        newdf=pd.DataFrame([table[:,-1]],columns=list(table[:,1]))

        df=pd.read_excel(self.techdata_folder+'Template_Indexing1.xlsx')
        df=df.append(newdf).fillna('')
        df.to_excel(self.techdata_folder+'Template_Indexing1.xlsx',index=False)
        
        return table

class ScrollLabel(QScrollArea):
  
    # constructor
    def __init__(self, *args, **kwargs):
        QScrollArea.__init__(self, *args, **kwargs)
  
        # making widget resizable
        self.setWidgetResizable(True)
  
        # making qwidget object
        content = QWidget(self)
        self.setWidget(content)
  
        # vertical box layout
        lay = QVBoxLayout(content)
  
        # creating label
        self.label = QLabel(content)
  
        # setting alignment to the text
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
  
        # making label multi-line
        self.label.setWordWrap(True)
  
        # adding label to the layout
        lay.addWidget(self.label)
  
    # the setText method
    def setText(self, text):
        # setting text to the label
        self.label.setText(text)
    def setPixmap(self, pixmap):
        # setting text to the label
        
        
        self.label.setPixmap(pixmap)
        # self.resize(300,400)
    # getting text method
    def text(self):
  
        # getting text of the label
        get_text = self.label.text()
  
        # return the text
        return get_text

class MainWindow(QMainWindow):
    def __init__(self,args, parent=None):
        QMainWindow.__init__(self, parent) 
        self.bigim_canvas=BigCanvasMainWindow(args.image_dir, args.class_file, args.save_dir, parent=self) 
        # self.field_canvas=FieldCanvasMainWindow( args.image_dir, args.class_file, args.save_dir,parent=parent) 
        self.field_canvas=QWidget()
        self.field_layout=QHBoxLayout()
        self.field_canvas.setLayout(self.field_layout)

        self.file_path= self.bigim_canvas.file_path
        self.label_coordinates= self.bigim_canvas.label_coordinates

        self.splitter = QSplitter(Qt.Horizontal)
        self.statusBar().showMessage('%s started.' % __appname__)
        self.statusBar().show()
        

        

        ML_button_layout=QVBoxLayout()

        # predict_fields_button = QPushButton(self)
        # predict_fields_button.setText("Pedict Fields")
        # predict_fields_button.clicked.connect(self.predict_fields_act)

        save_fields_button = QPushButton(self)
        save_fields_button.setText("Save Crop image")
        save_fields_button.clicked.connect(self.save_fields_act)



        crop_fields_button = QPushButton(self)
        crop_fields_button.setText("Crop Fields")
        crop_fields_button.clicked.connect(self.crop_fields_act)

        self.checkbox = QCheckBox('Return smooth', self)
        # self.checkbox.setGeometry(200, 150, 100, 30)

  
        
  

        align_button = QPushButton(self)
        align_button.setText("Align")
        align_button.clicked.connect(self.align_act)

        unalign_button = QPushButton(self)
        unalign_button.setText("Undo Align")
        unalign_button.clicked.connect(self.undo_align_act)
        ML_button_layout.addWidget(self.checkbox)
        ML_button_layout.addWidget(align_button)
        ML_button_layout.addWidget(unalign_button)
        
        ML_button_layout.addWidget(crop_fields_button)
        ML_button_layout.addWidget(save_fields_button)
        ML_button_group = QGroupBox("Predict")
        ML_button_group.setLayout(ML_button_layout)

        main_widget=QWidget(self)
        main_layout=QHBoxLayout()
        main_widget.setLayout(main_layout)
        main_layout.addWidget(ML_button_group)
        main_layout.addWidget(self.splitter)
        self.setCentralWidget(main_widget)
        self.mylabel=ScrollLabel(self)
        # self.mylabel_kv=ScrollLabel(self)
        self.field_layout.addWidget(self.mylabel)
        # self.field_layout.addWidget(self.mylabel_kv)
        self.field_canvas.setMinimumSize(int(self.frameGeometry().width()/2),int(self.frameGeometry().height()-30))

        self.splitter.addWidget(self.bigim_canvas)
        self.splitter.addWidget(ML_button_group)
        self.splitter.addWidget(self.field_canvas)
        # self.splitter.addWidget(field_ML_button_group)


        self.predicted_table=QWidget(self)
        
        self.splitter.addWidget(self.predicted_table)


        self.setCentralWidget(self.splitter)
        # self.loadModels()


    def predict_fields_act(self):
        print('predictin fields')

    def save_fields_act(self):
        print('Saving Cropimage')
        filename=self.bigim_canvas.file_path[:-4] +'_crop.png'

        self.crop_image.save(filename, "PNG")
        

        msg=QMessageBox()
        msg.setText('Done Saving.... \n'+filename)
        msg.exec_()



    def reset_state(self):
        None
        # # self.mylabel.clear()
        # self.mylabel=ScrollLabel(self)

        self.file_path = None
        self.image_data = None

        # self.canvas.reset_state()
        self.label_coordinates.clear()

    def crop_fields_act(self):        
        yolo_boxes=np.array(self.getYoloBoxes())
        # print('yolo_boxes ',yolo_boxes)

        # npimage = qimage2ndarray.recarray_view(self.bigim_canvas.image)
        xyxys=self.xywh2xyxy(yolo_boxes,self.bigim_canvas.image_data)
        # print('xyxy ',xyxys)
        rect = QRect(xyxys[0][0],xyxys[0][1] ,xyxys[0][2]-xyxys[0][0] ,xyxys[0][3]-xyxys[0][1]     )
        # print('self.bigim_canvas.image.size',self.bigim_canvas.image.size())
        
        # self.crop_image = self.bigim_canvas.image.copy(rect)
        self.crop_image = self.bigim_canvas.canvas.pixmap.toImage().copy(rect)
        print('self.crop_image.image.size',self.crop_image.size())
        # print('SIZE   ',image.size)        
        pixmap=QPixmap.fromImage(self.crop_image)
        pixmap = pixmap.scaled(self.bigim_canvas.frameGeometry().size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.mylabel.setPixmap(pixmap)
    def align_act(self):        
        # checking if it checked
        check = self.checkbox.isChecked()
        self.bigim_canvas.align_act(check)
    def undo_align_act(self):
        self.bigim_canvas.undo_align_act()
        

    def xywh2xyxy(self,newbboxes,newimage):
        # print(newimage.shape)
        newbboxes=newbboxes[:,1:]
        # width,height=newimage.shape
        width = newimage.width()
        height = newimage.height()

        newbboxes[:,:2]=newbboxes[:,:2]-newbboxes[:,2:]/2
        newbboxes[:,2:]=newbboxes[:,:2]+newbboxes[:,2:]

        newbboxes[:,[0,2]]=newbboxes[:,[0,2]]*width
        newbboxes[:,[1,3]]=newbboxes[:,[1,3]]*height
        return newbboxes

    def getLabel(self,crop_im):
        pixmap_label = QLabel()                                                                                                                                                                                
        pixmap_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)                                                                                                                                   
        # pixmap_label.resize(200,50)                                                                                                                                                                           
        pixmap_label.setAlignment(Qt.AlignCenter)                                                                                                                                                              

        # im_np = np.ones((1800,2880,3),dtype=uint8)      
        # print('crop_im shape ',crop_im.shape)   
        # im_np = np.transpose(crop_im, (1,0,2))   

        QI=QImage(crop_im.data, crop_im.shape[1], crop_im.shape[0], QImage.Format_RGB888)

        # QI=QImage(crop_im.data, crop_im.shape[0], crop_im.shape[1], QImage.Format_RGB888)
        # QI.setColorTable(COLORTABLE)
        pixmap_label.setPixmap(QPixmap.fromImage(QI))                                                                                                                                                                       
        # im_np = crop_im                                                                                                                                                                            
        # qimage = QImage(im_np, im_np.shape[1], im_np.shape[0],                                                                                                                                                 
        #                 QImage.Format_RGB888)                                                                                                                                                                 
        # pixmap = QPixmap(qimage)                                                                                                                                                                               
        # pixmap = pixmap.scaled(640,400, Qt.KeepAspectRatio)                                                                                                                                                    
        # pixmap_label.setPixmap(pixmap)
        return   pixmap_label                                                                                                                                                                      

    #  self.setCentralWidget(pixmap_label) 

    def getYoloBoxes(self):
        self.image_data=self.bigim_canvas.image_data
        image_shape = [self.image_data.height(), self.image_data.width(),
                       1 if self.image_data.isGrayscale() else 3]
        yolo_boxes=[]
        for s in self.bigim_canvas.canvas.shapes:
            print(s)
            # print('shape ',[(p.x(), p.y()) for p in s.points])
            points=[(p.x(), p.y()) for p in s.points]
            bnd_box = LabelFile.convert_points_to_bnd_box(points)
            x_min, y_min, x_max, y_max=[bnd_box[0], bnd_box[1], bnd_box[2], bnd_box[3]]

            x_center = float((x_min + x_max)) / 2 / image_shape[1]
            y_center = float((y_min + y_max)) / 2 / image_shape[0]

            w = float((x_max - x_min)) / image_shape[1]
            h = float((y_max - y_min)) / image_shape[0]
            yolo_boxes.append([1,x_center,y_center,w,h])
        return yolo_boxes
            # print(s.label,' bbox ',yolo_box)
            # assert self.beginner()
            # self.canvas.set_editing(False)
            # self.actions.create.setEnabled(False)
    def predict_text_act(self):
        print('predictin fields')


def get_main_app(argv=None):
    """
    Standard boilerplate Qt application code.
    Do everything but app.exec_() -- so that we can test the application in one thread
    """
    if not argv:
        argv = []
    app = QApplication(argv)
    app.setApplicationName(__appname__)
    app.setWindowIcon(new_icon("app"))
    # Tzutalin 201705+: Accept extra agruments to change predefined class file
    argparser = argparse.ArgumentParser()
    argparser.add_argument("image_dir", nargs="?")
    argparser.add_argument("class_file",
                           default=os.path.join(os.path.dirname(__file__), "data", "predefined_classes.txt"),
                           nargs="?")
    argparser.add_argument("save_dir", nargs="?")
    args = argparser.parse_args(argv[1:])

    args.image_dir = args.image_dir and os.path.normpath(args.image_dir)
    args.class_file = args.class_file and os.path.normpath(args.class_file)
    args.save_dir = args.save_dir and os.path.normpath(args.save_dir)

    # Usage : labelImg.py image classFile saveDir
    win=MainWindow(args)
    # win= MainWindow(args)
    win.show()
    return app, win


def main():
    """construct main app and run it"""
    app, _win = get_main_app(sys.argv)
    return app.exec_()

if __name__ == '__main__':
    sys.exit(main())