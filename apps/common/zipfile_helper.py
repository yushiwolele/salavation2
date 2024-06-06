# -*- coding: utf-8 -*-            
# @Author : libeijie
# @Time : 2023/10/18 17:08

import zipfile
import io
import os

def compress_file_to_zip(file_path_absolute):
    '''
    将文件压缩为zip文件
    :param file_path_absolute:
    :return:
    '''
    # 创建一个ZIP文件的内存对象
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 遍历文件夹中的文件并将它们添加到ZIP文件
        for root, dirs, files in os.walk(file_path_absolute):
            for file in files:
                file_path = os.path.join(root, file)
                # 计算在ZIP文件中的相对路径
                relative_path = os.path.relpath(file_path, file_path_absolute)
                zipf.write(file_path, relative_path)
    return zip_buffer