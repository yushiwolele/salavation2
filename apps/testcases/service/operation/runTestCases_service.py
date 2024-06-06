# -*- coding: utf-8 -*-            
# @Author : libeijie
# @Time : 2023/12/8 14:45

import os
import uuid
import logging
import codecs
import subprocess
import platform
import time
from robot.api import TestSuiteBuilder
from robot.errors import DataError


from Salvation.settings import BASE_DIR
from common.file_helper import rmtreedir,get_file_encoding,convert_file_encoding,detect_encoding,clear_directory
from common.cfg_helper import *
from testcases.models import RanScriptResultModel

logger = logging.getLogger('salvation')
class Folder:
    def __init__(self, folder_id, name, folder_type, parent_id=None, children=None, path=None):
        self.folder_id = folder_id
        self.name = name
        self.folder_type = folder_type  # 0 for folder, 1 for file ,2 for robot
        self.parent_id = parent_id
        self.children = children or []
        self.path = path

def folder_to_dict(folder):
    '''
    Folder对象转dict
    :param folder: Folder对象
    :return:
    '''

    if folder.folder_type == '2': #如果是robot文件，单独处理
        children = folder.children
    else:
        children = [folder_to_dict(child) for child in folder.children]
        children.sort(key=lambda k: k['type'], reverse=False)
    folder_dict = {
        "id": folder.folder_id,
        "name": folder.name,
        "path": folder.path,
        "type": folder.folder_type,
        "parent_id":folder.parent_id,
        "children": children
    }
    return folder_dict

class RunTestCasesService:
    def __init__(self):
        cfg_file = ''.join([str(BASE_DIR), '/apps/data/config.cfg'])
        self.cfg_read = CfgHelper(cfg_file)
        # 上传的脚本保存的临时路径
        self.autoScript_root_path = self.cfg_read.read_cfg_get_value_by_key('config_file','auto_script')
        self.argfile = 'argfile.txt'
        self.custom_keywords_file = 'Programs/自定义用户关键字'
        self.tmp_testcases = '*** Test Cases ***\nEmpty Test Case For Catch Error\n'
        self.env_file = 'Conf/env.py' #网址配置文件

    def handle_auto_script(self,auto_script_files,auto_script_file_paths,folder_name,user_id):
        '''
        处理上传的自动化脚本文件
        :param auto_script_files:
        :param auto_script_file_paths:
        :param folder_name:
        :return:
        '''
        folder_use_id = 'uid_'+str(user_id)
        script_folder_root_tmp = os.path.join(self.autoScript_root_path, folder_use_id)

        #删除此用户之前的脚本，目的是只保留一个最新的
        clear_directory(script_folder_root_tmp)
        #删除数据库此用户的所有执行信息
        try:
            objects_to_delete = RanScriptResultModel.objects.filter(user_id=user_id)
            objects_to_delete.delete()
        except Exception as e:
            logger.error('报错信息：' + repr(e) + ',报错的行号:' + str(e.__traceback__.tb_lineno))

        script_file_uuid = uuid.uuid4()
        script_folder_tmp = os.path.join(script_folder_root_tmp, str(script_file_uuid))
        script_folder_tmp = os.path.normpath(script_folder_tmp)

        # 先存为临时文件
        for index, script_component_file_path in enumerate(auto_script_file_paths):
            script_path_tmp = os.path.join(script_folder_tmp, script_component_file_path)
            folder_path = os.path.dirname(script_path_tmp)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            # 写入文件内容
            new_file = auto_script_files[index]
            try:
                # 保存新文件
                with open(script_path_tmp, 'wb') as destination:
                    for chunk in new_file.chunks():
                        destination.write(chunk)
            except Exception as e:
                logger.error('报错信息：' + repr(e) + ',报错的行号:' + str(e.__traceback__.tb_lineno))
                rmtreedir(script_folder_tmp)
                msg = f"发生错误：{str(e)}"
                return {'code':1,'data':msg}

        #处理文件夹结构，如果是robot文件，则读取，是Keywords，则添加为一条子项；如果是Variable则添加为一条子项，如果是test cases则添加为一条子项且前端可选
        folder_path = os.path.join(script_folder_tmp,folder_name)
        root_folder = self.process_folder(folder_path)

        return {'code':0,'data':root_folder}

    def get_latest_ran_script(self,user_id):
        '''
        获取此用户最新一次的用例脚本
        :param user_id: 用户id
        :return:
        '''
        folder_use_id = 'uid_' + str(user_id)
        script_folder_root_tmp = os.path.join(self.autoScript_root_path, folder_use_id)
        script_folder_root_tmp = os.path.normpath(script_folder_root_tmp)
        if os.path.exists(script_folder_root_tmp):
            content_list = os.listdir(script_folder_root_tmp)  # token目录下子文件（夹）
            if len(content_list) > 0:  # 有子文件（夹）
                # 获取最新的那一个，（其他的可以删除）
                # 获取每个子文件夹的最近修改时间
                subdirectories_with_time = [(subdir, int(os.path.getmtime(os.path.join(script_folder_root_tmp, subdir)))) for
                                            subdir in content_list]

                subdirectories_with_time_sorted = sorted(subdirectories_with_time, key=lambda x: x[1], reverse=True)
                # 找到最近修改时间的子文件夹
                latest_subdirectory = subdirectories_with_time_sorted[0][0] #时间最近一次的脚本，文件夹（uuid）名字
                script_folder_tmp = os.path.join(script_folder_root_tmp, latest_subdirectory)
                folder_name = (os.listdir(script_folder_tmp))[0]
                #其他非最新时间的文件夹可以删除
                # others_subdirectory = subdirectories_with_time_sorted[1:]
                # if len(others_subdirectory) > 0:
                #     for others_subdirectory_item in others_subdirectory:
                #         rmtreedir(os.path.join(script_folder_root_tmp, others_subdirectory_item[0]))
            else:  # 没有子文件夹
                msg = '此用户未执行过用例，无法获取执行过的用例。请选择本地脚本进行执行操作。'
                return {'code': 1, 'data': msg}
        else:
            msg = '此用户未执行过用例，无法获取执行过的用例。请选择本地脚本进行执行操作。'
            return {'code':1,'data':msg}

        # 处理文件夹结构，如果是robot文件，则读取，是Keywords，则添加为一条子项；如果是Variable则添加为一条子项，如果是test cases则添加为一条子项且前端可选
        folder_path = os.path.join(script_folder_tmp, folder_name)
        root_folder = self.process_folder(folder_path)

        return {'code': 0, 'data': root_folder}

    def process_folder(self,path, parent_id=None):
        folder_id = hash(path)
        folder_name = os.path.basename(path)
        children = []
        if os.path.isdir(path):
            folder_type = '0'  # 文件夹类型
            # Process each item in the folder
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                children.append(self.process_folder(item_path, parent_id=folder_id))
        else:
            folder_type = '1'  # 文件类型
            if path.lower().endswith('.robot'):
                folder_type = '2'  #robot
                robot_data = self.parse_robot_file(path)
                children = robot_data

        return Folder(folder_id, folder_name, folder_type, parent_id=parent_id,
                      children=children, path=path)

    def parse_robot_file(self,file_path):
        robot_data = {'testcases': [], 'keywords': [],'variables':[]}
        #获取文件编码
        encoding = get_file_encoding(file_path)
        if encoding.lower() == 'gbk' or encoding.lower() == 'gb2312':
            #更改文件编码
            convert_file_encoding(file_path,'utf-8')
        try:
            suite = TestSuiteBuilder().build(file_path)
        except DataError:#没有testcases报错
            # 如果出现 DataError，说明没有测试用例，添加一个空的测试用例
            with open(file_path, 'a') as file:
                file.write(self.tmp_testcases)
            # 重新尝试构建测试套件
            suite = TestSuiteBuilder().build(file_path)
        for suite_or_test in suite.tests:
            robot_data['testcases'].append(suite_or_test.name)
        for suite_or_test in suite.resource.keywords:
            robot_data['keywords'].append(suite_or_test.name)
        for suite_or_test in suite.resource.variables:
            robot_data['variables'].append(suite_or_test.name)
        return robot_data

    def change_name_service(self,item_path,initial_name,edited_text,robot_case_flag,content_flag):
        '''
        更改robot及testcases名字
        :param item_path: robot文件绝对路径
        :param initial_name: 修改前的名字
        :param edited_text: 修改后的名字
        :param robot_case_flag: 0-robot文件名；1-testcases名字
        :param robot_case_flag: 0-testcase;1-keywords;2-variables
        :return:
        '''
        if robot_case_flag  == '0':
            # 修改 robot 文件名字
            directory, filename = os.path.split(item_path)
            new_path = os.path.join(directory, edited_text)
            os.rename(item_path, new_path)
        else:
            if content_flag == '0':
                content_identify = '*** Test Cases ***'
            elif content_flag == '1':
                content_identify = '*** Keywords ***'
            else:
                content_identify = '*** Variables ***'
            self.rename_testcase_in_robot_file(item_path,initial_name,edited_text,content_identify)

    def rename_testcase_in_robot_file(self,file_path, initial_name, edited_text,content_identify):
        '''
        修改robot文件中
        :param file_path: robot文件绝对路径
        :param initial_name: 修改前名字
        :param edited_text: 修改后名字
        :param content_identify: 内容标识；*** Test Cases ***	/*** Keywords ***/*** Variables ***
        :return:
        '''
        encoding = get_file_encoding(file_path)
        with open(file_path, 'r', encoding=encoding) as file:
            content = file.read()
            # 查找测试用例段
            test_cases_start = content.find(content_identify)
            if test_cases_start != -1:
                # 查找测试用例名称
                test_case_start = content.find(initial_name, test_cases_start)
                if test_case_start != -1:
                    # 找到结束位置
                    test_case_end = content.find('\n', test_case_start)
                    if test_case_end != -1:
                        # 提取测试用例行
                        test_case_line = content[test_case_start:test_case_end].strip()
                        # 替换测试用例行
                        new_content = content.replace(test_case_line, edited_text, 1)

                        with open(file_path, 'w', encoding=encoding) as file:
                            file.write(new_content)
                    else:
                        logger.info('未发现'+content_identify+'结尾')
                else:
                    logger.info('未匹配上：' + initial_name)
            else:
                logger.info('此文件无' + content_identify)

    def delete_folder_file_service(self,item_path,folder_root):
        '''
        删除文件或者文件夹
        :param item_path: 要删除的文件或文件夹绝对位置
        :param folder_root: 前端页面展示的最高级路径，for 重新组织文件结构
        :return:
        '''
        try:
            if os.path.isfile(item_path):  # 如果是文件
                os.remove(item_path)
            elif os.path.isdir(item_path):  # 如果是文件夹
                rmtreedir(item_path)
            else:
                msg = f'无此文件或文件夹：{item_path}'
                logger.info(msg)
                return {'code':1,'data':msg}
        except Exception as e:
            logger.error('报错信息：' + repr(e) + ',报错的行号:' + str(e.__traceback__.tb_lineno))
            return {'code':1,'data':str(e)}
        #重新组织文件结构
        root_folder = self.process_folder(folder_root)
        return {'code':0,'data':root_folder}

    def update_script_file_content_physically(self,file_path,file_content):
        '''
        更改服务器上文件内容
        :param file_path: 服务器上文件位置
        :param file_content: 要更新的内容
        :return:
        '''
        code = 0
        #获取文件编码
        encoding = get_file_encoding(file_path)
        try:
            with open(file_path, "r+",encoding=encoding) as file:
                # 将文件指针移到文件开头
                file.seek(0)
                # 写入新内容
                file.write(file_content)
                # 截断文件以匹配新内容的长度
                file.truncate()
            #获取文件内容的格式
            data = self.parse_robot_file(file_path)
        except Exception as e:
            code = 1
            data = f"发生错误：{str(e)}"
        return {'code':code,'data':data}

    def handles_testcases_service(self,checked_testcases):
        '''
        处理前端传入的选中的testcases
        :param checked_testcases: 被选中的cases
        :return:
        '''
        test_suites_level = {} #【套件级别执行】集合，格式[功能绝对路径：robot绝对路径]
        functions = set() #涉及到的【功能】集合
        functions_level = [] #【功能级别执行】集合
        #获取robot文件
        for robot_file_item in list(checked_testcases.keys()):
            parent_directory_path = os.path.abspath(os.path.dirname(robot_file_item))
            functions.add(parent_directory_path)
            #选中的testcases个数
            robot_file_item_checked_testcases = len(checked_testcases[robot_file_item])
            #实际testcases个数
            encoding = get_file_encoding(robot_file_item)
            if encoding.lower() == 'gbk' or encoding.lower() == 'gb2312':
                # 更改文件编码
                convert_file_encoding(robot_file_item, 'utf-8')
            suite = TestSuiteBuilder().build(robot_file_item)
            testcases_num = len(suite.tests)
            if robot_file_item_checked_testcases == testcases_num: #robot文件全选，由【用例级别执行】升级为【套件级别执行】
                #获取对应的【功能】
                if parent_directory_path in test_suites_level.keys():
                    pass
                else:
                    test_suites_level[parent_directory_path] = list()
                test_suites_level[parent_directory_path].append(robot_file_item)
                #如果升级为【套件级别执行】，则不用【用例级别执行】，即删除checked_testcases对应的key
                checked_testcases.pop(robot_file_item)

        for functions_item in functions:
            # 获取目录下的所有文件和子目录
            all_files = os.listdir(functions_item)
            robot_files = [file for file in all_files if file.endswith(".robot")]
            robot_files_count = len(robot_files)
            #如果是robot文件本身里面没有testcases，则不统计此robot
            absolute_paths = [os.path.join(functions_item, file) for file in robot_files] #robot绝对路径
            for absolute_path in absolute_paths:
                suite = TestSuiteBuilder().build(absolute_path)
                if len(suite.tests) == 1 and suite.tests[0].name == 'Empty Test Case For Catch Error':
                    robot_files_count -= 1
            if functions_item in test_suites_level.keys(): #此【功能】下有robot是【套件级别执行】
                if robot_files_count == len(test_suites_level[functions_item]): #此功能下所有robot的所有testcases均被选中，由【套件级别执行】升级为【功能级别执行】
                    functions_level.append(functions_item)
                    #如果确认为【功能级别执行】，则不用【套件级别执行】，即删除test_suites_level中对应的key
                    test_suites_level.pop(functions_item)

        return checked_testcases,test_suites_level,functions_level

    def run_testcases_service(self,checked_testcases,folder_root,execution_environment,browser,user_id):
        '''
        运行脚本
        :param checked_testcases: 前端勾选的用例
        :param folder_root: 脚本根路径
        :param execution_environment: 执行环境
        :param browser: 浏览器
        :param user_id: 用户id
        :return:
        '''
        try:
            #去掉脚本中和用户交互的内容
            self.remove_interaction_script(folder_root,execution_environment,browser)
            #去掉参数robot中的testcases
            self.process_folders(folder_root)
            #生成参数文件argfile.txt
            self.generate_testcase_files(folder_root, checked_testcases)
            #修改config.txt
            self.modify_config_file(folder_root)
            # 判断是否可以连接脚本中的网址，如果连接不通，会导致无法关闭浏览器，则执行脚本会导致子线程挂起无法关闭；方法一：按此修改；方法二：脚本中teardown关闭浏览器
            # env_path = os.path.join(folder_root,self.env_file)
            # url = self.get_script_url(env_path,execution_environment)
            # socket.create_connection((url, 80))
        except Exception as e:
            logger.error('报错信息：' + repr(e) + ',报错的行号:' + str(e.__traceback__.tb_lineno))
            msg = f"run_script_error：{str(e)}"
            yield msg
            return

        command = [
                'robot',
                '--argumentfile', os.path.join(folder_root, self.argfile),
                folder_root
            ]
        shell = False
        if "Windows" in platform.platform():
            shell = True
        try:
            process = subprocess.Popen(command, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            # process = subprocess.Popen([executable_path] + args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)
            # 通过生成器把结果实时返回
            for line in iter(process.stdout.readline, ''):
                print(line)
                encoding = detect_encoding(line)
                if encoding == None: #认为是最后一行
                    break
                # 将后端的空格替换为前端的空格符
                yield line.decode(encoding)
            # 关闭与子进程的标准输出流的连接
            process.stdout.close()
            # 等待线程结束
            process.wait()
            # 等待1秒后返回结束
            time.sleep(1)
        except Exception as e:
            process.stdout.close()
            process.wait()
            logger.error('报错信息：' + repr(e) + ',报错的行号:' + str(e.__traceback__.tb_lineno))
            yield 'run_script_process_error'
            return
        # 获取output.xml数据，存入mysql
        self.handle_script_result(folder_root)
        yield 'run_script_completed'
        return

    def handle_script_result(self,folder_root):
        '''
        处理ouput.xml文件，存储脚本运行结果
        :param folder_root: 脚本根路径
        :return:
        '''
        import glob
        import xml.etree.ElementTree as ET
        data_list = list()
        batch_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        #通过脚本根路径，获取data_uuid和user_id
        # 获取相对路径
        relative_path = os.path.relpath(folder_root, self.autoScript_root_path)
        # 将相对路径拆分为各个部分
        parts = os.path.normpath(relative_path).split(os.path.sep)
        try:
            # 提取uid_1和uuid
            if len(parts) >= 3:
                uid = str(parts[0]).split('_')[1]
                uuid_part = parts[1]
                #获取output.xml
                # 指定路径
                xml_folder_path = os.path.join(folder_root,'Logs')
                # 获取路径下所有的 XML 文件列表
                xml_files = glob.glob(os.path.join(xml_folder_path, '*.xml'))
                # 如果存在 XML 文件
                if xml_files:
                    #删除数据库老数据（如果有）
                    try:
                        objects_to_delete = RanScriptResultModel.objects.filter(user_id=uid)
                        objects_to_delete.delete()
                    except Exception as e: #如果删除失败，只记录报错，不中断程序
                        logger.error('报错信息：' + repr(e) + ',报错的行号:' + str(e.__traceback__.tb_lineno))

                    # 根据文件的修改时间排序
                    xml_files.sort(key=os.path.getmtime, reverse=True)
                    # 获取最近的 XML 文件路径
                    latest_xml_file = xml_files[0]
                    tree = ET.parse(latest_xml_file)
                    root = tree.getroot()
                    filtered_suites = filter(lambda suite: suite.get('source', '').endswith('.robot'),root.findall('.//suite'))
                    for suite_elem in filtered_suites:
                        suite_source = suite_elem.get('source')
                        # 获取<suite>元素下的所有<test>元素
                        test_elements = suite_elem.findall('.//test')
                        for test_elem in test_elements:
                            test_name = test_elem.get('name')
                            status_elem = test_elem.find('./status')
                            status = status_elem.get('status')
                            data_list.append(RanScriptResultModel(robot_path=suite_source,
                                                                  test_name=test_name,status=status,data_uuid=uuid_part,user_id=uid,batch_time=batch_time))
                    RanScriptResultModel.objects.bulk_create(data_list)
                    return True
                else:
                    logger.error(f'{folder_root}：日志无xml文件')
            else:
                logger.error(f'{folder_root}：路径有误')
        except Exception as e:
            logger.error('报错信息：' + repr(e) + ',报错的行号:' + str(e.__traceback__.tb_lineno))
        return False

    def get_script_url(self,folder_root,execution_environment):
        '''
        获取网址
        :param folder_root: 脚本根路径
        :param execution_environment: 执行环境
        :return:
        '''
        #获取env.py文件
        env_list = []
        # 初始化键
        current_flag = False
        with open(folder_root, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            # 遍历集合
            for line in lines:
                # 如果以 "DICT__" 开头，表示一个新的字典定义开始
                if line.startswith("DICT__" + execution_environment):
                    current_flag = True
                elif "}" in line:
                    break
                elif current_flag:
                    env_list.append(line.strip())
        url = env_list[0].replace(" ", "").split(":")[2].replace("//", "").replace("',", "")
        return url

    def run_testcases_service_logfiles(self,checked_testcases,folder_root,execution_environment,browser):
        try:
            #去掉脚本中和用户交互的内容
            self.remove_interaction_script(folder_root,execution_environment,browser)
            #去掉参数robot中的testcases
            self.process_folders(folder_root)
            #生成参数文件argfile.txt
            self.generate_testcase_files(folder_root, checked_testcases)
        except Exception as e:
            logger.error('报错信息：' + repr(e) + ',报错的行号:' + str(e.__traceback__.tb_lineno))
            msg = f"发生错误：{str(e)}"
            return {'code': 1, 'msg': msg}

        #log.log记录
        log_path = codecs.open(os.path.join(folder_root,'Logs','logs.log'), "a+", "utf-8")
        command = [
                'robot',
                '--argumentfile', os.path.join(folder_root, self.argfile),
                folder_root
            ]
        shell = False
        if "Windows" in platform.platform():
            shell = True
        process = subprocess.Popen(command, shell=shell, stdout=log_path, stderr=subprocess.STDOUT)
        #process = subprocess.Popen([executable_path] + args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)

        initial_position = log_path.tell()
        while process.poll() is None:
            # 移动文件指针到当前位置
            log_path.seek(initial_position)
            # 读取文件
            log_content = log_path.read()
            if log_content:
                print(log_content)
                yield {'code': 0, 'msg': log_content}
                # 更新文件指针位置
            initial_position = log_path.tell()
            time.sleep(3)
        # 执行完成后，你也可以读取一次最终的日志内容
        log_path.seek(initial_position)
        final_log_content = log_path.read()
        yield final_log_content

        # 关闭与子进程的标准输出流的连接
        process.stdout.close()
        # 等待子进程结束，并返回进程的退出状态码
        process.wait()
        # 等待1秒后返回结束
        time.sleep(1)
        yield {'code': 0, 'msg': 'run_script_completed'}

    def remove_interaction_script(self,folder_root,execution_environment,browser):
        '''
        去掉脚本中和用户的交互部分（执行环境、浏览器）
        :param folder_root: 脚本根路径
        :param execution_environment:   交互部分的执行环境
        :param browser:     交互部分的浏览器
        :return:
        '''
        new_exe_bro = f"     @{{env}}        Create List        {execution_environment}       {browser}\n"
        #有用户交互部分的文件，固定路径
        interaction_script_path = os.path.join(folder_root,self.custom_keywords_file,'公用关键字.robot')
        #获取文件编码
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
    def modify_config_file(self,folder_root):
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

    def write_testcase_to_file(self,file, package_name,suite_path, testcase,folder_root):
        '''
        组织正确数据格式，写入argfile.txt文件
        :param file: argfile.txt文件
        :param package_name: 脚本项目名称
        :param suite_path: 套件路径
        :param testcase: 套件下选中的testcase
        :param folder_root: 脚本项目根路径
        :return:
        '''
        relative_path = os.path.relpath(suite_path, folder_root)  # 'Programs\\业务统计查询系统\\fortest.robot'
        package_path = os.path.dirname(relative_path)  # 'Programs\\业务统计查询系统'
        package_path = package_path.replace(os.path.sep, ".")
        suite_name = os.path.splitext(os.path.basename(suite_path))[0]
        testcase_path = f'{package_name}.{package_path}.{suite_name}.{testcase}'
        file.write(f'--test\n{testcase_path}\n')

    def generate_testcase_files(self,folder_root, checked_testcases):
        '''
        生成argfile.txt文件并写入数据
        :param folder_root: 脚本根路径
        :param checked_testcases: 前端勾选的testcases
        :return:
        '''
        #日志路径
        report_path = os.path.join(folder_root, 'Logs', 'report')
        log_path = os.path.join(folder_root, 'Logs', 'log')
        output_path = os.path.join(folder_root, 'Logs', 'output')
        #argfile.txt路径
        testcase_file_path = os.path.join(folder_root, self.argfile)

        #如果存在则删除
        if os.path.exists(testcase_file_path):
            os.remove(testcase_file_path)

        #脚本项目名
        package_name = os.path.basename(folder_root)
        with open(testcase_file_path, 'a', encoding='utf-8') as file:
            #写入日志路径
            file.write(f'--report\n{report_path}\n')
            file.write(f'--log\n{log_path}\n')
            file.write(f'--output\n{output_path}\n')
            # file.write(f'-r\n{report_path}\n')
            # file.write(f'-l\n{log_path}\n')
            # file.write(f'-o\n{output_path}\n')
            #写入用例
            for suite_path, testcases in checked_testcases.items():
                for testcase in testcases:
                    self.write_testcase_to_file(file, package_name,suite_path, testcase,folder_root)

    def process_robot_file(self,robot_file_path):
        '''
        处理文件
        :param robot_file_path: robot路径
        :return:
        '''
        #获取编码
        encoding = get_file_encoding(robot_file_path)
        # 读取文件内容
        with open(robot_file_path, 'r', encoding=encoding) as file:
            content = file.read()

        # 移除指定内容
        content = content.replace(self.tmp_testcases, '')

        # 写回文件
        with open(robot_file_path, 'w', encoding=encoding) as file:
            file.write(content)

    def process_folders(self, folder_root):
        '''
        去掉自定义用户关键字下的robot文件中的testcases
        :param folder_root: 脚本项目根路径
        :return:
        '''
        folder_path = os.path.join(folder_root, self.custom_keywords_file)
        self.process_files_in_folder(folder_path)

    def process_files_in_folder(self, folder_path):
        '''
        获取robot文件并处理文件
        :param folder_path: 指定处理此目录下的robot文件
        :return:
        '''
        for root, dirs, files in os.walk(folder_path):
            for file_name in files:
                if file_name.endswith('.robot'):
                    self.process_robot_file(os.path.join(root, file_name))

    def rewirte_execu_browser(self,folder_path):
        '''
        处理文件内容，将@{env}CreateList转成可选择
        :param folder_path:
        :return:
        '''
        #获取文件位置
        interaction_script_path = os.path.join(folder_path,self.custom_keywords_file,'公用关键字.robot')
        new_exe_bro = r'      ${env}         Get Selections From User        请选择执行环境：\nTEST-测试 DEV-开发 BETA-仿真           TEST        DEV     BETA        请选择浏览器:  IE     FireFox     Chrome'
        new_second_line_exe_bro = '\n'
        try:
            # 获取文件编码
            encoding = get_file_encoding(interaction_script_path)
            with open(interaction_script_path, 'r', encoding=encoding) as file:
                lines = file.readlines()
                # 查找匹配的行并进行替换
                new_lines = []
                for index, line in enumerate(lines):
                    if '@{env}CreateList' in line.replace(" ", ""):
                        new_lines.append(new_exe_bro)
                        new_lines.append(new_second_line_exe_bro)
                        continue
                    new_lines.append(line)
                # 写入更新后的内容
                with open(interaction_script_path, 'w', encoding=encoding) as file:
                    file.writelines(new_lines)
        except Exception as e:
            logger.error('报错信息：' + repr(e) + ',报错的行号:' + str(e.__traceback__.tb_lineno))
            msg = f"发生错误：{str(e)}"
            return {'code': 1, 'msg': msg}
        return {'code': 0, 'msg': ''}

    def get_classification_result(self,folder_path,user_id):
        '''
        获取成功/失败的case
        :param folder_path: 脚本根目录
        :param user_id: 用户id
        :return:
        '''
        from django.db.models import Max
        #获取uuid
        # 获取相对路径
        relative_path = os.path.relpath(folder_path, self.autoScript_root_path)
        # 将相对路径拆分为各个部分
        parts = os.path.normpath(relative_path).split(os.path.sep)
        # 提取uid_1和uuid
        if len(parts) >= 3:
            uuid_part = parts[1]
            latest_batch_data = RanScriptResultModel.objects.filter(data_uuid=uuid_part, user_id=user_id).values('data_uuid', 'user_id').annotate(latest_batch_time=Max('batch_time')).order_by('-latest_batch_time').first()
            if latest_batch_data:
                fail_data = {}
                pass_data = {}
                test_list = []
                latest_data = RanScriptResultModel.objects.filter(data_uuid=latest_batch_data['data_uuid'], user_id=latest_batch_data['user_id'], batch_time=latest_batch_data['latest_batch_time'])

                #组织这批数据的结构
                for latest_data_item in latest_data:
                    status_value = latest_data_item.status
                    test_name = latest_data_item.test_name
                    suite_source = latest_data_item.robot_path
                    # 将测试信息添加到测试列表
                    test_info = {'test_name': test_name, 'status_value': status_value}
                    test_list.append(test_info)
                    if status_value == 'FAIL':
                        fail_data.setdefault(suite_source, []).append(test_info)
                    elif status_value == 'PASS':
                        pass_data.setdefault(suite_source, []).append(test_info)
                data_json = {'fail_data':fail_data,'pass_data':pass_data}
                return {'code':0,'data':data_json}
            else:
                return {'code': 1, 'data': f'未找到此批数据（{uuid_part}）的执行信息'}
        return {'code':1,'data':f'路径有误：{folder_path}'}


if __name__ == "__main__":
    folder_root = r'F:\Salvation\tmp\autoScript\uid_1\016c16eb-ee00-40a4-ba17-340502634b2b\BSQ2023001-P8-URM-AutoTest-I-20231228'
    a = RunTestCasesService()
    a.get_classification_result(folder_root,1)


