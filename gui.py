import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QListWidget, QLabel, QPushButton, QFileDialog,
                             QDesktopWidget, QListWidgetItem, QMessageBox, 
                             QSpacerItem, QSizePolicy, QInputDialog, QFrame, QApplication)
from PyQt5.QtGui import QPixmap, QImage, QPalette, QColor, QFont
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QEvent
from slideshow import SlideShow

class PhotoManagerGUI(QMainWindow):
    photo_selected = pyqtSignal(QListWidgetItem)
    start_slideshow = pyqtSignal(list)  # 새로운 시그널 추가

    def __init__(self):
        super().__init__()
        self.category_list = QListWidget()
        self.photo_list = QListWidget()
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.preview_label.setMinimumSize(200, 200)  # 미리보기의 최소 크기 설정
        self.initUI()
        self.slideshow = None

        # 이벤트 필터 추가
        self.photo_list.setMouseTracking(True)
        self.photo_list.installEventFilter(self)

    def initUI(self):
        self.setWindowTitle('나종춘의 사진관리프로그램')
        self.setGeometry(100, 100, 800, 600)
        self.center()

        # 배경색 설정
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor('black'))
        palette.setColor(QPalette.WindowText, QColor('white'))
        palette.setColor(QPalette.Base, QColor('black'))
        palette.setColor(QPalette.Text, QColor('white'))
        self.setPalette(palette)

        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # 제목 추가
        title_label = QLabel('사진관리프로그램')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont('Arial', 15))
        title_label.setStyleSheet('color: #9fd1e3;')
        main_layout.addWidget(title_label)

        # 빈 공간 추가
        main_layout.addSpacing(20)

        # 기존 레이아웃
        content_layout = QHBoxLayout()

        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel('카테고리'))
        left_layout.addWidget(self.category_list)

        # 버튼 스타일 정의
        button_style = """
            QPushButton {{
                font-size: 10pt;
                border-radius: 15px;
                padding: 5px 10px;
                color: black;
                background-color: {bg_color};
            }}
            QPushButton:hover {{
                background-color: #E0E0E0;
            }}
        """

        # 파스텔 색상 정의
        pastel_colors = [
            "#FFB3BA",  # 파스텔 핑크
            "#BAFFC9",  # 파스텔 그린
            "#BAE1FF",  # 파스텔 블루
            "#FFFFBA",  # 파스텔 옐로우
            "#FFD9BA"   # 파스텔 오렌지
        ]

        # 버튼 생성 및 스타일 적용
        self.add_category_btn = self.create_styled_button('추가', button_style.format(bg_color=pastel_colors[0]))
        self.edit_category_btn = self.create_styled_button('수정', button_style.format(bg_color=pastel_colors[1]))
        self.delete_category_btn = self.create_styled_button('삭제', button_style.format(bg_color=pastel_colors[2]))
        self.add_photo_btn = self.create_styled_button('사진 추가', button_style.format(bg_color=pastel_colors[3]))
        self.download_btn = self.create_styled_button('다운로드', button_style.format(bg_color=pastel_colors[4]))

        category_btn_layout = QHBoxLayout()
        category_btn_layout.addWidget(self.add_category_btn)
        category_btn_layout.addWidget(self.edit_category_btn)
        category_btn_layout.addWidget(self.delete_category_btn)
        left_layout.addLayout(category_btn_layout)

        left_widget.setLayout(left_layout)

        center_widget = QWidget()
        center_layout = QVBoxLayout()
        center_layout.addWidget(QLabel('사진파일'))
        center_layout.addWidget(self.photo_list)
        self.add_photo_btn = self.create_styled_button('사진 추가', button_style.format(bg_color=pastel_colors[3]))
        center_layout.addWidget(self.add_photo_btn)
        center_widget.setLayout(center_layout)

        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel('미리보기'))
        right_layout.addWidget(self.preview_label)
        self.download_btn = self.create_styled_button('다운로드', button_style.format(bg_color=pastel_colors[4]))
        right_layout.addWidget(self.download_btn)
        right_widget.setLayout(right_layout)

        content_layout.addWidget(left_widget)
        content_layout.addWidget(center_widget)
        content_layout.addWidget(right_widget)

        main_layout.addLayout(content_layout)

        # 인용구와 종료 버튼을 포함하는 하단 레이아웃
        bottom_layout = QHBoxLayout()

        # 종료 버튼 추가
        self.exit_btn = self.create_styled_button('종료', button_style.format(bg_color=pastel_colors[0]))
        self.exit_btn.setFixedSize(80, 30)  # 버튼 크기 고정
        self.exit_btn.clicked.connect(self.close)  # 종료 버튼 클릭 시 창 닫기
        bottom_layout.addWidget(self.exit_btn)

        # 인용구 추가
        quote_label = QLabel('made by 나종춘(2024)')
        quote_label.setAlignment(Qt.AlignRight)
        quote_label.setFont(QFont('Arial', 11))
        quote_label.setStyleSheet('color: white;')
        bottom_layout.addWidget(quote_label)

        main_layout.addLayout(bottom_layout)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        self.photo_list.installEventFilter(self)

    def create_styled_button(self, text, style):
        button = QPushButton(text)
        button.setStyleSheet(style + """
            QPushButton {
                font-size: 10pt;
                border-radius: 15px;
            }
        """)
        return button

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def add_category(self):
        # 카테고리 추가 로직 구현
        pass

    def add_photo(self):
        # 사진 추가 로직 구현
        pass

    def download_photo(self):
        # 사진 다운로드 로직 구현
        pass

    def get_category_name(self, prompt="새 카테고리 이름을 입력하세요:"):
        category_name, ok = QInputDialog.getText(self, '카테고리 추가', prompt)
        if ok and category_name:
            return category_name
        return None

    def update_category_list(self, categories):
        self.category_list.clear()
        for category in categories:
            self.category_list.addItem(category)

    def get_photo_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            '사진 선택',
            '',
            'Image Files (*.png *.jpg *.jpeg *.bmp *.gif)'
        )
        return file_path
    
    def update_photo_list(self, photos):
        self.photo_list.clear()
        for photo in photos:
            item = QListWidgetItem(photo['name'])
            item.setData(Qt.UserRole, photo['path'])
            self.photo_list.addItem(item)

    def get_selected_category(self):
        selected_items = self.category_list.selectedItems()
        if selected_items:
            return selected_items[0].text()
        return None

    def update_preview(self, image_path):
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(self.preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.preview_label.setPixmap(scaled_pixmap)
            self.preview_label.setToolTip(f"원본 크기: {pixmap.width()}x{pixmap.height()}")
        else:
            self.preview_label.setText("이미지를 불러올 수 없습니다.")
            self.preview_label.setToolTip("")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.preview_label.pixmap():
            self.update_preview(self.preview_label.pixmap().toImage())

    def show_download_success(self, download_path):
        QMessageBox.information(self, "다운로드 완료", f"사진이 성공적으로 다운로드되었습니다:\n{download_path}")

    def show_error(self, message):
        QMessageBox.critical(self, "오류", message)

    def get_selected_photo(self):
        selected_items = self.photo_list.selectedItems()
        if selected_items:
            item = selected_items[0]
            return {
                'path': item.data(Qt.UserRole),
                'name': item.text()
            }
        return None

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Space:
            self.start_slideshow_signal()
            return True
        elif source == self.photo_list and event.type() == QEvent.MouseMove:
            item = self.photo_list.itemAt(event.pos())
            if item:
                self.photo_selected.emit(item)
        return super().eventFilter(source, event)

    def start_slideshow_signal(self):
        photo_paths = [self.photo_list.item(i).data(Qt.UserRole)
                       for i in range(self.photo_list.count())]
        self.start_slideshow.emit(photo_paths)

    def show_slideshow(self, photo_paths):
        if self.slideshow is None:
            self.slideshow = SlideShow(photo_paths)
            self.slideshow.closed.connect(self.on_slideshow_closed)
            self.slideshow.show()

    def on_slideshow_closed(self):
        self.slideshow = None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PhotoManagerGUI()
    ex.show()
    sys.exit(app.exec_())

