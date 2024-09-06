import os
import shutil
from PIL import Image
from config import RESOURCES_DIR, DEFAULT_DOWNLOAD_DIR
from PyQt5.QtGui import QImage

class FileHandler:
    def __init__(self, base_path):
        self.base_path = base_path

    @staticmethod
    def save_photo(source_path, category):
        try:
            # 카테고리 폴더가 없으면 생성
            category_path = os.path.join(RESOURCES_DIR, category)
            os.makedirs(category_path, exist_ok=True)

            # 파일 이름 추출 및 대상 경로 생성
            file_name = os.path.basename(source_path)
            destination_path = os.path.join(category_path, file_name)

            # 파일 복사
            shutil.copy2(source_path, destination_path)

            return destination_path
        except (FileNotFoundError, PermissionError, IOError) as e:
            print(f"파일 저장 중 오류 발생: {e}")
            return None

    @staticmethod
    def load_photo(file_path):
        try:
            image = QImage(file_path)
            if image.isNull():
                print(f"이미지를 불러올 수 없습니다: {file_path}")
                return None
            return image
        except Exception as e:
            print(f"이미지 로드 중 오류 발생: {e}")
            return None

    @staticmethod
    def download_photo(source_path, custom_name=None):
        try:
            file_name = custom_name or os.path.basename(source_path)
            destination_path = os.path.join(DEFAULT_DOWNLOAD_DIR, file_name)

            # 파일 복사
            shutil.copy2(source_path, destination_path)

            return destination_path
        except (FileNotFoundError, PermissionError, IOError) as e:
            print(f"파일 다운로드 중 오류 발생: {e}")
            return None

    @staticmethod
    def get_photo_list(category):
        category_path = os.path.join(RESOURCES_DIR, category)
        try:
            return [f for f in os.listdir(category_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        except FileNotFoundError:
            print(f"카테고리 폴더를 찾을 수 없습니다: {category}")
            return []

    def copy_file(self, src_path, dest_path):
        try:
            full_dest_path = os.path.join(self.base_path, dest_path)
            os.makedirs(os.path.dirname(full_dest_path), exist_ok=True)
            shutil.copy2(src_path, full_dest_path)
            return True
        except Exception as e:
            print(f"파일 복사 중 오류 발생: {e}")
            return False

    def delete_file(self, file_path):
        try:
            full_file_path = os.path.join(self.base_path, file_path)
            os.remove(full_file_path)
            return True
        except Exception as e:
            print(f"파일 삭제 중 오류 발생: {e}")
            return False

if __name__ == "__main__":
    # 테스트 코드
    import tempfile
    from PIL import Image

    # 임시 테스트 이미지 생성
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
        test_image = Image.new('RGB', (100, 100), color='red')
        test_image.save(temp_file.name)
        test_image_path = temp_file.name

    print(f"테스트 이미지 생성: {test_image_path}")

    result = FileHandler.save_photo(test_image_path, "test_category")
    if result:
        print(f"파일이 성공적으로 저장되었습니다: {result}")
    else:
        print("파일 저장에 실패했습니다.")

    if result:
        loaded_image = FileHandler.load_photo(result)
        if loaded_image:
            print("이미지가 성공적으로 로드되었습니다.")
        else:
            print("이미지 로드에 실패했습니다.")

        download_result = FileHandler.download_photo(result, "downloaded_image.jpg")
        if download_result:
            print(f"파일이 성공적으로 다운로드되었습니다: {download_result}")
        else:
            print("파일 다운로드에 실패했습니다.")

    photo_list = FileHandler.get_photo_list("test_category")
    print(f"카테고리의 사진 목록: {photo_list}")
