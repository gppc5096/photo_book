from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap, QPalette, QColor
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QSize

class SlideShow(QWidget):
    closed = pyqtSignal()

    def __init__(self, photo_paths):
        super().__init__()
        self.photo_paths = photo_paths
        self.current_index = 0
        self.image_label = QLabel(self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('슬라이드쇼')
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)

        # 배경색을 검정색으로 설정
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor('black'))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        layout = QVBoxLayout()
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)
        self.setLayout(layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_image)
        self.timer.start(3000)  # 3초 간격

        self.show_image()

    def show_image(self):
        if 0 <= self.current_index < len(self.photo_paths):
            pixmap = QPixmap(self.photo_paths[self.current_index])
            if not pixmap.isNull():
                self.image_label.setPixmap(pixmap)
                self.image_label.setAlignment(Qt.AlignCenter)
                # 창 크기를 이미지 크기에 맞춤
                self.resize(pixmap.size())
            else:
                self.image_label.setText("이미지를 불러올 수 없습니다.")
                self.resize(400, 300)  # 기본 크기 설정

    def next_image(self):
        self.current_index = (self.current_index + 1) % len(self.photo_paths)
        self.show_image()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        self.timer.stop()
        self.closed.emit()
        super().closeEvent(event)

