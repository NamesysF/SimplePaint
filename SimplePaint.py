import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QColorDialog, QWidget, QSpinBox, QLabel, QFileDialog
from PyQt6.QtGui import QPainter, QPen, QColor, QImage
from PyQt6.QtCore import Qt, QPoint
from collections import deque

class PaintArea(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StaticContents)
        self.drawing = False
        self.last_point = QPoint()
        self.pen_color = QColor(0, 0, 0)
        self.pen_width = 2
        self.image = QImage(800, 600, QImage.Format.Format_RGB32)
        self.image.fill(Qt.GlobalColor.white)
        self.history = deque(maxlen=10)
        self.redo_stack = deque()
        self.current_file = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(0, 0, self.image)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.last_point = event.pos()
            self.save_state()

    def mouseMoveEvent(self, event):
        if self.drawing:
            painter = QPainter(self.image)
            painter.setPen(QPen(self.pen_color, self.pen_width, Qt.PenStyle.SolidLine))
            painter.drawLine(self.last_point, event.pos())
            self.last_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False

    def set_pen_color(self, color):
        self.pen_color = color

    def set_pen_width(self, width):
        self.pen_width = width

    def clear_canvas(self):
        self.image.fill(Qt.GlobalColor.white)
        self.update()

    def save_state(self):
        self.history.append(self.image.copy())
        self.redo_stack.clear()

    def undo(self):
        if self.history:
            self.redo_stack.append(self.image.copy())
            self.image = self.history.pop()
            self.update()

    def redo(self):
        if self.redo_stack:
            self.history.append(self.image.copy())
            self.image = self.redo_stack.pop()
            self.update()

    def save_image(self, file_path):
        self.image.save(file_path)
        self.current_file = file_path

    def save_as(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save As", "", "PNG Files (*.png);;All Files (*)")
        if file_path:
            self.save_image(file_path)

    def save(self):
        if self.current_file:
            self.save_image(self.current_file)
        else:
            self.save_as()

    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open", "", "PNG Files (*.png);;All Files (*)")
        if file_path:
            self.image.load(file_path)
            self.current_file = file_path
            self.update()

class PaintApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SimplePaint")
        self.paint_area = PaintArea()
        self.setCentralWidget(self.paint_area)

        self.setMinimumSize(self.paint_area.image.size())
        self.setGeometry(100, 100, 800, 600)

        self.init_ui()

    def init_ui(self):
        toolbar = self.addToolBar("Tools")
        color_button = QPushButton("Choose Color")
        color_button.clicked.connect(self.choose_color)
        toolbar.addWidget(color_button)

        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.paint_area.clear_canvas)
        toolbar.addWidget(clear_button)

        self.pen_width_spinner = QSpinBox()
        self.pen_width_spinner.setRange(1, 50)
        self.pen_width_spinner.setValue(self.paint_area.pen_width)
        self.pen_width_spinner.valueChanged.connect(self.paint_area.set_pen_width)
        toolbar.addWidget(self.pen_width_spinner)

        self.pen_width_label = QLabel(f"Pen Width: {self.paint_area.pen_width}")
        self.pen_width_spinner.valueChanged.connect(lambda: self.pen_width_label.setText(f"Pen Width: {self.pen_width_spinner.value()}"))
        toolbar.addWidget(self.pen_width_label)

        undo_button = QPushButton("Undo")
        undo_button.clicked.connect(self.paint_area.undo)
        toolbar.addWidget(undo_button)

        redo_button = QPushButton("Redo")
        redo_button.clicked.connect(self.paint_area.redo)
        toolbar.addWidget(redo_button)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.paint_area.save)
        toolbar.addWidget(save_button)

        save_as_button = QPushButton("Save As")
        save_as_button.clicked.connect(self.paint_area.save_as)
        toolbar.addWidget(save_as_button)

        open_button = QPushButton("Open")
        open_button.clicked.connect(self.paint_area.open_image)
        toolbar.addWidget(open_button)

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.paint_area.set_pen_color(color)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PaintApp()
    window.show()
    sys.exit(app.exec())
