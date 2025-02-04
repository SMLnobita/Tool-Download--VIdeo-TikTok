from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLineEdit, QPushButton, QLabel, QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize  # Thêm QSize vào đây
from PyQt6.QtGui import QIcon, QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer
import yt_dlp
import sys
import os


class IconProvider:
    @staticmethod
    def get_download_icon():
        svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <path fill="white" d="M12 3C12.5523 3 13 3.44772 13 4V12.5858L15.2929 10.2929C15.6834 9.90237 16.3166 9.90237 16.7071 10.2929C17.0976 10.6834 17.0976 11.3166 16.7071 11.7071L12.7071 15.7071C12.3166 16.0976 11.6834 16.0976 11.2929 15.7071L7.29289 11.7071C6.90237 11.3166 6.90237 10.6834 7.29289 10.2929C7.68342 9.90237 8.31658 9.90237 8.70711 10.2929L11 12.5858V4C11 3.44772 11.4477 3 12 3ZM5 16C5.55228 16 6 16.4477 6 17V19C6 19.5523 6.44772 20 7 20H17C17.5523 20 18 19.5523 18 19V17C18 16.4477 18.4477 16 19 16C19.5523 16 20 16.4477 20 17V19C20 20.6569 18.6569 22 17 22H7C5.34315 22 4 20.6569 4 19V17C4 16.4477 4.44772 16 5 16Z"/>
        </svg>'''
        return IconProvider._svg_to_icon(svg_content)

    @staticmethod
    def get_folder_icon():
        svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <path fill="white" d="M4 4C3.44772 4 3 4.44772 3 5V19C3 19.5523 3.44772 20 4 20H20C20.5523 20 21 19.5523 21 19V8C21 7.44772 20.5523 7 20 7H11.4142L9.41421 5H4ZM1 5C1 3.34315 2.34315 2 4 2H10.4142L12.4142 4H20C21.6569 4 23 5.34315 23 7V19C23 20.6569 21.6569 22 20 22H4C2.34315 22 1 20.6569 1 19V5Z"/>
        </svg>'''
        return IconProvider._svg_to_icon(svg_content)

    @staticmethod
    def _svg_to_icon(svg_content):
        renderer = QSvgRenderer()
        renderer.load(bytes(svg_content, 'utf-8'))
        
        pixmap = QPixmap(24, 24)  # Kích thước icon
        pixmap.fill(Qt.GlobalColor.transparent)  # Nền trong suốt
        
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        
        return QIcon(pixmap)

class DownloadWorker(QThread):
    finished = pyqtSignal()
    progress = pyqtSignal(float)
    error = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url
        self.save_folder = "videos"
        
    def sanitize_filename(self, title):
        # Lấy timestamp để tạo tên file unique
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Chỉ giữ lại 30 ký tự đầu của title, loại bỏ các ký tự đặc biệt
        clean_title = re.sub(r'[^\w\s-]', '', title)[:30]
        clean_title = re.sub(r'[-\s]+', '_', clean_title)
        
        # Kết hợp timestamp và title
        return f"{timestamp}_{clean_title}"

    def run(self):
        try:
            if not os.path.exists(self.save_folder):
                os.makedirs(self.save_folder)

            ydl_opts = {
                'outtmpl': os.path.join(self.save_folder, '%(title)s.%(ext)s'),
                'restrictfilenames': True,
                'format': 'bestvideo+bestaudio/best',
                'progress_hooks': [self.progress_hook],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes', 0)
            
            if total == 0:
                total = d.get('total_bytes_estimate', 0)
            
            if total > 0:
                percentage = (downloaded / total) * 100
                self.progress.emit(percentage)

class TikTokDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.save_folder = "videos"
        self.initUI()

    def initUI(self):
        self.setWindowTitle('TikTok Video Downloader')
        self.setWindowIcon(IconProvider.get_download_icon())
        self.setMinimumSize(500, 300)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
            QWidget {
                background-color: #121212;
                color: #ffffff;
            }
            QLineEdit {
                padding: 12px;
                border: 2px solid #333333;
                border-radius: 8px;
                background-color: #1e1e1e;
                color: #ffffff;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #2563eb;
            }
            QPushButton {
                padding: 12px 24px;
                background-color: rgb(44, 72, 254);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                min-width: 140px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:pressed {
                background-color: #1e40af;
            }
            QPushButton:disabled {
                background-color: #666666;
            }
            QProgressBar {
                border: 2px solid #333333;
                border-radius: 8px;
                text-align: center;
                background-color: #1e1e1e;
                color: #ffffff;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #2563eb;
                border-radius: 6px;
            }
            QLabel {
                color: #2563eb;
            }
        """)

        # Widget chính
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Logo và tiêu đề
        title_label = QLabel('TikTok Video Downloader')
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2563eb;
            margin-bottom: 20px;
        """)
        layout.addWidget(title_label)

        # URL input
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText('Nhập URL video TikTok...')
        layout.addWidget(self.url_input)

        # Container cho các nút
        button_container = QHBoxLayout()
        button_container.setSpacing(15)
        button_container.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Nút tải xuống với icon
        self.download_button = QPushButton('  Tải xuống')
        self.download_button.setIcon(IconProvider.get_download_icon())
        self.download_button.setIconSize(QSize(20, 20))
        self.download_button.clicked.connect(self.start_download)
        button_container.addWidget(self.download_button)

        # Nút mở thư mục với icon
        self.folder_button = QPushButton('  Mở thư mục')
        self.folder_button.setIcon(IconProvider.get_folder_icon())
        self.folder_button.setIconSize(QSize(20, 20))
        self.folder_button.clicked.connect(self.open_folder)
        button_container.addWidget(self.folder_button)

        layout.addLayout(button_container)

        # Thanh tiến trình
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)

        # Thông báo trạng thái
        self.status_label = QLabel('')
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet('color: #2563eb;')
        layout.addWidget(self.status_label)

        layout.addStretch()

    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            self.status_label.setText('Vui lòng nhập URL video!')
            return

        self.download_button.setEnabled(False)
        self.status_label.setText('Đang tải xuống...')
        self.progress_bar.setValue(0)

        self.worker = DownloadWorker(url)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.download_finished)
        self.worker.error.connect(self.download_error)
        self.worker.start()

    def update_progress(self, percentage):
        self.progress_bar.setValue(int(percentage))

    def download_finished(self):
        self.download_button.setEnabled(True)
        self.status_label.setText('Tải xuống hoàn tất!')
        self.progress_bar.setValue(100)
        self.url_input.clear()

    def download_error(self, error_msg):
        self.download_button.setEnabled(True)
        self.status_label.setText(f'Lỗi: {error_msg}')
        self.progress_bar.setValue(0)

    def open_folder(self):
        """Mở thư mục chứa video đã tải"""
        try:
            # Tạo thư mục nếu chưa tồn tại
            if not os.path.exists(self.save_folder):
                os.makedirs(self.save_folder)
            
            # Mở thư mục theo hệ điều hành
            if sys.platform == 'win32':
                os.startfile(self.save_folder)
            elif sys.platform == 'darwin':  # macOS
                os.system(f'open "{self.save_folder}"')
            else:  # Linux và các hệ điều hành khác
                os.system(f'xdg-open "{self.save_folder}"')
                
            self.status_label.setText('Đã mở thư mục chứa video')
        except Exception as e:
            self.status_label.setText(f'Lỗi khi mở thư mục: {str(e)}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TikTokDownloader()
    window.show()
    sys.exit(app.exec())