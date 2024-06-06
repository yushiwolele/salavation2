# -*- coding: utf-8 -*-            
# @Author : libeijie
# @Time : 2023/9/7 15:02
from collections import Counter
from openpyxl import Workbook

class Folder:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.children = []

    @property
    def path(self):
        if self.parent is None:
            return self.name
        return f"{self.parent.path}/{self.name}"

def build_folder_tree(file_paths):
    folder_dict = {}  # 使用字典来映射文件夹名称到对应的Folder对象
    for file_path in file_paths:
        parts = file_path.split('/')
        current_folder = None

        for part in parts:
            # 检查当前部分是否已经存在于文件夹字典中
            child_folder = folder_dict.get(part)

            if not child_folder:
                child_folder = Folder(part, parent=current_folder)
                folder_dict[part] = child_folder

                # 如果有父文件夹，将子文件夹添加到父文件夹的children列表中
                if current_folder:
                    current_folder.children.append(child_folder)

            current_folder = child_folder

    # 找到根文件夹，即没有父文件夹的文件夹
    root_folders = [folder for folder in folder_dict.values() if folder.parent is None]

    return root_folders

file_paths = [
    'BSQ-CommonTestSuites/集成测试-静态类/静态类.robot',
    'BSQ-CommonTestSuites/集成测试-控件类/上传导入(一码通账户号码).robot',
    'BSQ-CommonTestSuites/集成测试-控件类/单项输入框.robot',
    'BSQ-CommonTestSuites/回归测试-流程类/流程类.robot',
    'BSQ-CommonTestSuites/回归测试-流程类/流程类4.robot',
    'BSQ-ProjectTreeConfig/00dir_project.txt',
    'BSQ-ProjectTreeConfig/01dir_first.txt',
]

folder_tree = build_folder_tree(file_paths)

# 递归打印文件夹树
def print_folder_tree(folder, indent=""):
    print(indent + folder.name)
    for child in folder.children:
        print_folder_tree(child, indent + "  ")

for root_folder in folder_tree:
    print_folder_tree(root_folder)

import re
a = 'BSQ-CommonTestSuites/eer/ds/4r.tt'
match = re.match(r'(.+?)/([^/]+)$',a)
if match:
    matched_text = match.group(0)
    matched_text2 = match.group(1)

else:
    print("未找到匹配")

import os
path='F:\Salvation学习\脚本功能用到\配置_基线包\IUMP-BSQ-AutoTest-F'
a = os.listdir(path)





import xlrd

# 打开Excel文件
workbook = xlrd.open_workbook('F:\\Salvation\\excbak\\写好的用例fortest.xlsm')
sheet = workbook.sheet_by_name('结算信息汇总查询-沪（Ⅰ级）')

#import shutil
# 使用shutil.make_archive创建ZIP文件
#shutil.make_archive('F:\\Salvation\\excbak\\baseline\\aaa\\IUMP-BSQ-AutoTest-F', 'zip', 'F:\\Salvation\\excbak\\baseline\\IUMP-BSQ-AutoTest-F')

file = 'conf'
tmp_rel_dir = 'Conf/env.py'.lower()
print(tmp_rel_dir[:4])
if file == tmp_rel_dir[:len(file)]:
    print(len(file))
    print('dddddddd')
    pass
try:
    try:
        print('11111111111')
        raise Exception
    except:
        print('222222222')
except:
    print('333333333')


if __name__ == '__main__':
    import time
