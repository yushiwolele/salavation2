# -*- coding: utf-8 -*-            
# @Author : libeijie
# @Time : 2023/12/26 14:23

from celery import shared_task
import os
import shutil
from Salvation.settings import BASE_DIR

@shared_task
def delete_files_task():
    print('删除操作===============')
    folder_path = os.path.join(BASE_DIR,'tmp')
    # 添加逻辑来删除文件或文件夹
    shutil.rmtree(folder_path)
    os.makedirs(folder_path)  # 重新创建空文件夹