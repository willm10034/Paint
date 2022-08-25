from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PIL import Image
import sys
import numpy as np
import cv2


# window class
class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        # setting title
        self.setWindowTitle("paint")

        # setting geometry to main window
        self.setGeometry(200, 200, 800, 600)

        # creating image object
        self.image = QImage(self.size(), QImage.Format_RGB32)

        # making image color to white
        self.image.fill(Qt.white)

        # variables
        # drawing flag
        self.drawing = False
        # default brush size
        self.brushSize = 4
        # default color
        self.brushColor = Qt.black

        self.tool = 'brush'  # brush, fill, rectangle
        self.drawrect = False
        self.drawfill = False
        self.drawellipse = False
        self.zoom = False
        self.drawline = False
        self.beginpoint, self.endpoint = QPoint(0, 0), QPoint(0, 0)
        self.b, self.g, self.r = 0, 0, 0

        # QPoint object to tract the point
        self.lastPoint = QPoint()

        # creating menu bar
        mainMenu = self.menuBar()

        # creating file menu for save and clear action
        fileMenu = mainMenu.addMenu("File")

        editMenu = mainMenu.addMenu("Edit")

        # creating open action
        openAction = QAction("Open", self)
        openAction.setShortcut("Ctrl + O")
        fileMenu.addAction(openAction)
        openAction.triggered.connect(self.open)

        # creating save action
        saveAction = QAction("Save", self)
        saveAction.setShortcut("Ctrl + S")
        fileMenu.addAction(saveAction)
        saveAction.triggered.connect(self.save)

        # creating clear action
        clearAction = QAction("Clear", self)
        clearAction.setShortcut("Ctrl + C")
        fileMenu.addAction(clearAction)
        clearAction.triggered.connect(self.clear)

        undoAction = QAction("Undo", self)
        undoAction.setShortcut("Ctrl + X")
        editMenu.addAction(undoAction)
        undoAction.triggered.connect(self.undo)

        self.undo_levels = 0
        self.undo_index = 0
        self.undo_stack = []

        # create tools window, implemented with open-cv
        self.img = cv2.imread('paint_pallete.jpg')
        cv2.namedWindow('tools')
        cv2.setMouseCallback('tools', self.select_color)
        cv2.rectangle(self.img, (417, 23), (475, 80), (0, 0, 0), -1)  # color selection
        cv2.rectangle(self.img, (601, 1), (632, 33), (255, 255, 255), 1)  # brush outline
        cv2.rectangle(self.img, (511, 1), (525, 99), (0, 225, 255), 2)  # line weight outline
        cv2.imshow('tools', self.img)

    def select_color(self, event, x, y, flags, param):
        if event == 4:  # mouse click
            self.img = cv2.imread('paint_pallete.jpg')
            cv2.namedWindow('tools')
            cv2.setMouseCallback('tools', self.select_color)
            # print(str(y) + ', ' + str(x))
            if x < 400:
                self.b, self.g, self.r = self.img[y, x]
                b, g, r = int(self.b), int(self.g), int(self.r)
                a = 1  # alpha
                self.brushColor = QColor.fromRgbF(r / 255, g / 255, b / 255, a)
                # cv2.rectangle(image, startpoint, endpoint, color, thickness) -1 thickness fills rectangle entirely
                cv2.rectangle(self.img, (417, 23), (475, 80), (b, g, r), -1)
                # print(str(b) + ', ' + str(g) + ', ' + str(r))
            elif 493 <= x <= 511:
                self.brushSize = 1
                b, g, r = int(self.b), int(self.g), int(self.r)
                cv2.rectangle(self.img, (417, 23), (475, 80), (b, g, r), -1)
            elif 512 <= x <= 526:
                self.brushSize = 4
                b, g, r = int(self.b), int(self.g), int(self.r)
                cv2.rectangle(self.img, (417, 23), (475, 80), (b, g, r), -1)
            elif 527 <= x <= 545:
                self.brushSize = 7
                b, g, r = int(self.b), int(self.g), int(self.r)
                cv2.rectangle(self.img, (417, 23), (475, 80), (b, g, r), -1)
            elif 546 <= x <= 560:
                self.brushSize = 9
                b, g, r = int(self.b), int(self.g), int(self.r)
                cv2.rectangle(self.img, (417, 23), (475, 80), (b, g, r), -1)
            elif 561 <= x <= 578:
                self.brushSize = 12
                b, g, r = int(self.b), int(self.g), int(self.r)
                cv2.rectangle(self.img, (417, 23), (475, 80), (b, g, r), -1)
            elif 579 <= x <= 600:
                self.brushSize = 15
                b, g, r = int(self.b), int(self.g), int(self.r)
                cv2.rectangle(self.img, (417, 23), (475, 80), (b, g, r), -1)
            elif 601 <= x <= 632 and y <= 33:
                self.tool = 'brush'
                b, g, r = int(self.b), int(self.g), int(self.r)
                cv2.rectangle(self.img, (417, 23), (475, 80), (b, g, r), -1)
            elif 601 <= x <= 632 and 34 <= y <= 66:
                self.tool = 'rectangle'
                b, g, r = int(self.b), int(self.g), int(self.r)
                cv2.rectangle(self.img, (417, 23), (475, 80), (b, g, r), -1)
            elif 601 <= x <= 632 and y > 66:
                self.tool = 'fill'
                b, g, r = int(self.b), int(self.g), int(self.r)
                cv2.rectangle(self.img, (417, 23), (475, 80), (b, g, r), -1)
            elif x > 633 and y <= 33:
                self.tool = 'dropper'
                b, g, r = int(self.b), int(self.g), int(self.r)
                cv2.rectangle(self.img, (417, 23), (475, 80), (b, g, r), -1)
            elif x > 633 and 34 <= y <= 66:
                self.tool = 'ellipse'
                b, g, r = int(self.b), int(self.g), int(self.r)
                cv2.rectangle(self.img, (417, 23), (475, 80), (b, g, r), -1)
            elif x > 633 and 67 <= y <= 100:
                self.tool = 'line'
                b, g, r = int(self.b), int(self.g), int(self.r)
                cv2.rectangle(self.img, (417, 23), (475, 80), (b, g, r), -1)

            if self.tool == 'brush':
                cv2.rectangle(self.img, (601, 1), (632, 33), (255, 255, 255), 1)
            elif self.tool == 'rectangle':
                cv2.rectangle(self.img, (601, 34), (632, 66), (255, 255, 255), 1)
            elif self.tool == 'fill':
                cv2.rectangle(self.img, (601, 67), (632, 99), (255, 255, 255), 1)
            elif self.tool == 'dropper':
                cv2.rectangle(self.img, (633, 1), (665, 33), (255, 255, 255), 1)
            elif self.tool == 'ellipse':
                cv2.rectangle(self.img, (633, 34), (665, 66), (255, 255, 255), 1)
            elif self.tool == 'line':
                cv2.rectangle(self.img, (633, 67), (665, 99), (255, 255, 255), 1)

            if self.brushSize == 1:
                cv2.rectangle(self.img, (493, 1), (511, 99), (0, 225, 255), 2)
            if self.brushSize == 4:
                cv2.rectangle(self.img, (512, 1), (526, 99), (0, 225, 255), 2)
            if self.brushSize == 7:
                cv2.rectangle(self.img, (527, 1), (545, 99), (0, 225, 255), 2)
            if self.brushSize == 9:
                cv2.rectangle(self.img, (546, 1), (560, 99), (0, 225, 255), 2)
            if self.brushSize == 12:
                cv2.rectangle(self.img, (561, 1), (578, 99), (0, 225, 255), 2)
            if self.brushSize == 15:
                cv2.rectangle(self.img, (579, 1), (600, 99), (0, 225, 255), 2)

            cv2.imshow('tools', self.img)

    def set_color(self, r, g, b):
        self.img = cv2.imread('paint_pallete.jpg')
        cv2.namedWindow('tools')
        cv2.setMouseCallback('tools', self.select_color)
        cv2.rectangle(self.img, (417, 23), (475, 80), (b, g, r), -1)

        if self.tool == 'brush':
            cv2.rectangle(self.img, (601, 1), (632, 33), (255, 255, 255), 1)
        elif self.tool == 'rectangle':
            cv2.rectangle(self.img, (601, 34), (632, 66), (255, 255, 255), 1)
        elif self.tool == 'fill':
            cv2.rectangle(self.img, (601, 67), (632, 99), (255, 255, 255), 1)
        elif self.tool == 'dropper':
            cv2.rectangle(self.img, (633, 1), (665, 33), (255, 255, 255), 1)
        elif self.tool == 'ellipse':
            cv2.rectangle(self.img, (633, 34), (665, 66), (255, 255, 255), 1)
        elif self.tool == 'line':
            cv2.rectangle(self.img, (633, 67), (665, 99), (255, 255, 255), 1)

        if self.brushSize == 1:
            cv2.rectangle(self.img, (493, 1), (511, 99), (0, 225, 255), 2)
        if self.brushSize == 4:
            cv2.rectangle(self.img, (512, 1), (526, 99), (0, 225, 255), 2)
        if self.brushSize == 7:
            cv2.rectangle(self.img, (527, 1), (545, 99), (0, 225, 255), 2)
        if self.brushSize == 9:
            cv2.rectangle(self.img, (546, 1), (560, 99), (0, 225, 255), 2)
        if self.brushSize == 12:
            cv2.rectangle(self.img, (561, 1), (578, 99), (0, 225, 255), 2)
        if self.brushSize == 15:
            cv2.rectangle(self.img, (579, 1), (600, 99), (0, 225, 255), 2)

        cv2.imshow('tools', self.img)

    # method for checking mouse cLicks
    def mousePressEvent(self, event):
        # if left mouse button is pressed
        if event.button() == Qt.LeftButton:
            # make drawing flag true
            self.undo_index = 0
            self.undo_levels += 1
            self.undo_stack.append(self.image.copy())
            # self.image.save('paint_undo.jpg')
            if self.tool == 'brush':
                self.drawing = True
            elif self.tool == 'rectangle':
                self.beginpoint = event.pos()
                self.endpoint = self.beginpoint
                self.drawrect = True
            elif self.tool == 'ellipse':
                self.beginpoint = event.pos()
                self.endpoint = self.beginpoint
                self.drawellipse = True
            elif self.tool == 'line':
                self.beginpoint = event.pos()
                self.endpoint = self.beginpoint
                self.drawline = True
            elif self.tool == 'dropper':
                self.brushColor = QColor.fromRgba(self.image.pixel(QPoint(event.pos())))
                r, g, b, a = QColor.getRgb(self.brushColor)
                self.r, self.g, self.b = r, g, b
                self.set_color(r, g, b)
            elif self.tool == 'zoom':
                self.zoom = not self.zoom
                if self.zoom:
                    self.image = self.image.scaled(2 * self.image.size())
                else:
                    self.image = self.image.scaled(0.5 * self.image.size())
                self.update()
            elif self.tool == 'fill':
                '''
                Fill code from: https://www.pythonguis.com/faq/implementing-qpainter-flood-fill-pyqt5pyside/
                '''
                w, h = self.image.width(), self.image.height()

                # Get our target color from origin.
                target_color = self.image.pixel(event.pos())
                x, y = event.pos().x(), event.pos().y()
                have_seen = set()
                queue = [(x, y)]

                def get_cardinal_points(have_seen, center_pos):
                    points = []
                    cx, cy = center_pos
                    for x, y in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                        xx, yy = cx + x, cy + y
                        if (xx >= 0 and xx < w and yy >= 0 and yy < h and (xx, yy) not in have_seen):
                            points.append((xx, yy))
                            have_seen.add((xx, yy))

                    return points

                # Now perform the search and fill.
                p = QPainter(self.image)
                p.setPen(QColor.fromRgbF(self.r / 255, self.g / 255, self.b / 255, 1))

                while queue:
                    x, y = queue.pop()
                    if self.image.pixel(x, y) == target_color:
                        p.drawPoint(QPoint(x, y))
                        # Prepend to the queue
                        queue[0:0] = get_cardinal_points(have_seen, (x, y))
                        # or append,
                        # queue.extend(get_cardinal_points(have_seen, (x, y))
                self.update()
            # make last point to the point of cursor
            self.lastPoint = event.pos()
            self.update()

    # method for tracking mouse activity
    def mouseMoveEvent(self, event):
        # checking if left button is pressed and drawing flag is true
        if (event.buttons() & Qt.LeftButton) & self.drawing:
            # creating painter object
            painter = QPainter(self.image)
            # set the pen of the painter
            painter.setPen(QPen(self.brushColor, self.brushSize,
                                Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            # draw line from the last point of cursor to the current point
            # this will draw only one step
            painter.drawLine(self.lastPoint, event.pos())
            # change the last point
            self.lastPoint = event.pos()
            # update
            self.update()
        elif (event.buttons() & Qt.LeftButton) & self.drawrect:
            self.endpoint = event.pos()
            self.update()
        elif (event.buttons() & Qt.LeftButton) & self.drawellipse:
            self.endpoint = event.pos()
            self.update()
        elif (event.buttons() & Qt.LeftButton) & self.drawline:
            self.endpoint = event.pos()
            self.update()
    # method for mouse left button release
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            # make drawing flag false
            self.drawing = False
            if self.drawrect:
                self.drawrect = False
                painter = QPainter(self.image)
                painter.setPen(QPen(self.brushColor, self.brushSize,
                                    Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                rect = QRect(self.beginpoint, self.endpoint)
                painter.drawRect(rect.normalized())
                self.beginpoint, self.endpoint = QPoint(0, 0), QPoint(0, 0)
            if self.drawline:
                self.drawline = False
                painter = QPainter(self.image)
                painter.setPen(QPen(self.brushColor, self.brushSize,
                                    Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                # rect = QRect(self.beginpoint, self.endpoint)
                painter.drawLine(self.beginpoint, self.endpoint)
                self.beginpoint, self.endpoint = QPoint(0, 0), QPoint(0, 0)
            if self.drawellipse:
                self.drawellipse = False
                painter = QPainter(self.image)
                painter.setPen(QPen(self.brushColor, self.brushSize,
                                    Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                # ellipse = QEllipse(self.beginpoint, self.endpoint)
                painter.drawEllipse(self.beginpoint, self.endpoint.x() - self.beginpoint.x(), self.endpoint.y() - self.beginpoint.y())
                self.beginpoint, self.endpoint = QPoint(0, 0), QPoint(0, 0)

    # paint event
    def paintEvent(self, event):
        # create a canvas
        canvasPainter = QPainter(self)

        # draw rectangle  on the canvas
        canvasPainter.drawImage(self.rect(), self.image, self.image.rect())

        if self.drawrect:
            if self.beginpoint != QPoint(0, 0) and self.endpoint != QPoint(0, 0):
                rect = QRect(self.beginpoint, self.endpoint)
                canvasPainter.drawRect(rect.normalized())
        self.update()

    def open(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File", "",
                                                  "Images (*.jpg *.jpeg *.bmp *.png *.tiff *.gif);;All files (*.*)")

        if fileName == "":
            return
        tmp = Image.open(fileName)
        width, height = tmp.size
        if height == 600:
            ratio = 1
        else:
            ratio = 800 / height
        newsize = (int(width * ratio), int(height * ratio))
        self.setGeometry(200, 200, int(width * ratio), int(height * ratio))
        tmp = tmp.resize(newsize)
        tmp = np.array(tmp)
        self.image = QImage(tmp, tmp.shape[1], tmp.shape[0], QImage.Format_RGB888)
        self.lastPoint = QPoint()
        self.update()

    def save(self):
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Image", "",
                                                  "PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*) ")

        if filePath == "":
            return
        self.image.save(filePath)

    # method for clearing every thing on canvas
    def clear(self):
        # make the whole canvas white
        self.image.fill(Qt.white)
        # clear the undo stack
        self.undo_index = 0
        self.undo_levels = 0
        self.undo_stack = []
        # update
        self.update()

    def undo(self):
        self.undo_index -= 1
        if self.undo_levels > 0 and self.undo_index * -1 <= len(self.undo_stack):
            self.image = self.undo_stack[self.undo_index]
            if self.undo_index * -1 == len(self.undo_stack):
                # clear the undo stack
                self.undo_index = 0
                self.undo_levels = 0
                self.undo_stack = []
        self.update()


# create pyqt5 app
App = QApplication(sys.argv)
# create the instance of our Window
window = Window()
# showing the window
window.show()
# start the app
sys.exit(App.exec())
