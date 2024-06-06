# -*- coding: utf-8 -*-            
# @Author : libeijie
# @Time : 2023/10/16 11:15

import os
import logging

import io
import shutil
import zipfile
from datetime import datetime
import uuid

from Salvation.settings import BASE_DIR,MEDIA_ROOT
from common.cfg_helper import *
from common.excel_helper import LoadExcelData
from testcases.models import ScriptConfig
from common.zipfile_helper import compress_file_to_zip
from common.file_helper import rmtreedir,createdir,write_to_file,read_to_file

logger = logging.getLogger('salvation')

class GenerateAutolestCases:
    def __init__(self):
        self.testcase_sheetname ='前端功能页面配置' #读取目标sheet页名
        self.testcase_sheetname_rowbegin = 2
        self.testcase_sheetname_function_rowbegin = 0
        self.suite_file_path = None
        self.TestSuites_flow ='回归测试-流程类'
        self.TestSuites_static ='集成测试-静态类'
        self.TestSuites_widget = '集成测试-控件类'
        self.config_file_path = None
        self.svn_root = None
        self.baseline_root = None
        self.dir00 = '00dir_project.txt'
        self.dir01 = '01dir_first.txt'
        self.dir02 = '02dir_second.txt'
        self.dir03 = '03dir_third.txt'
        self.dir04 = '04dir_fourth.txt'
        self.dir05 = '05dir_function.txt'
        self.extract_AutoTest_list= ['Conf',
                                    'Files',
                                    'Logs',
                                    'readme.txt',
                                    'update.txt',
                                    'Programs\\自定义用户关键字',
                                    'Path',#原来是:path_py\\element_path.py
                                    '自动化测试-评审及讨论记录表-YYYYMMDD.xlsx',
                                    '自动化测试-建表及插数SQL.xLsx']

        cfg_file = ''.join([str(BASE_DIR), '/apps/data/config.cfg'])
        self.cfg_read = CfgHelper(cfg_file)
        self.file_config_path  = self.cfg_read.read_cfg_get_value_by_key('config_file','file_config_path') #F:\\Salvation学习\\配置
        self.file_template_path  = self.cfg_read.read_cfg_get_value_by_key('config_file','file_template_path') #F:\\SalvationStudy\\template
        self.script_component_root_path = self.cfg_read.read_cfg_get_value_by_key('config_file','script_component_root_path') #F:\\Salvation学习\\脚本功能用到\\配置_测试套件
        #\\files\\script_baseline\\    F:\Salvation\media\files\script_baseline
        self.script_baseline_component_root_path = ''.join([str(MEDIA_ROOT),self.cfg_read.read_cfg_get_value_by_key('config_file','script_baseline_component_root_path')])

    def generate_auto_test_cases(self,system,testcase_file,script_baseline_id):
        '''
        根据测试用例，自动生成自动化测试套
        :param system: 测试系统类型
        :param testcase_file: 测试用例文件
        :param script_baseline_id: 基线包id
        :return:
        '''
        flg = True
        #通过id获取基线包名称
        script_baseline = ScriptConfig.objects.get(pk=script_baseline_id)
        if not script_baseline:
            logger.error('基线包不存在：'+str(script_baseline))
            return {'code':1,'data':'基线包不存在，请联系管理员！'}
        else:
            self.script_baseline_name = script_baseline.name

        self.file_uuid = str(uuid.uuid4())
        self.tmp_src_path = os.path.join(str(BASE_DIR), "tmp", "src"+'-'+self.file_uuid)
        self.tmp_tar_path = os.path.join(str(BASE_DIR), "tmp", "tar"+'-'+self.file_uuid)
        baseline_name = system+'-AutoTest-I-'+datetime.now().strftime("%Y%m%d")+"-"+self.file_uuid #EDW-AutoTest-I-20231019-4f3dc88e-1efb-4a57-adc8-75e017c909a3
        self.baseline_root = os.path.join(str(BASE_DIR), "tmp", "script",baseline_name)
        self.project_name = 'Programs'

        cf = configparser.ConfigParser()
        cf.read('config.ini')
        self.config_file_path = os.path.join(self.script_component_root_path,system+"-ProjectTreeConfig")   # 测试套件
        self.suite_file_path = os.path.join(self.script_component_root_path,system+"-CommonTestSuites") # 测试套件
        self.TestSuites_flow_path = os.path.join(self.suite_file_path,self.TestSuites_flow)
        self.TestSuites_static_path = os.path.join(self.suite_file_path,self.TestSuites_static)
        self.TestSuites_widget_path = os.path.join(self.suite_file_path, self.TestSuites_widget)
        self.svn_root = self.script_baseline_component_root_path #基线包路径
        self.autotest_zip_path = os.path.join(self.svn_root,self.script_baseline_name) #基线包路径+名称

        # 将文件内容存储在内存中，防止多次读取上传文件指针移至末尾报错
        file_content = io.BytesIO(testcase_file.read())
        # 读取测试用例文档
        extract_excel = LoadExcelData()
        data_list = extract_excel.load_from_excel_by_upload(file_content, self.testcase_sheetname, self.testcase_sheetname_rowbegin)
        if not data_list:
            message = '数据异常，请查看文档sheet页[%s]!'% (self.testcase_sheetname)
            logger.error(message)
            return {'code':1,'data':message}
        path_root = os.path.join(self.baseline_root, self.project_name) #F:\Salvation\tmp\script\BSQ-AutoTest-I-20231017-4f3dc88e-1efb-4a57-adc8-75e017c909a3\\Programs

        for row in data_list:
            path1, path2, path3, path4, path5,function_id = row[0], row[1], row[2], row[3], row[4],row[5]
            if not path1:
                break
            path5 = path5.replace('/'," / ")
            # 创建目录
            function_path = os.path.join(path_root, path1, path2, path3, path4, path5)
            if not createdir(function_path):
                logger.error('目录生成失败：' + str(function_path))
                return {'code':1,'data':'目录生成失败，请联系管理员！'}
            test_path1 = os.path.join(path_root, path1)
            test_path2 = os.path.join(path_root, path1, path2)
            test_path3 = os.path.join(path_root, path1, path2, path3)
            test_path4 = os.path.join(path_root, path1, path2, path3,path4)
            test_path5 = os.path.join(path_root, path1, path2, path3,path4,path5)

            txt0 = read_to_file(os.path.join(self.config_file_path, self.dir00)) #F:\Salvation学习\脚本功能用到\配置_测试套件\BSQ-ProjectTreeConfig\00dir_project.txt
            txt1 = read_to_file(os.path.join(self.config_file_path, self.dir01))
            txt2 = read_to_file(os.path.join(self.config_file_path, self.dir02))
            txt3 = read_to_file(os.path.join(self.config_file_path, self.dir03))
            txt4 = read_to_file(os.path.join(self.config_file_path, self.dir04))
            txt5 = read_to_file(os.path.join(self.config_file_path, self.dir05))
            #拷贝配置txt，并替换txt内的变量
            num = 0
            if not write_to_file(path_root, '__init__', txt0):
                flg = False
            if not write_to_file(test_path1,'__init__', txt1.format(name=path1)):
                flg = False
            num += 1
            if os.path.normpath(test_path1) != os.path.normpath(test_path2):
                num += 1
                if not write_to_file(test_path2, '__init__', txt2.format(name=path2)):
                    flg = False
            if os.path.normpath(test_path2) != os.path.normpath(test_path3):
                num += 1
                if not write_to_file(test_path3, '__init__', txt3.format(name=path3)):
                    flg = False
            if os.path.normpath(test_path3) != os.path.normpath(test_path4):
                num += 1
                if not write_to_file(test_path4,'__init__', txt4.format(name=path4)):
                    flg = False
            if os.path.normpath(test_path4) != os.path.normpath(test_path5):
                num += 1
                function_txt = txt5.format(name=path5, test_path='../'* num, function_id=function_id)
                if not write_to_file(test_path5,'__init__', function_txt):
                    flg = False
            # 拷贝测试套件
            data_function_list = extract_excel.load_from_excel_by_upload(file_content, path5,self.testcase_sheetname_function_rowbegin)

            if not data_function_list:
                msg = '数据异常，请查看文档sheet页[%s]!'%(self.testcase_sheetname)
                logger.error(msg)
                return {'code':1,'data':msg}

            test_suite_name_list = []
            for count, col_value in enumerate(data_function_list[0]):
                if col_value =='用例执行方式':
                    index = count # [用例执行方式]在的列号
                elif col_value == 'Test Suite':
                    index1 = count# [Test Suite]在的列号
                else:
                    pass

            for data_function in data_function_list[1:]:  # 获取控件列表，并去重
                auto_flg, test_suite_name = data_function[index], data_function[index1] #自动化/手工  静态类...
                if auto_flg.strip() =='自动化' and test_suite_name.strip() not in test_suite_name_list:
                    test_suite_name_list.append(test_suite_name.strip()) #[流程类，静态类，查询时段-清算日期，左右互选框-交收会员...]

            for test_suite in test_suite_name_list:#读取对应模板，替换变量输出
                if '静态类' == test_suite:
                    test_suite_mode = read_to_file(os.path.join(self.TestSuites_static_path, test_suite + '.robot'))
                    if not test_suite_mode:
                        flg = False
                        continue
                    robot1 = test_suite_mode.format(test_path='../' * num, function_id=function_id)

                elif '流程类' in test_suite:
                    test_suite_mode = read_to_file(os.path.join(self.TestSuites_flow_path, test_suite + '.robot'))
                    if not test_suite_mode:
                        flg = False
                        continue
                    robot1 = test_suite_mode.format(name=path5,test_path='../' * num,function_id=function_id)

                else: #控件类
                    test_suite_tmp = test_suite.split('-')[0]
                    test_suite_mode = read_to_file(os.path.join(self.TestSuites_widget_path, test_suite_tmp+'.robot'))
                    if not test_suite_mode:
                        flg = False
                        continue
                    robot1 = test_suite_mode.format(name=path5,test_path='../' * num, function_id=function_id)
                if not write_to_file(test_path5, test_suite, robot1, 'robot'):
                    flg = False
        # 拷贝公共测试目录及脚本
        if not self.zip_extract():
            logger.error('引用基线包:[%s]失败。'%(self.autotest_zip_path))
            return {'code':1,'data':'引用基线包失败，请联系管理员！'}
        if not flg:
            logger.error('脚本套件有误。')
            return {'code':1,'data':'脚本套件有误，请联系管理员！'}
        # 压缩为zip文件 -- 这里会有问题吗？内存中生成zip，会有并行安全问题吗？
        zip_buffer = compress_file_to_zip(self.baseline_root)
        logger.info("自动化测试脚本生成路径: [%s]"%(self.baseline_root))
        #删除本次生成的临时文件 -- 不处理异常，因为即使删除失败，此时自动化化脚本已生成。--后续可做定时删除固定日期前的文件
        rmtreedir(self.baseline_root)
        return {'code':0,'data':{'file':zip_buffer,'file_name':system+'-AutoTest-I-'+datetime.now().strftime("%Y%m%d")}}

    def zip_extract(self):
        '''
        解压自动化测试用例全集，并贝指定的文档到项目自动化测试用例中.
        :return: True / False
        '''
        # 删除临时目录
        if not rmtreedir(self.tmp_src_path):
            return False
        # 对基线包压缩
        file_uuid_len = len(self.file_uuid)
        shutil.make_archive(os.path.join(str(BASE_DIR), "tmp",self.script_baseline_name+"-"+self.file_uuid), 'zip', self.autotest_zip_path)
        autotest_zip_path_tmp = os.path.join(str(BASE_DIR), "tmp",self.script_baseline_name+"-"+self.file_uuid+".zip") #临时基线包zip路径

        zipfilename = os.path.basename(autotest_zip_path_tmp)  # 获取zip文件名  IUMP-BSQ-AutoTest-F-4f3dc88e-1efb-4a57-adc8-75e017c909a3.zip
        zipfilepath = os.path.dirname(autotest_zip_path_tmp)#获取zip文件路径  F:\Salvation\tmp

        file_list = os.listdir(zipfilepath)
        #遍历zip文件路径，获取到真实zip文件，防止版本号不一致的情况
        for file in file_list:
            if os.path.isfile(os.path.join(zipfilepath,file)) and file == zipfilename:
                zipfilename = file
                break

        self.extract_AutoTest_list = [i.lower() for i in self.extract_AutoTest_list]

        myzip = zipfile.ZipFile(os.path.join(zipfilepath, zipfilename),'r')
        #print(myzip.namelist())
        tmp_extract_list = [] #获取在zip中已找到的目录或文件
        try:
            for fn in myzip.namelist():  # 遍历zip目录及文件
                flg = False
                #code_flag = 0
                tmp_rel_dir = os.path.normpath(fn).lower()
                # try:
                #     tmp_rel_dir = os.path.normpath(fn.encode('cp437').decode('gbk')).lower() #os.path.normpath()转换路径fn.encode('cp437').decode('gbk')转编码，由乱码转换为GBK编码
                # except:
                #     try:
                #         code_flag = 1
                #         tmp_rel_dir = os.path.normpath(fn.encode('cp437').decode('utf-8')).lower()
                #     except:
                #         code_flag = 2
                #         tmp_rel_dir =os.path.normpath(fn).lower()

                for file in self.extract_AutoTest_list:#遍历要拷贝的列表
                    if file == tmp_rel_dir[:len(file)]:#如果 要贝的列表在zip列表中找到，则退出循环，并只fg状态为True
                        flg = True
                        tmp_extract_list.append(file)
                        break
                if not flg:  #在zip的当前循环中没有在要拷贝的内容，则进入下一个循环
                    continue
                myzip.extract(fn,self.tmp_src_path)#找到要贝的内容，提取zip内容，并获取提取后的路径
                if os.path.isfile(os.path.join(self.tmp_src_path, fn)):#提取出来的是文件
                    #转码相对路径中的乱码，并删除zip文件的相对根目录
                    tmp_dir = os.path.dirname(fn).replace(zipfilename[:-(4+file_uuid_len+1)], '', 1)
                    # if code_flag == 0:
                    #     tmp_dir = os.path.dirname(fn.encode('cp437').decode('gbk')).replace(zipfilename[:-(4+file_uuid_len+1)],'',1)
                    # elif code_flag == 1:
                    #     tmp_dir = os.path.dirname(fn.encode('cp437').decode('utf-8')).replace(zipfilename[:-(4+file_uuid_len+1)], '', 1)
                    # else:
                    #     tmp_dir = os.path.dirname(fn).replace(zipfilename[:-(4+file_uuid_len+1)], '', 1)
                    #tmp_dir = tmp_dir.replace('/','',1)
                    if not createdir(os.path.join(self.baseline_root, tmp_dir)):#目标目录中创建目录树
                        return False
                    shutil.move(os.path.join(self.tmp_src_path, fn),os.path.join(self.baseline_root, fn.replace(zipfilename[:-(4+file_uuid_len+1)] + '/', '', -1)))
                    # if code_flag == 0:
                    #     shutil.move(os.path.join(self.tmp_src_path,fn), os.path.join(self.baseline_root, fn.encode('cp437').decode('gbk').replace(zipfilename[:-(4+file_uuid_len+1)]+'/','',-1)))
                    # elif code_flag == 1:
                    #     shutil.move(os.path.join(self.tmp_src_path, fn), os.path.join(self.baseline_root,fn.encode('cp437').decode('utf-8').replace(zipfilename[:-(4+file_uuid_len+1)] + '/', '',-1)))
                    # else:
                    #     shutil.move(os.path.join(self.tmp_src_path, fn), os.path.join(self.baseline_root,fn.replace(zipfilename[:-(4+file_uuid_len+1)] + '/', '',-1)))

                elif os.path.isdir(os.path.join(self.tmp_src_path, fn)):#提取出来的是路径
                    tmp_dir = os.path.dirname(fn).replace(zipfilename[:-(4+file_uuid_len+1)], '', 1)
                    # if code_flag == 0:
                    #     tmp_dir = os.path.dirname(fn.encode('cp437').decode('gbk')).replace(zipfilename[:-(4+file_uuid_len+1)],'',1)
                    # elif code_flag == 1:
                    #     tmp_dir = os.path.dirname(fn.encode('cp437').decode('utf-8')).replace(zipfilename[:-(4+file_uuid_len+1)], '', 1)
                    # else:
                    #     tmp_dir = os.path.dirname(fn).replace(zipfilename[:-(4+file_uuid_len+1)], '', 1)

                    if not createdir(os.path.join(self.baseline_root,tmp_dir)):
                        return False
                else: #提取出来的不是文件页不是路径，报错
                    logger.error('[%s]不是文件也不是目录'%(fn))
            myzip.close()
        except Exception as e: #提取过程中由任何异常，报错
            logger.error('报错信息:' + repr(e) + ',报错的行号:' + str(e.__traceback__.tb_lineno))
            return False

        if not rmtreedir(self.tmp_src_path): #删除临时目录树
            return False
        #输出没有找到目录或文件
        tmp_extract_list = set(self.extract_AutoTest_list).difference(set(tmp_extract_list))

        for x in tmp_extract_list:
            logger.warning("[%s]文件中没有找到[%s]"%(zipfilename,x))
        # 删除临时基线包文件
        if os.path.exists(autotest_zip_path_tmp):
            try:
                os.remove(autotest_zip_path_tmp)
            except:
                return False
        else:
            return False

        return True


