# -*- coding: utf-8 -*-            
# @Author : libeijie
# @Time : 2023/10/17 14:31

import copy
import logging
import xlrd
import os

class ExcelHelperForXlrd(object): #读取单文件速度依然很快
    def __init__(self):
        self.xlrd_excelbook = None
    def read_excel_by_upload(self,file):
        '''
        处理上传的文件
        :param file: 上传的文件
        :return:
        '''
        try:
            self.xlrd_excelbook = xlrd.open_workbook(file_contents=file.getvalue())
            return True
        except Exception as e:
            logging.warning('Exception',exc_info=1)
            return False

    def read_excel_by_path(self,filepath):
        '''
        根据文件路径获取文件
        :param filepath: 文件路径
        :return:
        '''
        if os.path.exists(filepath):
            logging.warning('文件不存在：%s',filepath)
            return False
        try:
            self.xlrd_excelbook = xlrd.open_workbook(filepath)
            return True
        except:
            logging.warning('Exception',exc_info=1)
            return False

    def get_cells_by_sheetname_for_read(self,sname):
        '''
        处理file，获取excel中sname sheet页的数据
        :param sname:sheet名称
        :return: 返回4元素元组（取值矩阵，类型矩阵，总行数，总列数）
        '''
        sheet_names_list = self.xlrd_excelbook.sheet_names()
        if sname not in sheet_names_list:
            logging.error("[{0}]sheet页不存在！".format(sname))
            return None, None, None, None
        try:
            excelsheet = self.xlrd_excelbook.sheet_by_name(sname)
        except Exception as e:
            logging.error('报错信息：' + repr(e) + ',报错的行号:' + str(e.__traceback__.tb_lineno))
            return None, None, None, None

        nr = excelsheet.nrows  # 有效行数
        nc = excelsheet.ncols  # 有效果列数
        if nr == 0 or nc == 0:
            logging.warning('读取到的有效行数是[%s](最大5000行)，有效列数是[%s](最大100列)。请检查excel文档：', nr, nc)
            return None, None, None, None
        if nr >= 5000 or nc >= 100:
            logging.warning('读取到的有效行数是[%s](最大5000行)，有效列数是[%s](最大100列)已经超出正常范围！请检查excel文档：', nr, nc)
            return None, None, None, None

        valuematrix = []
        ctypematrix = []
        for x in range(0, nr):  # 循环行
            valuematrix.append([])
            ctypematrix.append([])
            for y in range(0, nc):  # 循环列
                # 无法获得确切行数列数，取数会出错，可忽略异常，把所有能取出的数抽取
                try:
                    cty = excelsheet.cell_type(x,y) #0-empty,1-string,2-number,3-date,4-boolean,5-error  共5种类型
                    val = excelsheet.cell_value(x,y)
                    if cty == 2 and str(val).split('.')[1] == '0': #number类型 小数位如果是‘.0’就需要去掉
                        val = str(val).split('.')[0]
                    else:
                        val = val.strip()
                except:
                    val = ''
                    cty = 6
                    pass
                valuematrix[x].append(val)
                ctypematrix[x].append(cty)
        return valuematrix, ctypematrix, nr, nc

class LoadExcelData:
    def __init__(self):
        self.data_list = None
    def load_from_excel_by_upload(self,file, sname, rowbegin):
        '''
        获取excel中sheet页的数据
        :param file:上传的文件
        :param sname:sheet页名
        :param rowbegin:开始读取的开始行号（从0开始）
        :return:数据二维列表（为None表示读取失败）
        '''
        self.data_list = None
        eh = ExcelHelperForXlrd()
        if not eh.read_excel_by_upload(file):
            return None
        (vm, cm, nr, nc) = eh.get_cells_by_sheetname_for_read(sname)
        if not vm:
            return None
        self.data_list = copy.deepcopy(vm[rowbegin:][:])
        return self.data_list

