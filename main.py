import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox, QInputDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from gui import PhotoManagerGUI
from database import Database
from file_handler import FileHandler
from slideshow import SlideShow  # SlideShow 클래스 추가

# 실행 파일 또는 스크립트의 디렉토리 경로 얻기
if getattr(sys, 'frozen', False):
    # 실행 파일로 실행될 때
    application_path = os.path.dirname(sys.executable)
else:
    # 스크립트로 실행될 때
    application_path = os.path.dirname(os.path.abspath(__file__))

# 데이터베이스 파일 경로 설정
DATABASE_PATH = os.path.join(application_path, 'photo_manager.db')

class PhotoManager:
    def __init__(self, db_path):
        self.db = Database(db_path)
        self.db.connect()
        if not os.path.exists(db_path):
            self.db.initialize_database()  # 데이터베이스 초기화
        self.file_handler = FileHandler(os.path.dirname(db_path))
        self.gui = PhotoManagerGUI()
        self.setup_connections()
        self.load_categories()  # 카테고리 로드

    def setup_connections(self):
        self.gui.add_category_btn.clicked.connect(self.add_category)
        self.gui.edit_category_btn.clicked.connect(self.edit_category)
        self.gui.delete_category_btn.clicked.connect(self.delete_category)
        self.gui.add_photo_btn.clicked.connect(self.add_photo)
        self.gui.download_btn.clicked.connect(self.download_photo)
        self.gui.category_list.itemClicked.connect(self.load_category_photos)
        self.gui.photo_list.itemClicked.connect(self.show_photo_preview)
        self.gui.photo_list.itemEntered.connect(self.show_photo_preview)  # 커서가 파일 위에 올 때
        self.gui.photo_list.currentItemChanged.connect(self.show_photo_preview)  # 키보드 상/하 화살표

        # 스페이스바로 슬라이드쇼 시작
        self.gui.photo_list.keyPressEvent = self.keyPressEvent

    def load_categories(self):
        categories = self.db.get_categories()
        self.gui.update_category_list(categories)

    def add_category(self):
        category_name, ok = QInputDialog.getText(self.gui, '카테고리 추가', '새 카테고리 이름을 입력하세요:')
        if ok and category_name:
            self.db.add_category(category_name)
            self.load_categories()

    def edit_category(self):
        current_category = self.gui.get_selected_category()
        if current_category:
            new_name, ok = QInputDialog.getText(self.gui, '카테고리 수정', '새 이름을 입력하세요:', text=current_category)
            if ok and new_name:
                self.db.edit_category(current_category, new_name)
                self.load_categories()

    def delete_category(self):
        category = self.gui.get_selected_category()
        if category:
            confirm = QMessageBox.question(self.gui, '카테고리 삭제', f'"{category}" 카테고리를 삭제하시겠습니까?',
                                           QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                self.db.delete_category(category)
                self.load_categories()

    def add_photo(self):
        file_path = self.gui.get_photo_file()  # GUI에서 파일 선택
        category = self.gui.get_selected_category()  # GUI에서 선택된 카테고리 가져오기
        if file_path and category:
            self.db.add_photo(file_path, category)
            photos = self.db.get_photos_by_category(category)  # 카테고리의 모든 사진 가져오기
            self.gui.update_photo_list(photos)  # 사진 목록 업데이트

    def download_photo(self):
        selected_photo = self.gui.get_selected_photo()  # GUI에서 선택된 사진 정보 가져오기
        if selected_photo:
            download_path = self.file_handler.download_photo(selected_photo['path'])
            if download_path:
                self.gui.show_download_success(download_path)
            else:
                self.gui.show_error("사진 다운로드에 실패했습니다.")
        else:
            self.gui.show_error("다운로드할 사진을 선택해주세요.")

    def load_category_photos(self, category_item):
        category_name = category_item.text()
        photos = self.db.get_photos_by_category(category_name)
        self.gui.update_photo_list(photos)

    def show_photo_preview(self, photo_item):
        if photo_item:
            photo_path = photo_item.data(Qt.UserRole)  # 사진 경로 가져오기
            if photo_path:
                preview_image = self.file_handler.load_photo(photo_path)
                if preview_image:
                    self.gui.update_preview(preview_image)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            photo_paths = [self.gui.photo_list.item(i).data(Qt.UserRole)
                           for i in range(self.gui.photo_list.count())]
            if photo_paths:
                self.slideshow = SlideShow(photo_paths)
                self.slideshow.exec_()

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(os.path.join(application_path, 'photos.ico')))  # 아이콘 설정
    photo_manager = PhotoManager(DATABASE_PATH)
    photo_manager.gui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
