# -*- coding: utf-8 -*-            
# @Author : libeijie
# @Time : 2023/10/26 14:36

import uuid
import os
import subprocess
import threading
import logging

from common.cfg_helper import *
from Salvation.settings import BASE_DIR
from common.zipfile_helper import compress_file_to_zip
from common.file_helper import rmtreedir,detect_encoding

script_runEnv_lock = threading.Lock()

logger = logging.getLogger('salvation')
class RunEnvFreeService():
    def __init__(self):
        cfg_file = ''.join([str(BASE_DIR), '/apps/data/config.cfg'])
        self.cfg_read = CfgHelper(cfg_file)
        self.script_runEnv_tmp = self.cfg_read.read_cfg_get_value_by_key('config_file','script_runEnv')

    def get_folder_run_pyinstall(self,script_component_files,script_component_file_paths,folder_name):
        '''
        存储上传的文件夹，运行pyinstaller命令生成dist文件夹
        :param script_component_files: 上传的文件
        :param script_component_file_paths:上传的文件路径
        :param folder_name:上传文件的根目录名
        :return:
        '''
        #先存为临时文件+uuid
        script_file_uuid = uuid.uuid4()
        script_folder_tmp = os.path.join(self.script_runEnv_tmp,'script_folder_tmp_'+str(script_file_uuid))

        target_encoding = 'utf-8'
        for index, script_component_file_path in enumerate(script_component_file_paths):
            script_path_tmp = os.path.join(script_folder_tmp, script_component_file_path)
            folder_path = os.path.dirname(script_path_tmp)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            # 写入文件内容
            new_file = script_component_files[index]
            try:
                # 保存新文件
                with open(script_path_tmp, 'wb') as destination:
                    for chunk in new_file.chunks():
                        source_encoding = detect_encoding(chunk)
                        if source_encoding == None:
                            destination.write(chunk)
                            continue
                        decoded_data = chunk.decode(source_encoding, errors='ignore')  # 'ignore' 参数表示在解码过程中遇到无法解码的字符时忽略
                        encoded_data = decoded_data.encode(target_encoding)
                        destination.write(encoded_data)
            except Exception as e:
                print(e)
                logger.error('报错信息：' + repr(e) + ',报错的行号:' + str(e.__traceback__.tb_lineno))
                rmtreedir(script_folder_tmp)
                msg = f"发生错误：{str(e)}"
                return {'code':1,'msg':msg}

        script_runEnv_lock.acquire()
        os.environ['PROJECT_PATH'] = script_folder_tmp + '/' + folder_name + '/'  # 设置环境变量-项目路径
        os.environ['SELF_CONFIG_PATH'] = str(BASE_DIR) + '/' + 'apps' + '/' + 'common' + '/'  # 设置环境变量-self_config.txt readme.txt
        try:
            #执行 pyinstaller
            #subprocess.run(["pyinstaller", "--distpath", self.script_runEnv_tmp,'RunEnvFreeTest.spec'], shell=True) #Django应用的运行目录不同于a.py所在的目录，无法直接访问RunEnvFreeTest.spec，需要用绝对路径
            # 获取当前文件的绝对路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # 拼接绝对路径
            spec_file_path = os.path.join(current_dir, 'RunEnvFreeTest.spec')
            subprocess.run(["pyinstaller", "--distpath", self.script_runEnv_tmp, spec_file_path], shell=True)
            #删除build文件夹
            build_folder = os.path.join(BASE_DIR,'build')
            rmtreedir(build_folder)

            zip_buffer = compress_file_to_zip(self.script_runEnv_tmp + '/RunEnvFree')
            # 删除文件
            rmtreedir(script_folder_tmp)
            rmtreedir(self.script_runEnv_tmp + '/RunEnvFree')

        except Exception as e:
            # 删除文件
            rmtreedir(script_folder_tmp)
            logger.error('报错信息：' + repr(e) + ',报错的行号:' + str(e.__traceback__.tb_lineno))
            msg = f"发生错误：{str(e)}"
            return {'code': 1, 'msg': msg}
        finally:
            # 删除环境变量
            if 'PROJECT_PATH' in os.environ:
                os.environ.pop('PROJECT_PATH')
            if 'SELF_CONFIG_PATH' in os.environ:
                os.environ.pop('SELF_CONFIG_PATH')
            script_runEnv_lock.release()


        return {'code': 0, 'msg': zip_buffer}


# if __name__ == '__main__':
#     os.environ['PROJECT_PATH'] = 'F:\\Salvation\\excbak\\runenvfreepackage\\'
#     print(os.environ.get('PROJECT_PATH'))
#     subprocess.run(["pyinstaller", "--distpath", "F:\\Salvation学习\\runEnv", 'RunEnvFreeTest.spec'], shell=True)
#     # 删除build文件夹
#     build_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'build')
#     print(build_folder)
#     shutil.rmtree(build_folder)
#     # 删除环境变量
#     if 'PROJECT_PATH' in os.environ:
#         os.environ.pop('PROJECT_PATH')








