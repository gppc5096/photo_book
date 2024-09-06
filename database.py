import sqlite3
import os

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            self.create_tables()
        except sqlite3.Error as e:
            print(f"데이터베이스 연결 오류: {e}")
            raise

    def create_tables(self):
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )
            ''')

            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS photos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT NOT NULL,
                    name TEXT NOT NULL,
                    category_id INTEGER,
                    FOREIGN KEY (category_id) REFERENCES categories (id)
                )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"테이블 생성 오류: {e}")
            raise

    def initialize_database(self):
        if not os.path.exists(self.db_path):
            try:
                # 테이블 생성
                self.create_tables()

                # 기본 카테고리 추가
                default_categories = ['가족', '여행', '음식', '풍경', '기타']
                for category in default_categories:
                    self.add_category(category)

                self.conn.commit()
                print("데이터베이스가 성공적으로 초기화되었습니다.")
            except sqlite3.Error as e:
                print(f"데이터베이스 초기화 중 오류 발생: {e}")
                self.conn.rollback()

    def add_category(self, category_name):
        try:
            self.cursor.execute("INSERT INTO categories (name) VALUES (?)", (category_name,))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            print(f"카테고리 '{category_name}'이(가) 이미 존재합니다.")
            return False
        except sqlite3.Error as e:
            print(f"카테고리 추가 오류: {e}")
            self.conn.rollback()
            return False

    def get_categories(self):
        try:
            self.cursor.execute("SELECT name FROM categories")
            return [row[0] for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"카테고리 조회 오류: {e}")
            return []

    def edit_category(self, old_name, new_name):
        try:
            self.cursor.execute("UPDATE categories SET name = ? WHERE name = ?", (new_name, old_name))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"카테고리 수정 오류: {e}")
            self.conn.rollback()
            return False

    def delete_category(self, category_name):
        try:
            self.cursor.execute("DELETE FROM categories WHERE name = ?", (category_name,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"카테고리 삭제 오류: {e}")
            self.conn.rollback()
            return False

    def add_photo(self, photo_path, category_name):
        try:
            self.cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
            category_id = self.cursor.fetchone()
            if category_id:
                photo_name = os.path.basename(photo_path)
                self.cursor.execute("INSERT INTO photos (path, name, category_id) VALUES (?, ?, ?)", 
                                    (photo_path, photo_name, category_id[0]))
                self.conn.commit()
                return True
            else:
                print(f"카테고리 '{category_name}'을(를) 찾을 수 없습니다.")
                return False
        except sqlite3.Error as e:
            print(f"사진 추가 오류: {e}")
            self.conn.rollback()
            return False

    def get_photos_by_category(self, category_name):
        try:
            self.cursor.execute("""
                SELECT photos.id, photos.path, photos.name
                FROM photos
                JOIN categories ON photos.category_id = categories.id
                WHERE categories.name = ?
            """, (category_name,))
            return [{'id': row[0], 'path': row[1], 'name': row[2]} for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"사진 조회 오류: {e}")
            return []

    def close(self):
        if self.conn:
            self.conn.close()
