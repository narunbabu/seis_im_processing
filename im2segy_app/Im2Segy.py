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
from image2segy_utils import *
__appname__ = 'DocDigi'

# class PredictedList(QWidget):
#     techdata_folder=r'D:\Ameyem\python\Digitization\TechMahindra\TechMData\\'

#     def __init__(self,fields,parent=None):
#         super().__init__(parent=parent)
#         self.title = 'Predictions'
#         self.result_layout=QVBoxLayout()
#         self.final_layout=QVBoxLayout()
#         # self.result_layout.setSpacing(5)
#         # self.result_layout.setContentsMargins(0,0,0,0)
#         self.final_layout.addLayout(self.result_layout)
#         self.setLayout(self.final_layout)
#         self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
#         self.rows=[]
#         self.fields=fields

#         addbutton=QPushButton(self)
#         addbutton.setText("Add +")
#         addbutton.setStyleSheet("background-color : grey")
#         self.final_layout.addWidget(addbutton)
#         addbutton.clicked.connect(self.addField)

#         button=QPushButton(self)
#         button.setText("Accept")
#         button.setStyleSheet("background-color : green")
#         self.final_layout.addWidget(button)
#         button.clicked.connect(self.getTable)
#     def addList(self,textlist):
#         for kv in textlist:
#             # print('kv ',kv)
#             self.addKeyValpair(kv[0],kv[1])

#     def addField(self):
#         self.addKeyValpair('','')
#     def addKeyValpair(self,key,val):
#         keyline = QLineEdit(self)
#         keyline.setText(key)
#         valline = QLineEdit(self)
#         valline.setText(val)
#         cb = QComboBox()
#         for c in self.fields:
#             cb.addItem(c)
#         self.rows.append([keyline,cb,valline])

#         keyval_layout=QHBoxLayout()        
#         keyval_layout.addWidget(keyline)
#         keyval_layout.addWidget(cb)
#         keyval_layout.addWidget(valline)
#         self.result_layout.addLayout(keyval_layout)

#     def getTable(self):
#         table=[]
#         for row in self.rows:
#             table.append([row[0].text(),row[1].currentText(),row[2].text()])
#         table=np.array(table)
#         newdf=pd.DataFrame([table[:,-1]],columns=list(table[:,1]))

#         df=pd.read_excel(self.techdata_folder+'Template_Indexing1.xlsx')
#         df=df.append(newdf).fillna('')
#         df.to_excel(self.techdata_folder+'Template_Indexing1.xlsx',index=False)
        
#         return table

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
        trace_label=QLabel("Trace Count")
        self.trace_count_edit=QLineEdit()

        totaltime_label=QLabel("TotalTime(sec)")
        self.total_time_edit=QLineEdit('6.0')

        trac_hbox=QHBoxLayout()
        trac_hbox.addWidget(trace_label)
        trac_hbox.addWidget(self.trace_count_edit)
        trace_wdgt=QWidget()
        trace_wdgt.setLayout(trac_hbox)
        trace_wdgt.setMaximumHeight(50)

        time_hbox=QHBoxLayout()
        time_hbox.addWidget(totaltime_label)
        time_hbox.addWidget(self.total_time_edit)
        time_wdgt=QWidget()
        time_wdgt.setLayout(time_hbox)
        time_wdgt.setMaximumHeight(50)

        segy_export_button = QPushButton(self)
        segy_export_button.setText("Export Segy")
        segy_export_button.clicked.connect(self.segy_export_act)     

        save_fields_button = QPushButton(self)
        save_fields_button.setText("Save Crop image")
        save_fields_button.clicked.connect(self.save_fields_act)     
        save_fields_button.setEnabled(True)

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
        ML_button_layout.addWidget(trace_wdgt)
        ML_button_layout.addWidget(time_wdgt)
        ML_button_layout.addWidget(segy_export_button)


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


        # self.predicted_table=QWidget(self)
        
        # self.splitter.addWidget(self.predicted_table)


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
    def PixIm_to_CV2Im(self,qimg):
        # print('-----QPixmap_to_Opencv-----')
        # print('qtpixmap type:',type(qtpixmap))
        # qimg = qtpixmap.toImage()  # QPixmap-->QImage
        # print('qimg type:', type(qimg))

        temp_shape = (qimg.height(), qimg.bytesPerLine() * 8 // qimg.depth())
        temp_shape += (4,)
        ptr = qimg.bits()
        ptr.setsize(qimg.byteCount())
        result = np.array(ptr, dtype=np.uint8).reshape(temp_shape)
        result = result[..., :3]
        # cv2.imwrite('./result.jpg',result) # If saved, RGB format will be displayed
        return result
    def segy_export_act(self):
        filename=self.bigim_canvas.file_path[:-4] +'_raw.sgy'
        ntrace=int(self.trace_count_edit.text())
        ntrc=ntrace
        strc=1
        # etrc=strc+ntrc+
        stime,etime=0,float(self.total_time_edit.text())*1000
        try:
            gray = cv2.cvtColor(self.PixIm_to_CV2Im(self.crop_image), cv2.COLOR_BGR2GRAY)
        except:
            gray=np.zeros((2,2))
            msg=QMessageBox()
            msg.setText('Crop image first \n')
            msg.exec_()
            return 0

        sgray=gray.sum(axis=1)


        cutoff = 30.0
        bestcases={'':6}
        for key in bestcases:
            case=bestcases[key]
            print('Case: ',case)
            crude_hor_filter,useStepOp,useHorfilter=getDirections(case)
            #Horizontal filter calculation to remove horizontal lines
            twt=list(range(len(sgray)))
            lf_data,wf_data,hf_data,xmaxnormmeans=windowFilt(twt,sgray,nclip=0,window=(1,10),order=4)
            useHorfilter=True
            crude_hor_filter=False
            if useHorfilter:
                if not crude_hor_filter:
                    hlfilter=gethorizontalLineFilter(hf_data,gray) #median gap found and kept lo values to nullify horizontal line
                    hlfilter[hlfilter<=0.5]=0.5
                    print('hlfilter')
                else:
                    hlfilter=getHorizontalRawFilter(hf_data) #filter generate with crude way, line gaps are filled with 0.1 values

            mthresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
            #     traces=img2rawtrace(clipped_im,stime,etime,ntrc)
            traces=img2rawtrace(mthresh,stime,etime,ntrc)
            # traces=successiveDeduction(traces,ntraces=200)
            #Operator for smooth trace
            trcno=200
            if trcno> len(traces): trcno=int(len(traces)/2)
            mtrc=traces[trcno]


            if useHorfilter:
                mtrc=mtrc*hlfilter

            if not useStepOp:
                op=getOperator(mtrc,old=False)
            else:
                op=getOperatorStep(mtrc)


            # Filter or not and make resultant traces as float64 type
            tracet=traces.shape[1]
            actualt=etime
            tracetpermsec=tracet/etime
            for50msec=tracetpermsec*30
            traces[:,:int(for50msec)]=traces[:,:int(for50msec)]*0.1

            if useHorfilter:
                result=(np.array(traces)*hlfilter*1000).astype(np.float64)
            else:
                result=(np.array(traces)*1000).astype(np.float64)

            print(traces.shape,result.shape)
            trange=np.arange(stime,etime+1,2).astype(int)
            proctrcs= getOpProcTraces(result,op,trange)
        #     filttrcs=np.array(proctrcs)
            filttrcs= getLowPassfilteredTraces(proctrcs,cutoff = cutoff )

            inputdict=dict(dstpath=filename,srcpath='./bak_test2.sgy',mintime=1300,mxtime=1500,dt=1,iline=1, xline=169, offset=0)

            status=saveAsSegy(filttrcs.T,inputdict=inputdict,delrt=2,strc=strc,setimes=[stime,etime])
            if status:    
                print('Done export..',inputdict['dstpath'])
            else:
                print('Export incomplete..')
            msg=QMessageBox()
            msg.setText('Done Export.... \n'+filename)
            msg.exec_()
    # def scan_all_images(self, folder_path):
    #     extensions = ['.tif']
    #     images = []

    #     for root, dirs, files in os.walk(folder_path):
    #         for file in files:
    #             if file.lower().endswith(tuple(extensions)):
    #                 relative_path = os.path.join(root, file)
    #                 path = ustr(os.path.abspath(relative_path))
    #                 images.append(path)
    #     natural_sort(images, key=lambda x: x.lower())
    #     return images
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