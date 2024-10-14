import os
import random
from pynput import keyboard
import pyautogui

def autoClick(image_path, loop_count=-1):
    """
    自动查找并点击图片，并通过鼠标轨迹移动到新坐标。
    
    :param image_path: 图片路径
    :param loop_count: 循环次数 (-1 表示无限循环)
    """
    if not os.path.exists(image_path):
        print("错误：图片路径不存在，请输入正确的图片路径。")
        return

    stop_flag = False

    def on_press(key):
        nonlocal stop_flag
        if key == keyboard.Key.f11:
            stop_flag = True
            print("循环停止。")

    # 开始监听键盘事件
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    if loop_count == -1:
        print("开始无限循环查找并点击图片...")
        while not stop_flag:
            try:
                location = pyautogui.locateOnScreen(image_path, confidence=0.7)
                if location is not None:
                    left, top, width, height = location
                    x = random.randint(left, left + width)
                    y = random.randint(top, top + height)
                    
                    # 获取当前鼠标位置
                    current_x, current_y = pyautogui.position()
                    
                    # 移动鼠标到目标位置
                    pyautogui.moveTo(x, y, duration=1.0, tween=pyautogui.easeInOutQuad)
                    
                    print(f"找到图片 {image_path} 并点击位置: ({x}, {y})")
                    pyautogui.click(x, y)
                else:
                    print(f"未找到图片 {image_path}")
            except IOError as e:
                print(f"处理图片 {image_path} 时出错: {e}")
                continue  # 跳过当前图片，继续处理下一个图片
    else:
        print(f"开始循环 {loop_count} 次查找并点击图片...")
        for _ in range(loop_count):
            try:
                location = pyautogui.locateOnScreen(image_path, confidence=0.7)
                if location is not None:
                    left, top, width, height = location
                    x = random.randint(left, left + width)
                    y = random.randint(top, top + height)
                    
                    # 获取当前鼠标位置
                    current_x, current_y = pyautogui.position()
                    
                    # 移动鼠标到目标位置
                    pyautogui.moveTo(x, y, duration=1.0, tween=pyautogui.easeInOutQuad)
                    
                    print(f"找到图片 {image_path} 并点击位置: ({x}, {y})")
                    pyautogui.click(x, y)
                else:
                    print(f"未找到图片 {image_path}")
            except IOError as e:
                print(f"处理图片 {image_path} 时出错: {e}")
                continue  # 跳过当前图片，继续处理下一个图片

    # 停止监听键盘事件
    listener.stop()
def main():
    # 示例图片路径
    image_path = "images/TGX0NN1C.jpg"
    
    # 示例循环次数
    loop_count = 5
    
    # 调用 autoClick 函数
    autoClick(image_path, loop_count)

if __name__ == "__main__":
    main()