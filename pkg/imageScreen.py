import ctypes
import os
import random
import string
import logging
from PIL import ImageGrab
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter, QPen
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QMainWindow

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 获取屏幕的缩放比
def get_screen_scaling():
    return ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100

class ScreenshotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.begin = None
        self.end = None
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setWindowOpacity(0.2)
        self.setWindowState(Qt.WindowFullScreen)
        self.screen_scaling = get_screen_scaling()
        logging.info("初始化截图窗口")

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = event.pos()
        logging.info("鼠标按下事件")

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()
        logging.info("鼠标移动事件")

    def mouseReleaseEvent(self, event):
        self.close()
        if self.begin is not None and self.end is not None:
            x1, y1 = self.begin.x() * self.screen_scaling, self.begin.y() * self.screen_scaling
            x2, y2 = self.end.x() * self.screen_scaling, self.end.y() * self.screen_scaling
            
            if x1 > x2:
                x1, x2 = x2, x1
            if y1 > y2:
                y1, y2 = y2, y1
            
            if x1 == x2 or y1 == y2:
                logging.warning("未选择截图区域")
                self.screenshot_complete()
                return
            
            im = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            logging.info("截图完成")

            random_filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8)) + ".jpg"
            if not os.path.exists("images"):
                os.makedirs("images")
            im.save(os.path.join("images", random_filename))
            logging.info(f"截图保存到 {os.path.join('images', random_filename)}")

            # 调用截图完成后的回调函数
            self.screenshot_complete()
        else:
            logging.warning("未选择截图区域")
            self.screenshot_complete()
    
    def screenshot_complete(self):
        self.close()

    def paintEvent(self, event):
        if self.begin and self.end:
            painter = QPainter(self)
            pen = QPen(Qt.red)
            pen.setWidth(2)
            painter.setPen(pen)
            x1, y1 = int(self.begin.x() * self.screen_scaling), int(self.begin.y() * self.screen_scaling)
            x2, y2 = int(self.end.x() * self.screen_scaling), int(self.end.y() * self.screen_scaling)
            painter.drawRect(x1, y1, x2 - x1, y2 - y1)
            logging.info("绘制矩形")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        button = QPushButton("截图", self)
        button.clicked.connect(self.start_screenshot)
        layout.addWidget(button)

        self.setWindowTitle("截图工具")
        self.setGeometry(100, 100, 300, 200)

    def start_screenshot(self):
        logging.info("开始截图")
        self.hide()
        screenshot_widget = ScreenshotWidget()
        screenshot_widget.show()
        screenshot_widget.screenshot_complete = lambda: self.show_after_screenshot(screenshot_widget)

    def show_after_screenshot(self, screenshot_widget):
        logging.info("截图结束")
        screenshot_widget.close()
        self.show()

def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
    logging.info("程序退出")

if __name__ == '__main__':
    main()