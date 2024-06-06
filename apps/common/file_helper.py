# -*- coding: utf-8 -*-            
# @Author : libeijie
# @Time : 2023/10/30 16:42

import os
import shutil
import logging
import codecs
import chardet

logger = logging.getLogger('salvation')

def createdir(path):
    '''
    创建目录树
    :param path:待生成的目录
    :return: True/False
    '''
    try:
        if not os.path.isdir(path):
            os.makedirs(path)
    except Exception as e:
        logger.error('入参：'+str(path)+',报错信息:' + repr(e) + ',报错的行号:' + str(e.__traceback__.tb_lineno))
        return False
    return True

def rmtreedir(path):
    '''
    删除目录树
    param path: 待删除的目录
    :return:True/False
    '''
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
    except Exception as e:
        logger.error('入参：'+str(path)+',报错信息:' + repr(e) + ',报错的行号:' + str(e.__traceback__.tb_lineno))
        return False
    return True

def clear_directory(path):
    '''
    清空文件夹下的内容
    :param path:
    :return:
    '''
    try:
        # 检查目录是否存在
        if os.path.exists(path):
            # 删除目录及其所有内容
            shutil.rmtree(path)
            # 重新创建空目录
            os.makedirs(path)
        else:
            # 重新创建空目录
            os.makedirs(path)
    except Exception as e:
        logger.error('入参：' + str(path) + ',报错信息:' + repr(e) + ',报错的行号:' + str(e.__traceback__.tb_lineno))
        return False
    return True

def write_to_file(path, name,data,postfix ="txt"):
    '''
    写文件
    :param path: 待生成的目录
    :param name: 写文件的名称(没有文件后缀)
    :param data: 写的数据
    :param postfix: 文件后缀
    :return: True/False
    '''
    if not path:
        logger.error("没有目录[%s]"%(path))
        return False
    try:
        mf = codecs.open(r'{0}\{1}.{2}'.format(path,name,postfix), mode='w',encoding='UTF-8')
        mf.write(data)
        mf.close()
    except Exception as e:
        logger.error('入参：' + str(path)+';'+str(name)+ ',报错信息:' + repr(e) + ',报错的行号:' + str(e.__traceback__.tb_lineno))
        return False
    return True

def read_to_file(filename):
    '''
    读文件
    :param filename: 带路径的文件名（有文件后缀）
    :return:文件内容，异常返回空
    '''
    try:
        filecontent = (codecs.open(filename,mode='r',encoding='UTF-8')).read()
    except Exception as e:
        logger.error('入参：' + str(filename)+ ',报错信息:' + repr(e) + ',报错的行号:' + str(e.__traceback__.tb_lineno))
        return ''
    return filecontent

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

def detect_encoding(data):
    '''
    获取字节编码
    :param data: 字节
    :return:
    '''
    result = chardet.detect(data)
    return result['encoding']

def convert_file_encoding(file_path, target_encoding='utf-8'):
    '''
    转编码
    :param file_path: 文件路径
    :param target_encoding: 目标编码
    :return:
    '''
    # 获取当前文件编码
    source_encoding = get_file_encoding(file_path)

    # 打开文件并用源编码读取内容
    with open(file_path, 'r', encoding=source_encoding) as source_file:
        content = source_file.read()

    # 将内容用目标编码写回文件
    with open(file_path, 'w', encoding=target_encoding) as target_file:
        target_file.write(content)