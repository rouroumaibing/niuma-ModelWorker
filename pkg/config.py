# config.py

import logging
import yaml
from PyQt5.QtWidgets import QFileDialog, QMessageBox

def config_import_export_button_clicked(window, is_import=True):
    logging.info("处理配置导入/导出")
    options = QFileDialog.Options()

    if is_import:
        # 导入配置
        file_name, _ = QFileDialog.getOpenFileName(window, "打开配置文件", "", "YAML Files (*.yaml);;All Files (*)", options=options)
        if file_name:
            try:
                # 读取 YAML 文件
                with open(file_name, 'r', encoding='utf-8') as file:
                    data = yaml.safe_load(file)
                
                # 获取所有需要删除的控件行
                layouts_to_delete = [control['layout'] for control in window.controls]

                # 逆序删除控件行
                for row_layout in reversed(layouts_to_delete):
                    window.delete_control_row(row_layout)
                
                # 清空 controls 列表
                window.controls.clear()

                # 重新加载数据
                for control_data in data:
                    window.add_control_row(window.controls_layout)
                    control = window.controls[-1]
                    control['option_combo'].setCurrentText(control_data['option'])
                    control['image_input'].setText(control_data['image_path'])
                    control['wait_input'].setText(control_data['wait_time'])
                    control['text_input'].setText(control_data['input_text'])
                    control['loop_input'].setText(control_data['loop_count'])

                logging.info(f"配置已从 {file_name} 加载")
            except Exception as e:
                logging.error(f"导入配置失败: {e}")
                QMessageBox.critical(window, "错误", f"导入配置失败: {str(e)}")
    else:
        # 导出配置
        file_name, _ = QFileDialog.getSaveFileName(window, "保存配置文件", "config.yaml", "YAML Files (*.yaml);;All Files (*)", options=options)
        if file_name:
            # 如果用户选择了文件，则保存配置
            data = []
            for control in window.controls:
                control_data = {
                    'option': control['option_combo'].currentText(),
                    'image_path': control['image_input'].text(),
                    'wait_time': control['wait_input'].text(),
                    'input_text': control['text_input'].text(),
                    'loop_count': control['loop_input'].text()
                }
                data.append(control_data)

            # 写入 YAML 文件
            with open(file_name, 'w', encoding='utf-8') as file:
                yaml.dump(data, file, default_flow_style=False, allow_unicode=True)
            logging.info(f"配置已保存到 {file_name}")