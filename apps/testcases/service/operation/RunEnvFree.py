# -*- coding: utf-8 -*-            
# @Author : libeijie
# @Time : 2023/10/26 17:02

import os
import shutil
from robot import run_cli
import chardet
import platform

def get_file_encoding(file_path):
    '''
    获取文件编码
    :param file_path:
    :return:
    '''
    with open(file_path, 'rb') as file:
        result = chardet.detect(file.read())
        encoding = result['encoding']
    return encoding

def remove_interaction_script(folder_root, execution_environment, browser):
    '''
    去掉脚本中和用户的交互部分（执行环境、浏览器）
    :param folder_root: 脚本根路径
    :param execution_environment:   交互部分的执行环境
    :param browser:     交互部分的浏览器
    :return:
    '''
    new_exe_bro = f"     @{{env}}        Create List        {execution_environment}       {browser}\n"
    # 有用户交互部分的文件，固定路径
    interaction_script_path = os.path.join(folder_root, 'Programs/自定义用户关键字/公用关键字.robot')
    # 获取文件编码
    encoding = get_file_encoding(interaction_script_path)

    with open(interaction_script_path, 'r', encoding=encoding) as file:
        lines = file.readlines()
    # 查找匹配的行并进行替换
    new_lines = []
    found_line = False
    for index, line in enumerate(lines):
        if 'Get Selections From User' in line:
            if lines[index + 1].strip().startswith('...'):
                found_line = True
            else:
                new_lines.append(new_exe_bro)
            continue

        if '@{env}CreateList' in line.replace(" ", ""):
            new_lines.append(new_exe_bro)
            continue

        if found_line and line.strip().startswith('...'):
            found_line = False
            new_lines.append(new_exe_bro)
        elif not found_line:
            new_lines.append(line)
    # 写入更新后的内容
    with open(interaction_script_path, 'w', encoding=encoding) as file:
        file.writelines(new_lines)

def modify_config_file(folder_root):
    '''
    修改config.txt文件
    :param folder_root:脚本项目根路径
    :return:
    '''
    #判断系统
    if "Windows" in platform.platform():
        separator = r'\\'
    else:
        separator = r'/'
    package_name = os.path.basename(folder_root)
    parent_directory = os.path.dirname(folder_root)
    config_file_path = os.path.join(folder_root,'Conf','config.txt')
    encoding = get_file_encoding(config_file_path)
    with open(config_file_path, 'r',encoding=encoding) as file:
        lines = file.readlines()
    with open(config_file_path, 'w',encoding=encoding) as file:
        for line in lines:
            if "${project_path} " in line:
                line = f'${{project_path}}     {parent_directory}\n'
            elif "${baseline_name} " in line:
                line = f'${{baseline_name}}     {package_name}\n'
            else:
                # 替换分隔符
                line.replace(r'\\',separator)
            file.write(line)

script_dir = os.path.dirname(os.path.realpath(__file__))
print(script_dir)
env_free_project_path = os.path.join(script_dir, 'AutoTest')

#读取self_config.txt文件
self_config = os.path.join(script_dir,'self_config.txt')
encoding = get_file_encoding(self_config)
with open(self_config, 'r',encoding=encoding) as file:
    lines = file.readlines()
    # 检查文件是否足够长以包含需要的行数
    if len(lines) >= 6:
        driver_paths = lines[1].strip()
        envs = lines[3].strip()
        browsers = lines[5].strip()
#将浏览器驱动复制到script_dir路径下
destination_path = ''
driver_path = driver_paths.split(';')[0]
if driver_path.endswith('chromedriver.exe'):  # 谷歌
    destination_path = os.path.join(script_dir, 'chromedriver.exe')
elif driver_path.endswith('geckodriver.exe'):  # 火狐
    destination_path = os.path.join(script_dir, 'geckodriver.exe')
shutil.copyfile(driver_path, destination_path)

#获取到env和browser，写入脚本公用关键字.robot
remove_interaction_script(env_free_project_path, envs.split(';')[0], browsers.split(';')[0])

#修改config.txt
modify_config_file(env_free_project_path)

#运行在windows虚拟机上，所以路径分隔符为\\
run_cli(['-r',env_free_project_path+'\\Logs\\report',
         '-l',env_free_project_path+'\\Logs\\log',
         '-o',env_free_project_path+'\\Logs\\ouput',
         '-T',
         '--extension','robot:txt',
         env_free_project_path+'\\Programs'],exit=False)

os.system("pause")

