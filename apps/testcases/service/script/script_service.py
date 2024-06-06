# -*- coding: utf-8 -*-
# @Author : libeijie
# @Time : 2023/9/19 15:28


import os
import re
import shutil
import zipfile
import threading
import logging

from django.db import connection

from Salvation.settings import BASE_DIR,MEDIA_ROOT,MEDIA_URL
from common.cfg_helper import *
from testcases.models import ScriptConfig
from common.zipfile_helper import compress_file_to_zip
from common.file_helper import get_file_encoding

image_suffix = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
text_file_suffix = ('.txt', '.robot')
excel_suffix = ('.xls','.xlsx','xlsm')

script_component_lock = threading.Lock()
script_baseline_lock = threading.Lock()

logger = logging.getLogger('salvation')
class Folder:
    def __init__(self, id, name, path,type,parent_id):
        self.id = id
        self.name = name
        self.path = path
        self.children = []
        self.type = type
        self.parent_id = parent_id

class FolderWhole:
    def __init__(self, id, name, parent_id, level, path,tags=0):
        self.id = id
        self.name = name
        self.parent_id = parent_id
        self.level = level
        self.path = path
        self.children = []
        self.tags = tags

class ScriptService():
    def __init__(self):
        self.cursor = connection.cursor()
        cfg_file = ''.join([str(BASE_DIR), '/apps/data/config.cfg'])
        self.cfg_read = CfgHelper(cfg_file)

        #这里也要修改，可以改成使用media
        self.script_component_root_path = self.cfg_read.read_cfg_get_value_by_key('config_file', 'script_component_root_path')

        self.script_baseline_component_root_path = ''.join([str(MEDIA_ROOT), self.cfg_read.read_cfg_get_value_by_key('config_file', 'script_baseline_component_root_path')])

        #这里需要修改为只执行一次
        if not os.path.exists(self.script_component_root_path):
            os.makedirs(self.script_component_root_path)
        if not os.path.exists(self.script_baseline_component_root_path):
            os.makedirs(self.script_baseline_component_root_path)

    def get_all_script_component_path_data(self,):
        '''
        获取脚本套件
        :return:
        '''
        script_component_lock.acquire()
        try:
            sql = "select `id`,`name`,`parent_id`,`level`,`path`,`type` from testcase_script_config where tags='0'"
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            scirpt_component_list = self.handle_sql_data(result)
            return scirpt_component_list
        finally:
            script_component_lock.release()

    def get_all_script_baseline_path_data(self):
        '''
        获取基线包的信息
        :return:
        '''
        script_baseline_lock.acquire()
        try:
            sql = "select `id`,`name`,`parent_id`,`level`,`path`,`type` from testcase_script_config where tags='1'"
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            scirpt_component_list = self.handle_sql_data(result)
            return scirpt_component_list
        finally:
            script_baseline_lock.release()

    def handle_sql_data(self,result):
        '''
        将数据库数据处理成固定格式
        :param result:
        :return:
        '''
        scirpt_component_list = list()
        for item in result:
            script_component_id = item[0]
            script_component_name = item[1]
            script_component_parent_id = item[2]
            script_component_level = item[3]
            script_component_path = item[4]
            script_component_type = item[5]
            scirpt_component_list.append({'id': script_component_id, 'name': script_component_name,
                                          'parent_id': script_component_parent_id, 'level': script_component_level,
                                          'path': script_component_path, 'type': script_component_type})
        return scirpt_component_list



    def build_folder_structure(self,data, parent_id=None):
        '''
        将数据库树结构数据转包含folder的json结构
        :param data:数据库list
        :param parent_id:父id
        :return:
        '''
        folders = []
        for item in data:
            if item['parent_id'] == parent_id:
                folder = Folder(item['id'], item['name'], item['path'],item['type'],item['parent_id'])
                folder.children = self.build_folder_structure(data, folder.id)
                folder.children.sort(key=lambda k: k.type, reverse=False)
                folders.append(folder)
        return folders

    def folder_to_dict(self,folder):
        '''
        Folder对象转dict
        :param folder: Folder对象
        :return:
        '''
        folder_dict = {
            "id": folder.id,
            "name": folder.name,
            "path": folder.path,
            "type": folder.type,
            "parent_id":folder.parent_id,
            "children": [self.folder_to_dict(child) for child in folder.children]
        }
        return folder_dict

    def get_script_content_by_path(self,script_path,script_tags):
        '''
        通过物理地址获取脚本文件内容
        :param script_path: 脚本在服务器上的物理地址
        :param script_tags: 0-脚本套件；1-基线包；2-上传的自动化测试脚本绝对路径
        :return:
        '''
        code = 0 #0-正确读取文本格式；1-错误读取；2-正确读取图片文件路径；3-正确读取excel
        if script_tags == 0: #脚本套件
            script_path_absolute = os.path.join(self.script_component_root_path, script_path)
            script_component_lock.acquire()
        elif script_tags == 1: #基线包
            script_path_absolute = os.path.join(self.script_baseline_component_root_path, script_path)#'F:\\Salvation\\media\\\\files\\\\script_baseline\\\\IUMP-BSQ-AutoTest-I/IUMP-BSQ-AutoTest-I/Logsreport.html'
            script_baseline_lock.acquire()
        else: #上传的自动化测试脚本，此路径为绝对路径，且不用加锁
            script_path_absolute = script_path
        try:
            if script_path_absolute and os.path.isfile(script_path_absolute): #地址存在，可以为空，但不能为none，否则报错
                #读取文件内容
                try:
                    if script_path_absolute.endswith(image_suffix): #图片且非上传的自动化测试脚本绝对路径
                        if script_tags == 2:
                            file_contents = script_path_absolute
                        else:
                            file_contents = ''.join([str(MEDIA_URL), self.cfg_read.read_cfg_get_value_by_key('config_file', 'script_baseline_component_root_path'),script_path])
                        code = 2
                    elif script_path_absolute.endswith(excel_suffix): #excel
                        if script_tags == 2:
                            file_contents = script_path_absolute
                        else:
                            file_contents = ''.join([str(MEDIA_URL), self.cfg_read.read_cfg_get_value_by_key('config_file', 'script_baseline_component_root_path'),script_path])
                        code = 3
                    else:
                        with open(script_path_absolute, "r", encoding="utf-8") as file:
                            # 读取文件内容
                            file_contents = file.read()
                except Exception as e:
                    code = 1
                    file_contents = f"发生错误：'{str(e)}'"
            else:
                code = 1
                file_contents = f" '{script_path}' 文件不存在。"
            result = {'code':code,'file_contents':file_contents}
            logger.info(str(result))
            return result
        finally:
            if script_tags == 0: #0-脚本套件
                script_component_lock.release()
            elif script_tags == 1: #1-基线包
                script_baseline_lock.release()
    def update_script_file_content_physically(self,file_path,file_content):
        '''
        更改服务器上文件内容
        :param file_path: 服务器上文件位置
        :param file_content: 要更新的内容
        :return:
        '''
        script_path_absolute = os.path.join(self.script_component_root_path, file_path)
        script_component_lock.acquire()
        # 获取文件编码
        encoding = get_file_encoding(file_path)
        try:
            with open(script_path_absolute, "r+",encoding=encoding) as file:
                # 将文件指针移到文件开头
                file.seek(0)
                # 写入新内容
                file.write(file_content)
                # 截断文件以匹配新内容的长度
                file.truncate()
            msg = f"更新成功"
        except Exception as e:
            msg = f"发生错误：{str(e)}"
        finally:
            script_component_lock.release()
        return msg

    def insert_folder_if_not_exists(self,name, parent_id, level, path):
        # 查询数据库中是否存在相同路径的文件夹
        self.cursor.execute("SELECT id FROM testcase_script_config WHERE path='{0}'".format(path))
        folder_id = self.cursor.fetchone()

        if folder_id is None:
            # 不存在则插入新的文件夹记录
            sql = "INSERT INTO testcase_script_config (`name`, `parent_id`, `level`, `path`,`tags`,`type`) VALUES (%s, %s, %s, %s, %s,%s)"

            if name.endswith(text_file_suffix): #文件
                data = (name, parent_id, level, path,'0','1')
            else: #文件夹
                data = (name, parent_id, level, path,'0','0')
            # 将 None 替换为 NULL
            data = tuple(None if value is None else value for value in data)
            self.cursor.execute(sql,data)
            folder_id = self.cursor.lastrowid

        return folder_id

    def insert_script_component_folder(self,script_component_files,script_component_file_paths):
        '''
        将文件信息插入数据库，并保存到服务器
        :param script_component_files: 脚本套件文件
        :param script_component_file_paths: 脚本套件文件路径
        :return:
        '''
        script_component_lock.acquire()
        try:
            #上传(替换)文件到服务器，并插入数据库
            for index,script_component_file_path in enumerate(script_component_file_paths): #BSQ-CommonTestSuites/集成测试-静态类/静态类.robot
                script_path_tmp = os.path.join(self.script_component_root_path, script_component_file_path)
                folder_path = os.path.dirname(script_path_tmp)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                # 写入文件内容
                new_file = script_component_files[index]
                try:
                    # 保存新文件
                    with open(script_path_tmp, 'wb') as destination:
                        for chunk in new_file.chunks():
                            destination.write(chunk)
                except Exception as e:
                    # 删除服务器文件，不能删除文件夹，因为无法确认其父文件夹是此次生成还是之前就有
                    if os.path.exists(script_path_tmp):
                        os.remove(script_path_tmp)
                    msg = f"发生错误：{str(e)}"
                    return msg
                #存入数据库
                # 拆分路径，获取文件夹层级结构
                components = script_component_file_path.split('/')
                parent_id = None
                try:
                    for i, component in enumerate(components):
                        path = '/'.join(components[:i + 1])
                        level = i
                        # 检查数据库中是否存在相同路径的文件夹
                        parent_id = self.insert_folder_if_not_exists(component, parent_id, level, path)
                except Exception as e:
                    #删除服务器文件，不能删除文件夹，因为无法确认其父文件夹是此次生成还是之前就有
                    if os.path.exists(script_path_tmp):
                        os.remove(script_path_tmp)
                    #删除数据库数据，只能删除一条（例如BSQ-CommonTestSuites/集成测试-静态类/静态类.robot），无法删除其依次生成的父目录，因为无法确认父目录是此次生成还是之前就有
                    delete_item =  ScriptConfig.objects.filter(path=script_component_file_path)
                    if delete_item:
                        delete_item = delete_item[0]
                        delete_item.delete()
                    msg = f"发生错误：{str(e)}"
                    return msg
            msg = '新增成功！'
        finally:
            script_component_lock.release()
        return msg

    def update_script_component_folder(self,script_id,script_component_files,script_component_file_paths):
        '''
        更新脚本套件，包括数据库及服务器上的文件
        :param script_id:  要更新的脚本套件文件id
        :param script_component_files:  脚本套件文件
        :param script_component_file_paths: 脚本套件文件路径
        :return:
        '''
        script_component_lock.acquire()
        try:
            records_to_update = ScriptConfig.objects.get(pk=script_id)
            #1、数据库删除此条数据下的子文件(夹)
            self.delete_script_file_data(script_id)
            #2、服务器删除此条数据及其下子文件(夹)
            self.delete_script_file_physically(records_to_update)
            #3、服务器及数据库插入数据
            msg = self.update_script_file_data(records_to_update,script_component_files,script_component_file_paths)
            return msg
        finally:
            script_component_lock.release()

    def delete_script_file_data(self, folder_id):
        '''
        删除数据库中folder_id下的子文件夹及子文件
        :param folder_id: 前端传入的id
        :return:
        '''
        # 查询数据库，获取指定ID的文件夹数据
        records_to_delete = ScriptConfig.objects.filter(parent_id=folder_id)
        if not records_to_delete:
            return
        subfolders_ids = list()
        for record in records_to_delete:
            subfolders_ids.append(record.id)
        records_to_delete.delete()
        for subfolder_id in subfolders_ids:
            self.delete_script_file_data(subfolder_id)

    def delete_script_file_physically(self,records_to_update):
        '''
        删除服务器上的文件及子文件夹
        :param records_to_update：要在服务器中删除的文件
        :return:
        '''
        if not records_to_update:
            return
        records_to_update_path = os.path.join(self.script_component_root_path,records_to_update.path)
        #删除目录
        if os.path.exists(records_to_update_path):
            shutil.rmtree(records_to_update_path)

    def update_script_file_data(self,records_to_update,script_component_files,script_component_file_paths):
        '''
        更新/插入数据库数据
        :param records_to_update:要在数据库中更新的数据
        :param script_component_files:更新的文件
        :param script_component_file_paths:需插入的路径
        :return:
        '''
        if not records_to_update:
            return None
        match = re.match(r'(.+?)/([^/]+)$', records_to_update.path)
        if match:
            records_to_update_root_path = match.group(1) # BSQ-CommonTestSuites
        else: #最高级目录
            records_to_update_root_path = records_to_update.path

        new_records_name = script_component_file_paths[0].split('/')[0] #集成测试-静态类1/1.robot -> 集成测试-静态类1
        if records_to_update_root_path == records_to_update.path:
            records_to_update_path = new_records_name
        else:
            records_to_update_path = records_to_update_root_path+"/"+new_records_name
        #更新操作
        records_to_update.name = new_records_name
        records_to_update.path = records_to_update_path
        records_to_update.save()

        parent_id = records_to_update.id

        for index,script_component_file_path in enumerate(script_component_file_paths): #集成测试-静态类1/abc/1.robot
            match = re.search(r'/([^/].*)$', script_component_file_path)
            if match:
                script_component_file_path = match.group(1)

            script_component_file_path = records_to_update_path+"/"+script_component_file_path

            script_path_tmp = os.path.join(self.script_component_root_path,script_component_file_path)
            folder_path = os.path.dirname(script_path_tmp)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            # 写入文件内容
            new_file = script_component_files[index]
            try:
                # 保存新文件
                with open(script_path_tmp, 'wb') as destination:
                    for chunk in new_file.chunks():
                        destination.write(chunk)
            except Exception as e:
                # 删除服务器文件，不能删除文件夹，因为无法确认其父文件夹是此次生成还是之前就有
                if os.path.exists(script_path_tmp):
                    os.remove(script_path_tmp)
                msg = f"发生错误：{str(e)}"
                return msg
            # 存入数据库
            # 拆分路径，获取文件夹层级结构
            components = script_component_file_path.split('/')
            try:
                for i, component in enumerate(components):
                    path = '/'.join(components[:i + 1])
                    level = i
                    # 检查数据库中是否存在相同路径的文件夹
                    parent_id = self.insert_folder_if_not_exists(component, parent_id, level, path)
            except Exception as e:
                # 删除服务器文件，不能删除文件夹，因为无法确认其父文件夹是此次生成还是之前就有
                if os.path.exists(script_path_tmp):
                    os.remove(script_path_tmp)
                # 删除数据库数据，只能删除一条（例如BSQ-CommonTestSuites/集成测试-静态类/静态类.robot），无法删除其依次生成的父目录，因为无法确认父目录是此次生成还是之前就有
                delete_item = ScriptConfig.objects.filter(path=script_component_file_path)
                if delete_item:
                    delete_item = delete_item[0]
                    delete_item.delete()
                msg = f"发生错误：{str(e)}"
                return msg
        msg = '更新成功！'
        return msg

    def update_script_component_file(self,update_item_id,upload_script_component_files):
        '''
        单个更新文件
        :param update_item_id: 需更新的文件id
        :param upload_script_component_files: 需更新的文件
        :return:
        '''
        script_component_lock.acquire()
        try:
            update_item = ScriptConfig.objects.get(pk=update_item_id)
            if not update_item:#数据库中不存在
                return '不存在此条数据，请联系管理员！'

            update_item_path = update_item.path
            update_item_path_absolute = os.path.join(self.script_component_root_path,update_item_path)

            #删除文件
            folder_path = os.path.dirname(update_item_path_absolute)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            new_name = upload_script_component_files.name
            new_path_absolute = os.path.join(folder_path,new_name)

            if os.path.exists(update_item_path_absolute):
                os.remove(update_item_path_absolute)

            try:
                # 保存新文件
                with open(new_path_absolute, 'wb') as destination:
                    for chunk in upload_script_component_files.chunks():
                        destination.write(chunk)
            except Exception as e:
                # 删除服务器文件，不能删除文件夹，因为无法确认其父文件夹是此次生成还是之前就有
                if os.path.exists(new_path_absolute):
                    os.remove(new_path_absolute)
                msg = f"发生错误：{str(e)}"
                return msg

            #更新数据库数据
            try:
                update_item.name = new_name
                match = re.match(r'(.+?)/([^/]+)$',update_item.path)
                if match:
                    update_item_dir = match.group(1) #BSQ-CommonTestSuites11/集成测试-静态类/
                else:
                    update_item_dir = update_item.path

                new_path = update_item_dir+'/'+new_name
                update_item.path = new_path
                update_item.save()
            except Exception as e:
                # 删除服务器文件，不能删除文件夹，因为无法确认其父文件夹是此次生成还是之前就有
                if os.path.exists(new_path_absolute):
                    os.remove(new_path_absolute)
                # 删除数据库数据，只能删除一条（例如BSQ-CommonTestSuites/集成测试-静态类/静态类.robot），无法删除其依次生成的父目录，因为无法确认父目录是此次生成还是之前就有
                delete_item = ScriptConfig.objects.filter(path=update_item_path)
                if delete_item:
                    delete_item = delete_item[0]
                    delete_item.delete()
                msg = f"发生错误：{str(e)}"
                return msg
            msg = "更新成功！"
            return msg
        finally:
            script_component_lock.release()


    def download_script_folder(self,folder_id,tags):
        '''
        将文件生成为zip包
        :param folder_id:要下载的文件（夹）id
        :param tags:0-脚本套件；1-基线包
        :return:
        '''
        if tags == 0:
            script_component_lock.acquire()
        else:
            script_baseline_lock.acquire()
        try:
            dowload_item = ScriptConfig.objects.get(pk=folder_id)
            if not dowload_item: #数据库不存在数据
                return
            dowload_path = dowload_item.path #BSQ-CommonTestSuites11/集成测试-静态类
            dowload_name = dowload_item.name #集成测试-静态类
            if tags == 0: #脚本套件
                dowload_path_absolute = os.path.join(self.script_component_root_path,dowload_path) #F:\Salvation学习\脚本功能用到\配置_测试套件\BSQ-CommonTestSuites11\集成测试-静态类
            else: #基线包
                dowload_path_absolute = os.path.join(self.script_baseline_component_root_path,dowload_path)

            if dowload_name.endswith(text_file_suffix): #文件
                return dowload_path_absolute,dowload_name,True

            #压缩为zip文件
            zip_buffer = compress_file_to_zip(dowload_path_absolute)
            return zip_buffer,dowload_name,False
        finally:
            if tags == 0:
                script_component_lock.release()
            else:
                script_baseline_lock.release()

    def delete_script_folder(self,folder_id,tags):
        '''
        删除文件（夹）
        :param folder_id: 要删除的文件（夹）id
        :param tags: 0-脚本套件；1-基线包
        :return:
        '''
        if tags == 0:
            script_component_lock.acquire()
        else:
            script_baseline_lock.acquire()
        try:
            flag = 0 #执行状态，0-成功，1-失败
            delete_item = ScriptConfig.objects.get(pk=folder_id)
            #删除数据库中其下的子文件（夹）
            self.delete_script_file_data(folder_id)
            if not delete_item:
                return '不存在此条数据，请联系管理员！'

            #删除服务器文件
            delete_path = delete_item.path
            if tags == 0: #测试套件
                delete_path_absolute = os.path.join(self.script_component_root_path,delete_path) #F:\Salvation学习\脚本功能用到\配置_测试套件\BSQ-CommonTestSuites11\集成测试-静态类
            else: #基线包
                delete_path_absolute = os.path.join(self.script_baseline_component_root_path, delete_path)

            delete_name = delete_item.name
            try:
                if os.path.exists(delete_path_absolute):
                    #if delete_name.find('.txt') >= 0 or delete_name.find('.robot') >= 0:  # 文件
                    if delete_name.endswith(text_file_suffix):  # 文件
                        os.remove(delete_path_absolute)
                    else:
                        shutil.rmtree(delete_path_absolute)
            except Exception as e:
                flag = 1
                msg_error = str(e)
            finally:
                #删除此条数据
                delete_item.delete()
            if flag == 0:
                msg = '删除成功！'
            else:
                msg = '发生错误：{}'.format(msg_error)
            return msg
        finally:
            if tags == 0:
                script_component_lock.release()
            else:
                script_baseline_lock.release()

    def upload_script_baseline_folder(self,script_baseline_files):
        '''
        处理上传的脚本基线包，解压zip文件
        :param script_baseline_files:
        :return:
        '''
        code = 0
        script_baseline_lock.acquire()
        script_baseline_files_name = os.path.splitext(script_baseline_files.name)[0]
        try:
            exist_flag = 0 #在数据库中是否存在，0-不存在；1-存在
            zip_file_path = os.path.join(self.script_baseline_component_root_path, script_baseline_files.name)

            root_dir = os.path.join(self.script_baseline_component_root_path, script_baseline_files_name)# 解压后的根目录 F:\Salvation学习\脚本功能用到\配置_基线包\IUMP-BSQ-AutoTest-F
            if os.path.exists(root_dir): #已存在此文件，则删除服务器文件，且删除数据库此数据下的子项
                shutil.rmtree(root_dir)
                parent_dir =  os.path.splitext(script_baseline_files.name)[0] #IUMP-BSQ-AutoTest-F
                root_item = ScriptConfig.objects.filter(path=parent_dir)
                if root_item:
                    exist_flag = 1
                    root_item = root_item[0]
                    root_item_id = root_item.id
                    self.delete_script_file_data(root_item_id)

            # 保存上传的ZIP文件，此时上传的zip文件会以zip形式保存到服务器上。如果已存在，则更新
            with open(zip_file_path, 'wb') as destination:
                for chunk in script_baseline_files.chunks():
                    destination.write(chunk)
            #解压zip文件，并删除原zip文件
            try:
                with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                    file_list = zip_ref.namelist()
                    if file_list[0] == script_baseline_files_name + '/': #嵌套zip（即zip下包含根目录）
                        root_dir = self.script_baseline_component_root_path
                    for file_info in zip_ref.infolist():
                        try:
                            file_info.filename = file_info.filename.encode('cp437').decode('utf-8')
                        except:
                            try:
                                file_info.filename = file_info.filename.encode('cp437').decode('gbk')
                            except:
                                pass
                        zip_ref.extract(file_info, root_dir)
            except Exception as e:
                #删除文件
                if os.path.exists(zip_file_path):
                    os.remove(zip_file_path)
                if os.path.exists(os.path.join(self.script_baseline_component_root_path, script_baseline_files_name)):  # 已存在此文件，则删除服务器文件
                    shutil.rmtree(os.path.join(self.script_baseline_component_root_path, script_baseline_files_name))
                code = 1
                msg = f'新增报错：str{e}'
                return {'code':code,'msg':msg}
            try:
                if os.path.exists(zip_file_path):
                    os.remove(zip_file_path)
                root_dir = os.path.join(self.script_baseline_component_root_path, script_baseline_files_name)
                print(root_dir)
                # 处理解压后的文件结构并存入数据库
                def insert_folder_structure(root_path, parent_folder, parent_id, level):
                    # 获取当前文件夹下的子文件夹和文件
                    items = os.listdir(root_path)

                    for item in items:
                        item_path = os.path.join(root_path, item)
                        if os.path.isdir(item_path):
                            # 如果是文件夹，创建一个Folder对象并插入到数据库
                            folder = ScriptConfig(name=item, parent_id=parent_id, level=level,
                                            path=str(os.path.join(parent_folder.path, item) if parent_folder else item).replace('\\','/'),tags=1,type=0)
                            folder.save()
                            # 递归处理子文件夹
                            insert_folder_structure(item_path, parent_folder=folder, parent_id=folder.id, level=level + 1)
                        else:
                            # 如果是文件，直接插入到数据库
                            file = ScriptConfig(name=item,parent_id=parent_id, level=level,
                                          path=str(os.path.join(parent_folder.path, item) if parent_folder else item).replace('\\','/'),tags=1,type=1)
                            file.save()
                # 如果没有父文件夹，表示当前是根文件夹，创建一个Folder对象并插入到数据库
                if exist_flag == 1: #数据库中已存在，则更新此条数据
                    pass
                else:
                    root_item = ScriptConfig(name=os.path.basename(root_dir),level=0, path=os.path.basename(root_dir), tags=1)
                    root_item.save()
                    print(root_item.id)
                insert_folder_structure(root_dir,parent_folder=root_item,parent_id=root_item.id,level=1)
            except Exception as e:
                # 删除文件
                if os.path.exists(zip_file_path):
                    os.remove(zip_file_path)
                if os.path.exists(root_dir):  # 已存在此文件，则删除服务器文件，且删除数据库此数据下的子项
                    shutil.rmtree(root_dir)
                #删除数据库此条数据下的子数据
                self.delete_script_file_data(root_item.id)
                #删除数据库中此条数据
                root_item.delete()
                code = 1
                msg = f'新增报错：str{e}'
                return {'code':code,'msg':msg}
            msg = '新增成功！'
            return {'code':code,'msg':msg}
        finally:
            script_baseline_lock.release()

def get_script_baselines_service(level,tags):
    '''
    获取基线包名称和id
    :return:
    '''
    script_baseline_names_ids = []
    script_baseline_data = ScriptConfig.objects.filter(parent_id=None,level=level,tags=tags)
    for script_baseline_item in script_baseline_data:
        script_baseline_item_name = script_baseline_item.name
        script_baseline_item_id = script_baseline_item.id
        script_baseline_names_ids.append({"name":script_baseline_item_name,"id":script_baseline_item_id})
    return script_baseline_names_ids

# if __name__ == "__main__":
#     ss = ScriptService()
#     scirpt_component_list = [
#         {"id": 1, "name": "BSQ-CommonTestSuites", "parent_id": None, "level": 0, "path": "D://BSQ-CommonTestSuites"},
#         {"id": 2, "name": "回归测试-流程类", "parent_id": 1, "level": 1, "path": "D://BSQ-CommonTestSuites//回归测试-流程类"},
#         {"id": 3, "name": "集成测试-静态类", "parent_id": 1, "level": 1, "path": "D://BSQ-CommonTestSuites//集成测试-静态类"},
#         {"id": 4, "name": "流程类.robot", "parent_id": 2, "level": 2, "path": "D://BSQ-CommonTestSuites//回归测试-流程类//流程类.robot"},
#         {"id": 5, "name": "静态类.robot", "parent_id": 3, "level": 2, "path": "D://BSQ-CommonTestSuites//集成测试-静态类//静态类.robot"},
#         {"id": 6, "name": "集成测试-控件类", "parent_id": 1, "level": 1, "path": "D://BSQ-CommonTestSuites//集成测试-控件类"},
#         # 添加其他记录...
#     ]
#     f = ss.build_folder_structure(scirpt_component_list)
#     print(f)