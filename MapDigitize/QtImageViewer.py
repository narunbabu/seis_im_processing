""" QtImageViewer.py: PyQt image viewer widget for a QPixmap in a QGraphicsView scene with mouse zooming and panning.

"""

import os.path
try:
    from PyQt5.QtCore import Qt, QRectF, pyqtSignal, QT_VERSION_STR,QPointF
    from PyQt5.QtGui import QImage, QPixmap, QPainterPath
    from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QFileDialog,QLabel,QGraphicsSimpleTextItem
except ImportError:
    try:
        from PyQt4.QtCore import Qt, QRectF, pyqtSignal, QT_VERSION_STR
        from PyQt4.QtGui import QGraphicsView, QGraphicsScene, QImage, QPixmap, QPainterPath, QFileDialog
    except ImportError:
        raise ImportError("QtImageViewer: Requires PyQt5 or PyQt4.")


__author__ = "Marcel Goldschen-Ohm <marcel.goldschen@gmail.com>"
__version__ = '0.9.0'


class QtImageViewer(QGraphicsView):
    """ PyQt image viewer widget for a QPixmap in a QGraphicsView scene with mouse zooming and panning.

    Displays a QImage or QPixmap (QImage is internally converted to a QPixmap).
    To display any other image format, you must first convert it to a QImage or QPixmap.

    Some useful image format conversion utilities:
        qimage2ndarray: NumPy ndarray <==> QImage    (https://github.com/hmeine/qimage2ndarray)
        ImageQt: PIL Image <==> QImage  (https://github.com/python-pillow/Pillow/blob/master/PIL/ImageQt.py)

    Mouse interaction:
        Left mouse button drag: Pan image.
        Right mouse button drag: Zoom box.
        Right mouse button doubleclick: Zoom to show entire image.
    """

    # Mouse button signals emit image scene (x, y) coordinates.
    # !!! For image (row, column) matrix indexing, row = y and column = x.
    leftMouseButtonPressed = pyqtSignal(float, float)
    rightMouseButtonPressed = pyqtSignal(float, float)
    leftMouseButtonReleased = pyqtSignal(float, float)
    rightMouseButtonReleased = pyqtSignal(float, float)
    leftMouseButtonDoubleClicked = pyqtSignal(float, float)
    rightMouseButtonDoubleClicked = pyqtSignal(float, float)

    middleMouseButtonPressed = pyqtSignal(float, float)

    def __init__(self):
        QGraphicsView.__init__(self)

        # Image is displayed as a QPixmap in a QGraphicsScene attached to this QGraphicsView.
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        # Store a local handle to the scene's current image pixmap.
        self._pixmapHandle = None

        # Image aspect ratio mode.
        # !!! ONLY applies to full image. Aspect ratio is always ignored when zooming.
        #   Qt.IgnoreAspectRatio: Scale image to fit viewport.
        #   Qt.KeepAspectRatio: Scale image to fit inside viewport, preserving aspect ratio.
        #   Qt.KeepAspectRatioByExpanding: Scale image to fill the viewport, preserving aspect ratio.
        self.aspectRatioMode = Qt.KeepAspectRatio

        # Scroll bar behaviour.
        #   Qt.ScrollBarAlwaysOff: Never shows a scroll bar.
        #   Qt.ScrollBarAlwaysOn: Always shows a scroll bar.
        #   Qt.ScrollBarAsNeeded: Shows a scroll bar only when zoomed.
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Stack of QRectF zoom boxes in scene coordinates.
        self.zoomStack = []

        # Flags for enabling/disabling mouse interaction.
        self.canZoom = True
        self.canPan = True

        self.label_position = QGraphicsSimpleTextItem('Welocme to the Map digitizer...')
        self.scene.addItem(self.label_position)

        self.label_position.setPos(50,50)

        # self.video_label = QLabel()
        # self.video_label.setStyleSheet("background-color: green; border: 1px solid black")
        # self.label_position = QLabel(
        #     self.video_label, alignment=Qt.AlignCenter
        # )
        # self.label_position.setStyleSheet('background-color: white; border: 1px solid black')

    def hasImage(self):
        """ Returns whether or not the scene contains an image pixmap.
        """
        return self._pixmapHandle is not None

    def clearImage(self):
        """ Removes the current image pixmap from the scene if it exists.
        """
        if self.hasImage():
            self.scene.removeItem(self._pixmapHandle)
            self._pixmapHandle = None

    def pixmap(self):
        """ Returns the scene's current image pixmap as a QPixmap, or else None if no image exists.
        :rtype: QPixmap | None
        """
        if self.hasImage():
            return self._pixmapHandle.pixmap()
        return None

    def image(self):
        """ Returns the scene's current image pixmap as a QImage, or else None if no image exists.
        :rtype: QImage | None
        """
        if self.hasImage():
            return self._pixmapHandle.pixmap().toImage()
        return None

    def setImage(self, image):
        """ Set the scene's current image pixmap to the input QImage or QPixmap.
        Raises a RuntimeError if the input image has type other than QImage or QPixmap.
        :type image: QImage | QPixmap
        """
        if type(image) is QPixmap:
            pixmap = image
        elif type(image) is QImage:
            pixmap = QPixmap.fromImage(image)
        else:
            raise RuntimeError("ImageViewer.setImage: Argument must be a QImage or QPixmap.")
        if self.hasImage():
            self._pixmapHandle.setPixmap(pixmap)
        else:
            self._pixmapHandle = self.scene.addPixmap(pixmap)
        self.setSceneRect(QRectF(pixmap.rect()))  # Set scene size to image size.
        self.updateViewer()

    def loadImageFromFile(self, fileName=""):
        """ Load an image from file.
        Without any arguments, loadImageFromFile() will popup a file dialog to choose the image file.
        With a fileName argument, loadImageFromFile(fileName) will attempt to load the specified image file directly.
        """
        if len(fileName) == 0:
            if QT_VERSION_STR[0] == '4':
                fileName = QFileDialog.getOpenFileName(self, "Open image file.")
            elif QT_VERSION_STR[0] == '5':
                fileName, dummy = QFileDialog.getOpenFileName(self, "Open image file.")
        if len(fileName) and os.path.isfile(fileName):
            image = QImage(fileName)
            self.setImage(image)

    def updateViewer(self):
        """ Show current zoom (if showing entire image, apply current aspect ratio mode).
        """
        if not self.hasImage():
            return
        if len(self.zoomStack) and self.sceneRect().contains(self.zoomStack[-1]):
            # self.fitInView(self.zoomStack[-1], Qt.IgnoreAspectRatio)  # Show zoomed rect (ignore aspect ratio).
            self.fitInView(self.zoomStack[-1], self.aspectRatioMode)  # Show zoomed rect (ignore aspect ratio).
        else:
            self.zoomStack = []  # Clear the zoom stack (in case we got here because of an invalid zoom).
            self.fitInView(self.sceneRect(), self.aspectRatioMode)  # Show entire image (use current aspect ratio mode).

    def resizeEvent(self, event):
        """ Maintain current zoom on resize.
        """
        self.updateViewer()
    def handleEllipseItemRelased(self,pos,name):       
        None

    def mousePressEvent(self, event):
        """ Start mouse pan or zoom mode.
        """
        # print(event.pos())
        scenePos = self.mapToScene(event.pos())
        if event.button() == Qt.LeftButton:
            if self.canPan:
                self.setDragMode(QGraphicsView.ScrollHandDrag)

            # self.leftMouseButtonPressed.emit(scenePos.x(), scenePos.y())
            self.leftMouseButtonPressed.emit(event.pos().x(), event.pos().y())
        elif event.button() == Qt.RightButton:
            if self.canZoom:
                self.setDragMode(QGraphicsView.RubberBandDrag)
            self.rightMouseButtonPressed.emit(scenePos.x(), scenePos.y())
        elif event.button() == Qt.MidButton:
            self.middleMouseButtonPressed.emit(scenePos.x(), scenePos.y())
        QGraphicsView.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        """ Stop mouse pan or zoom mode (apply zoom if valid).
        """
        QGraphicsView.mouseReleaseEvent(self, event)
        scenePos = self.mapToScene(event.pos())
        if event.button() == Qt.LeftButton:
            self.setDragMode(QGraphicsView.NoDrag)
            self.leftMouseButtonReleased.emit(scenePos.x(), scenePos.y())
        elif event.button() == Qt.RightButton:
            if self.canZoom:
                viewBBox = self.zoomStack[-1] if len(self.zoomStack) else self.sceneRect()
                selectionBBox = self.scene.selectionArea().boundingRect().intersected(viewBBox)
                self.scene.setSelectionArea(QPainterPath())  # Clear current selection area.
                if selectionBBox.isValid() and (selectionBBox != viewBBox):
                    self.zoomStack.append(selectionBBox)
                    print(self.zoomStack)
                    self.updateViewer()
            self.setDragMode(QGraphicsView.NoDrag)
            self.rightMouseButtonReleased.emit(scenePos.x(), scenePos.y())

    def mouseDoubleClickEvent(self, event):
        """ Show entire image.
        """
        scenePos = self.mapToScene(event.pos())
        if event.button() == Qt.LeftButton:
            self.leftMouseButtonDoubleClicked.emit(scenePos.x(), scenePos.y())
        elif event.button() == Qt.RightButton:
            if self.canZoom:
                self.zoomStack = []  # Clear zoom stack.
                self.updateViewer()
            self.rightMouseButtonDoubleClicked.emit(scenePos.x(), scenePos.y())
        QGraphicsView.mouseDoubleClickEvent(self, event)
    def applyZoom(self,factor):

        if self.canZoom:
            sceneBBox = self.sceneRect()
            # print(dir(self))
            # print('viewBBox ', viewBBox)
            vprect=self.viewport().rect()
            # print('self.viewport().rect() ',self.viewport().rect())
            

            # vieportrect=self.mapToScene(self.viewport().rect())

            
            # print('vprect ',vprect.x(),vprect.y(),vprect.width(), vprect.height())
            # print(dir(vieportrect))
            svprect = QRectF(self.mapToScene(vprect.x(),vprect.y()), self.mapToScene(vprect.width(), vprect.height()))
            viewBBox=svprect
            if svprect.x()<0:
                viewBBox.setX(sceneBBox.x())
                viewBBox.setWidth(sceneBBox.width())
            if svprect.y()<0:
                viewBBox.setY(sceneBBox.y())
                viewBBox.setHeight(sceneBBox.height())

            # selBox=self.scene.sceneRect()
            # print('scene.sceneRect of vprect ', scenerect)

            # print('vieportrect ', vieportrect.value(4))
            # print('visibleRegion ',self.visibleRegion(),'rect ',self.rect(),'viewportMargins ',self.viewportMargins(),'screen ',self.screen())
            left=viewBBox.x()+viewBBox.width()/2
            top=viewBBox.y()+viewBBox.height()/2
            w,h=viewBBox.width() * factor, viewBBox.height() * factor
            print('viewBBox.width() , viewBBox.height() ',viewBBox.width() , viewBBox.height())

            print('w,h ',w,h)
            x,y=left-w/2,top-h/2
            print('x,y,w,h ',x,y,w,h)
            # x,y,w,h=max(left-w/2,viewBBox.x()),max(top-h/2,viewBBox.y()),min(w,viewBBox.width()),min(h,viewBBox.height())
            
            x,y,w,h=max(x,sceneBBox.x()),max(y,sceneBBox.y()),min(w,sceneBBox.width()),min(h,sceneBBox.height())
            print('x,y,w,h ',x,y,w,h)

            box=QRectF(x,y,w,h)
            # print('viewBBox ', box)
            # selectionBBox = self.scene.selectionArea().boundingRect().intersected(box)
            # print('selectionBBox ', selectionBBox)
            self.scene.setSelectionArea(QPainterPath())  # Clear current selection area.
            # if selectionBBox.isValid() and (selectionBBox != viewBBox):
            self.zoomStack.append(box)
            print('zoomStack length: ',len(self.zoomStack))
            self.updateViewer()

        # if self.hasImage():
        #     # unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
        #     # self.scale(1 / unity.width(), 1 / unity.height())
            
        #     # factor = min(viewrect.width() / scenerect.width(),
        #     #              viewrect.height() / scenerect.height())
        #     self.scale(factor, factor)
        # #     rect = self.viewport().rect()
        # #     scenerect = self.transform().mapRect(rect)
        # #     self.zoomStack.append(scenerect)
        # # self._zoom = 0
        # self.updateViewer()
    def myfitInView(self, scale=True):
        # rect = QRectF(self._pixmapHandle.pixmap().rect())

        # self.scene.setSelectionArea(QPainterPath())  # Clear current selection area.
        # self.zoomStack.append(rect)

        self.zoomStack = []

        # self.setSceneRect(rect)  # Set scene size to image size.
        self.updateViewer()
        self.setDragMode(QGraphicsView.NoDrag)

        # if not rect.isNull():
        #     self.setSceneRect(rect)
        #     if self.hasImage():
        #         unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
        #         self.scale(1 / unity.width(), 1 / unity.height())
        #         viewrect = self.viewport().rect()
        #         scenerect = self.transform().mapRect(rect)
        #         # factor = min(viewrect.width() / scenerect.width(),
        #         #              viewrect.height() / scenerect.height())
        #         # self.scale(factor, factor)
        #         self.zoomStack.append(scenerect)
        #     self._zoom = 0
        #     self.updateViewer()


if __name__ == '__main__':
    import sys
    try:
        from PyQt5.QtWidgets import QApplication
    except ImportError:
        try:
            from PyQt4.QtGui import QApplication
        except ImportError:
            raise ImportError("QtImageViewer: Requires PyQt5 or PyQt4.")
    print('Using Qt ' + QT_VERSION_STR)

    def handleLeftClick(x, y):
        row = int(y)
        column = int(x)
        print("Clicked on image pixel (row="+str(row)+", column="+str(column)+")")

    # Create the application.
    app = QApplication(sys.argv)

    # Create image viewer and load an image file to display.
    viewer = QtImageViewer()
    viewer.loadImageFromFile()  # Pops up file dialog.

    # Handle left mouse clicks with custom slot.
    viewer.leftMouseButtonPressed.connect(handleLeftClick)

    # Show viewer and run application.
    viewer.show()
    sys.exit(app.exec_())