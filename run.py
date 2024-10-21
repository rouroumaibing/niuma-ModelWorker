import os
import sys
from pynput import keyboard
import pyautogui
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QLineEdit, QFileDialog, QComboBox, QSizePolicy, QMenuBar, QAction
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QCursor
from PIL import ImageGrab
import ctypes
import string
import yaml
from pkg.autoCycle  import autoCycle, on_press
from pkg.imageScreen import ScreenshotWidget
from pkg.config import config_import_export_button_clicked


# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.controls = []  # 保存所有控件
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('牛马-ModelWorker')
        self.setGeometry(200, 200, 400, 100)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)  # 设置窗口为无边框


        main_layout = QVBoxLayout()

        top_buttons_layout = QHBoxLayout()
        
        # 全局循环次数输入框
        self.all_loop_count_input = QLineEdit('1')
        self.all_loop_count_label = QLabel('次')
        self.all_loop_count_input.setFixedWidth(50)  # 设置输入框宽度

        # 开始按钮
        self.start_button = QPushButton('开始（按F11停止）')
        self.start_button.setStyleSheet(
            "QPushButton {"
            "    background-color: black;"
            "    color: white;"
            "}"
        )
        self.start_button.clicked.connect(lambda: self.start_cycle(int(self.all_loop_count_input.text())))


        # 截图按钮
        self.screenshot_button = QPushButton('截图', self)
        self.screenshot_button.setStyleSheet(
            "QPushButton {"
            "    background-color: black;"
            "    color: white;"
            "}"
        )
        self.screenshot_button.clicked.connect(self.on_screenshot_button_clicked)

        # 添加导入按钮
        self.import_button = QPushButton('导入', self)
        self.import_button.clicked.connect(lambda: config_import_export_button_clicked(self, True))

        # 添加导出按钮
        self.export_button = QPushButton('导出', self)
        self.export_button.clicked.connect(lambda: config_import_export_button_clicked(self, False))

        # 隐藏窗口按钮
        self.minimize_button = QPushButton('最小化')
        self.minimize_button.clicked.connect(self.minimize_window)

        # 关闭窗口按钮
        self.close_button = QPushButton('关闭')
        self.close_button.clicked.connect(self.close_window)

        # UI加载控件
        top_buttons_layout.addWidget(self.screenshot_button)
        top_buttons_layout.addWidget(self.start_button)
        top_buttons_layout.addWidget(self.all_loop_count_input)
        top_buttons_layout.addWidget(self.all_loop_count_label)
        top_buttons_layout.addWidget(self.import_button)
        top_buttons_layout.addWidget(self.export_button)
        top_buttons_layout.addWidget(self.minimize_button)
        top_buttons_layout.addWidget(self.close_button)

        main_layout.addLayout(top_buttons_layout)

        # 创建一个带有透明背景的 QWidget 来包裹 controls_layout，放置控件行
        self.controls_container = QWidget()
        self.controls_container.setStyleSheet(
            "QWidget {"
            "    background-color: rgba(255, 255, 255, 128);"
            "}"
        )
        self.controls_layout = QVBoxLayout(self.controls_container)
        main_layout.addWidget(self.controls_container)

        # 添加初始的一行控件
        self.add_control_row(self.controls_layout)

        # 添加一个 "+" 号按钮
        self.add_button = QPushButton('+')
        self.add_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.add_button.clicked.connect(lambda: self.add_control_row(self.controls_layout))
        self.controls_layout.addWidget(self.add_button)

        # 创建中心widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # 设置键盘事件监听
        self.setMouseTracking(True)
        self.setAcceptDrops(True)
        self.setFocusPolicy(Qt.StrongFocus)

        # 重写鼠标事件
        self._drag_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos is not None:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def minimize_window(self):
        self.showMinimized()

    def close_window(self):
        self.close()

    def add_control_row(self, layout):
        logging.info("添加控件行")
        row_layout = QHBoxLayout()
        row_layout.setSpacing(5)  # 减小控件之间的间距
        row_layout.setContentsMargins(0, 0, 0, 0)  # 减小布局的边距

        # 上按钮
        up_button = QPushButton('↑')
        up_button.clicked.connect(lambda: self.move_control_row(row_layout, -1))
        up_button.setFixedWidth(25)  # 设置按钮宽度
        up_button.setFixedHeight(25)  # 设置按钮高度

        # 下按钮
        down_button = QPushButton('↓')
        down_button.clicked.connect(lambda: self.move_control_row(row_layout, 1))
        down_button.setFixedWidth(25)  # 设置按钮宽度
        down_button.setFixedHeight(25)  # 设置按钮高度

        # 循环次数输入框
        loop_label = QLabel('循环次数:')
        loop_input = QLineEdit('1')
        loop_input.setFixedWidth(50)  # 设置输入框宽度
        
        # 删除按钮
        delete_button = QPushButton('-')
        delete_button.clicked.connect(lambda: self.delete_control_row(row_layout))

        # 选项按钮
        option_label = QLabel('操作:')
        option_combo = QComboBox()
        option_combo.addItems(['单击', '双击', '等待', '输入'])
        option_combo.currentTextChanged.connect(lambda text, combo=option_combo: self.update_option_text(combo, text))

        # 等待时间输入框
        wait_label = QLabel('等待时间 (秒):')
        wait_input = QLineEdit('0')
        wait_input.setFixedWidth(150)  # 设置输入框宽度
        wait_label.hide()   # 初始化时隐藏
        wait_input.hide()   # 初始化时隐藏

        # 图片路径输入框
        image_label = QLabel('图片路径:')
        image_input = QLineEdit('')
        image_input.setFixedWidth(150)
        select_button = QPushButton('选择')
        select_button.clicked.connect(self.select_image)

        # 文本输入框
        text_label = QLabel('输入文本:')
        text_input = QLineEdit()
        text_input.setFixedWidth(150)
        text_label.hide()   # 初始化时隐藏
        text_input.hide()   # 初始化时隐藏

        # 界面初始化添加控件
        row_layout.addWidget(up_button)
        row_layout.addWidget(down_button)
        row_layout.addWidget(option_label)
        row_layout.addWidget(option_combo)
        row_layout.addWidget(image_label)
        row_layout.addWidget(image_input)
        row_layout.addWidget(select_button)
        row_layout.addWidget(wait_label)
        row_layout.addWidget(wait_input)
        row_layout.addWidget(text_label)
        row_layout.addWidget(text_input)
        row_layout.addWidget(loop_label)
        row_layout.addWidget(loop_input)
        row_layout.addWidget(delete_button)

        layout.insertLayout(layout.count() - 1, row_layout)  # 在“+”号按钮之前插入新行

        # 保存控件
        self.controls.append({
            'up_button': up_button,
            'down_button': down_button,
            'option_label': option_label,
            'option_combo': option_combo,
            'image_label': image_label,
            'image_input': image_input,
            'select_button': select_button,
            'wait_label': wait_label,
            'wait_input': wait_input,
            'text_label': text_label,
            'text_input': text_input,
            'loop_label': loop_label,
            'loop_input': loop_input,
            'delete_button': delete_button,
            'layout': row_layout
        })

    def move_control_row(self, row_layout, direction):
        logging.info(f"移动控件行 {direction}")
        # 找到当前行对应的控件信息
        control_info = next((control for control in self.controls if control['layout'] is row_layout), None)
        if control_info is None:
            logging.warning("未找到对应的控件信息")
            return

        index = self.controls.index(control_info)
        new_index = index + direction

        if 0 <= new_index < len(self.controls):
            # 移除当前控件行
            current_layout = self.controls_layout
            current_layout.removeItem(row_layout)

            # 移动控件
            self.controls[index], self.controls[new_index] = self.controls[new_index], self.controls[index]

            # 重新插入控件行
            current_layout.insertLayout(new_index, row_layout)

            # 移除并重新添加“+”号按钮
            current_layout.removeWidget(self.add_button)
            current_layout.addWidget(self.add_button)

    def delete_control_row(self, row_layout):
        logging.info("删除控件行")

        # 清除布局中的所有小部件
        while row_layout.count():
            item = row_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
            else:
                self.delete_control_row(item.layout())

        # 移除布局本身
        self.controls_layout.removeItem(row_layout)
        row_layout.setParent(None)

        # 更新控件列表
        self.controls = [control for control in self.controls if control['layout'] is not row_layout]

        # 重新调整窗口大小
        self.adjustSize()

    def select_image(self):
        logging.info("选择图片")
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "Images (*.png *.jpg *.jpeg)", options=options)
        if file_name:
            sender = self.sender()
            index = [control['select_button'] for control in self.controls].index(sender)
            self.controls[index]['image_input'].setText(file_name)

    def on_screenshot_button_clicked(self):
        logging.info("开始截图")
        self.hide()
        screenshot_widget = ScreenshotWidget()
        screenshot_widget.show()
        screenshot_widget.screenshot_complete = lambda: self.show_after_screenshot(screenshot_widget)

    def show_after_screenshot(self, screenshot_widget):
        logging.info("截图结束")
        screenshot_widget.close()
        self.show()

    def update_option_text(self, combo, text):
        logging.info(f"选项改变: {text}")
        index = [control['option_combo'] for control in self.controls].index(combo)

        # 动态更新控件
        control_info = self.controls[index]

        # 显示或隐藏图片相关控件
        if text == '单击' or text == '双击':
            control_info['image_label'].show()
            control_info['image_input'].show()
            control_info['select_button'].show()
        else:
            control_info['image_label'].hide()
            control_info['image_input'].hide()
            control_info['select_button'].hide()

        # 显示或隐藏文本输入框
        if text == '输入':
            control_info['text_label'].show()
            control_info['text_input'].show()
        else:
            control_info['text_label'].hide()
            control_info['text_input'].hide()

        # 显示或隐藏等待时间控件
        if text == '等待':
            control_info['wait_label'].show()
            control_info['wait_input'].show()
        else:
            control_info['wait_label'].hide()
            control_info['wait_input'].hide()
        # 重新调整窗口大小
        self.adjustSize()
    def start_cycle(self, all_loop_count=-1):
        logging.info("开始自动点击")

        # 初始化停止标志
        stop_flag = [False]
        # 开始监听键盘事件
        listener_main = keyboard.Listener(on_press=lambda key: on_press(key, stop_flag))
        listener_main.start()
        logging.info(f"all_loop_count: {all_loop_count}")

        if all_loop_count == -1:
            while not stop_flag[0]:
                self.cycle_body(stop_flag)
        else:
            for _ in range(all_loop_count):
                self.cycle_body(stop_flag)

        # 停止监听键盘事件
        listener_main.stop()

    def cycle_body(self, stop_flag):
        try:
            # 获取所有行的用户输入的值
            for index in range(self.controls_layout.count()):
                control_layout = self.controls_layout.itemAt(index).layout()
                control = next((item for item in self.controls if item['layout'] is control_layout), None)
                if control:

                    image_path = control['image_input'].text()
                    wait_time = control['wait_input'].text()
                    text_input = control['text_input'].text()
                    loop_count = int(control['loop_input'].text())
                    option = control['option_combo'].currentText()

                    # 调用功能函数
                    if option == '单击':
                        if not os.path.exists(image_path):
                            print("错误：图片路径不存在，请输入正确的图片路径。")
                            stop_flag[0] = True
                            return
                        autoCycle(stop_flag, loop_count=loop_count, action='click', other=image_path)
                    elif option == '双击':
                        if not os.path.exists(image_path):
                            print("错误：图片路径不存在，请输入正确的图片路径。")
                            stop_flag[0] = True
                            return
                        autoCycle(stop_flag, loop_count=loop_count, action='double_click', other=image_path)
                    elif option == '等待':
                        autoCycle(stop_flag, loop_count=loop_count, action='wait', other=wait_time)
                    elif option == '输入':
                        autoCycle(stop_flag, loop_count=loop_count, action='input', other=text_input)
                    else:
                        logging.warning("无效的操作选项")
        except ValueError as e:
            logging.error(f"输入错误: {e}")
        except Exception as e:
            logging.error(f"发生错误: {e}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()