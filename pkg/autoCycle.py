import os
import random
from pynput import keyboard
import pyautogui
from time import sleep
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def autoCycle(stop_flag, **kwargs):
    """
    根据action参数执行相应的操作。
    点击、双击、等待、输入文本
    
    :param stop_flag: 全局停止标志
    :param loop_count: 循环次数 (-1 表示无限循环)
    :param action: 操作类型 ('click', 'double_click', 'wait', 'input')
    :param other: 
        image_path: 图片路径
        wait_time: 等待时间 (单位：秒)
        input_text: 输入文本
    """
    action = kwargs.get('action')
    loop_count = kwargs.get('loop_count')
    other_params = kwargs.get('other')

    if action == 'click' or action == 'double_click':
        image_path = other_params
        cycle_click(stop_flag, action, loop_count, image_path)
    elif action == 'wait':
        wait_time = other_params
        cycle_wait(stop_flag, loop_count, wait_time)
    elif action == 'input':
        input_text = other_params
        cycle_input(stop_flag, loop_count, input_text)
    else:
        print("错误：未知的操作类型。")

def on_press(key, stop_flag):
    if key == keyboard.Key.f11:
        stop_flag[0] = True
        print("循环停止。")

def find_and_click(image_path, click_type):
    try:

        location = pyautogui.locateOnScreen(image_path, confidence=0.9)
        if location is not None:
            left, top, width, height = location
            x = random.randint(left, left + width)
            y = random.randint(top, top + height)

            # 打印找到的图片位置
            print(f"找到图片 {image_path} 位置: ({left}, {top}, {width}, {height})")
            print(f"随机点击位置: ({x}, {y})")

            # 移动鼠标到目标位置
            pyautogui.moveTo(x, y, duration=1.0, tween=pyautogui.easeInOutQuad)

            print(f"点击位置: ({x}, {y})")
            if click_type == 'double_click':
                pyautogui.doubleClick(x, y)
            elif click_type == 'click':
                pyautogui.click(x, y)
        else:
            print(f"未找到图片 {image_path}")
    except IOError as e:
        print(f"处理图片 {image_path} 时出错: {e}")

def cycle_click(stop_flag, action, loop_count, image_path):
    if not os.path.exists(image_path):
        print("错误：图片路径不存在，请输入正确的图片路径。")
        return

    click_type = action

    # 开始监听键盘事件
    cycle_click_listener = keyboard.Listener(on_press=lambda key: on_press(key, stop_flag))
    cycle_click_listener.start()

    if loop_count == -1:
        print("开始无限循环查找并点击图片...")
        while not stop_flag[0]:
            import pygetwindow as gw
            current_window = gw.getActiveWindow()
            if current_window:
                print(f"当前窗口标题: {current_window.title}")
            else:
                print("无法获取当前窗口标题")

            find_and_click(image_path, click_type)
    else:
        print(f"开始循环 {loop_count} 次查找并点击图片...")
        logging.info(f"loop_count: {loop_count}")
        for _ in range(loop_count):
            import pygetwindow as gw
            current_window = gw.getActiveWindow()
            if current_window:
                print(f"当前窗口标题: {current_window.title}")
            else:
                print("无法获取当前窗口标题")
                
            find_and_click(image_path, click_type)

    # 停止监听键盘事件
    cycle_click_listener.stop()

def cycle_wait(stop_flag, loop_count, wait_time):
    # 开始监听键盘事件
    cycle_wait_listener = keyboard.Listener(on_press=lambda key: on_press(key, stop_flag))
    cycle_wait_listener.start()

    if loop_count == -1:
        print("开始无限循环等待...")
        while not stop_flag[0]:
            sleep(int(wait_time))
    else:
        print(f"开始循环 {loop_count} 次等待 {wait_time} 秒...")
        for _ in range(loop_count):
            sleep(int(wait_time))

    # 停止监听键盘事件
    cycle_wait_listener.stop()

def cycle_input(stop_flag, loop_count, text_input):
    # 开始监听键盘事件
    cycle_input_listener = keyboard.Listener(on_press=lambda key: on_press(key, stop_flag))
    cycle_input_listener.start()

    if loop_count == -1:
        print("开始无限循环输入文本...")
        while not stop_flag[0]:
            # 获取当前鼠标位置
            current_position = pyautogui.position()
            # 在当前位置点击鼠标
            pyautogui.click(current_position)
            # 输入文本
            pyautogui.write(text_input)

            sleep(0.3)
            # 输入Enter
            pyautogui.press('enter')
    else:
        print(f"开始循环 {loop_count} 次输入文本...")
        for _ in range(loop_count):
            # 获取当前鼠标位置
            current_position = pyautogui.position()
            # 在当前位置点击鼠标
            pyautogui.click(current_position)
            # 输入文本
            pyautogui.write(text_input)

            sleep(0.3)
            # 输入Enter
            pyautogui.press('enter')

    # 停止监听键盘事件
    cycle_input_listener.stop()

def main():
    # 示例图片路径
    image_path = "images/TGX0NN1C.jpg"
    
    # 示例循环次数
    loop_count = 5
    
    # 调用 autoCycle 函数
    stop_flag = [False]
    autoCycle(stop_flag, loop_count=loop_count, action='click', other=image_path)

if __name__ == "__main__":
    main()