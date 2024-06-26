# -*- coding: utf-8 -*-            
# @Author : libeijie
# @Time : 2024/6/8 7:35

import json
import os
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse,FileResponse,HttpResponse
from django.utils.encoding import escape_uri_path
from django.shortcuts import render
from django.http import HttpResponseServerError
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core import serializers

from testcases.models import ManageToolDataFileModel
from customadmin.models import SystemContent,FileType


@login_required
def managetool_data_file_page_view(request):
    '''
    跳转至数据文件页
    :param request:
    :return:
    '''
    response = render(request, template_name='managetool/managetool_data_file6_2.html', context={})
    return response

@csrf_exempt
def managetool_data_file_get_data_view(request):
    '''
    获取数据文件表的数据
    :param request:
    :return:
    '''
    # 获取分页参数
    limit = int(request.GET.get('limit', 10))
    offset = int(request.GET.get('offset', 0))
    #ManageToolDataFileModel
    #data_files = ManageToolDataFileModel.objects.select_related('system_conten_id').all()[offset:offset + limit]  AB表有外键关联关系
    # 查询数据文件表
    data_files = ManageToolDataFileModel.objects.all()[offset:offset + limit]

    # 获取所有相关的系统结构数据
    system_ids = [data_file.system_conten_id for data_file in data_files]
    systems = {system.id: system for system in SystemContent.objects.filter(id__in=system_ids)}

    #获取所有相关的文件类型数据
    file_type_ids = [data_file.file_type_id for data_file in data_files]
    file_types = {file_type.id: file_type for file_type in FileType.objects.filter(id__in=file_type_ids)}

    resp_container = []
    for file in data_files:
        system = systems.get(file.system_conten_id)
        file_type = file_types.get(file.file_type_id)
        file_name = os.path.basename(file.file_path)  # 获取文件名部分
        resp_container.append({
            'file_id': file.id,
            'file_type': file_type.filetype if file_type is not None else '',
            'file_path': file.file_path,
            'file_name': file_name,
            'file_update_time': file.update_time,
            'system_id': system.id if system else None,
            'system_name': system.system_name if system else '',
            'leve_1_name': system.leve_1_name if system else '',
            'leve_2_name': system.leve_2_name if system else '',
            'leve_3_name': system.leve_3_name if system else '',
            'leve_4_name': system.leve_4_name if system else '',
            'importance_level': system.importance_level if system else '',
            'function_name': system.function_name if system else '',
            'function_code': system.function_code if system else '',
        })
    return JsonResponse({
        'total': ManageToolDataFileModel.objects.count(),
        'rows': resp_container
    })



@csrf_exempt
def managetool_data_file_get_data_view1(request):
    '''
    获取数据文件表的数据
    :param request:
    :return:
    '''
    # 获取分页参数
    page = int(request.query_params.get('page', 1))
    limit = int(request.query_params.get('page_size', 10))
    offset = (page - 1) * limit

    #limit = int(request.GET.get('limit', 10))
    #offset = int(request.GET.get('offset', 0))
    #ManageToolDataFileModel
    #data_files = ManageToolDataFileModel.objects.select_related('system_conten_id').all()[offset:offset + limit]  AB表有外键关联关系
    # 查询数据文件表
    data_files = ManageToolDataFileModel.objects.all()[offset:offset + limit]

    # 获取所有相关的系统结构数据
    system_ids = [data_file.system_conten_id for data_file in data_files]
    systems = {system.id: system for system in SystemContent.objects.filter(id__in=system_ids)}

    #获取所有相关的文件类型数据
    file_type_ids = [data_file.file_type_id for data_file in data_files]
    file_types = {file_type.id: file_type for file_type in FileType.objects.filter(id__in=file_type_ids)}

    resp_container = []
    for file in data_files:
        system = systems.get(file.system_conten_id)
        file_type = file_types.get(file.file_type_id)
        file_name = os.path.basename(file.file_path)  # 获取文件名部分
        resp_container.append({
            'file_id': file.id,
            'file_type': file_type.filetype if file_type is not None else '',
            'file_path': file.file_path,
            'file_name': file_name,
            'file_update_time': file.update_time,
            'system_id': system.id if system else None,
            'system_name': system.system_name if system else '',
            'leve_1_name': system.leve_1_name if system else '',
            'leve_2_name': system.leve_2_name if system else '',
            'leve_3_name': system.leve_3_name if system else '',
            'leve_4_name': system.leve_4_name if system else '',
            'importance_level': system.importance_level if system else '',
            'function_name': system.function_name if system else '',
            'function_code': system.function_code if system else '',
        })
    return JsonResponse({
        'total': ManageToolDataFileModel.objects.count(),
        'rows': resp_container
    })

@csrf_exempt
def managetool_data_file_getall_structure_filetype_view(request):
    '''
    获取系统目录结构 文件类型所有数据
    :param request:
    :return:
    '''

    system_structures = list(SystemContent.objects.values())
    file_types = list(FileType.objects.values())
    return JsonResponse({'system_structures': system_structures, 'file_types': file_types})

@csrf_exempt
def managetool_data_file_add_page_view(request):
    '''
    跳转到数据文件新增页
    :param request:
    :return:
    '''
    pagenum = request.GET.get('pagenum')
    pagesize = request.GET.get('pagesize')
    system_structures = list(SystemContent.objects.values())
    file_types = list(FileType.objects.values())
    response = render(request, template_name='managetool/managetool_data_file_add5.html', context={'system_structures': system_structures,
                                                                                              'file_types': file_types,
                                                                                              'pagenum':pagenum,
                                                                                              'pagesize':pagesize})
    return response

image_suffix = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
text_file_suffix = ('.txt', '.robot')
excel_suffix = ('.xls','.xlsx','xlsm')
from Salvation.settings import BASE_DIR,MEDIA_ROOT,MEDIA_URL
from common.cfg_helper import *
import base64
import mimetypes

@csrf_exempt
def managetool_data_file_preview_page_view(request):
    '''
    处理文件，跳到预览页面
    :param request:
    :return:
    '''
    file_path = request.GET.get('file_path')
    pagenum = request.GET.get('pagenum')
    pagesize = request.GET.get('pagesize')
    file_extension = os.path.splitext(file_path)[1].lower()
    cfg_file = ''.join([str(BASE_DIR), '/apps/data/config.cfg'])
    cfg_read = CfgHelper(cfg_file)
    try:
        if file_extension in image_suffix:
            # 图片文件处理方式
            file_contents = ''.join([str(MEDIA_URL), cfg_read.read_cfg_get_value_by_key('config_file','managetool_data_file'),file_path])
            return render(request, template_name='managetool/managetool_data_file_preview.html',
                      context={'file_content': file_contents,'file_extension':file_extension})
        elif file_extension == '.txt':
            # 文本文件处理方式
            print(''.join([str(BASE_DIR),str(MEDIA_URL), cfg_read.read_cfg_get_value_by_key('config_file','managetool_data_file'),file_path]))
            with open(''.join([str(BASE_DIR),str(MEDIA_URL), cfg_read.read_cfg_get_value_by_key('config_file','managetool_data_file'),file_path]), "r", encoding="utf-8") as file:
                # 读取文件内容
                file_contents = file.read()

            return render(request, template_name='managetool/managetool_data_file_preview.html',
                          context={'file_content': file_contents,'file_extension':file_extension})
        elif file_extension in ['.xls', '.xlsx']:
            # Excel 文件处理方式
            # 实现 Excel 文件的预览逻辑
            ...
            with open(''.join([str(BASE_DIR),str(MEDIA_URL), cfg_read.read_cfg_get_value_by_key('config_file','managetool_data_file'),file_path]), 'rb') as file:
                file_content = base64.b64encode(file.read()).decode('utf-8')
            return render(request, template_name='managetool/managetool_data_file_preview2.html',
                          context={'file_content': file_content, 'file_extension': file_extension})
        elif file_extension == '.zip':
            # ZIP 文件处理方式
            # 解压 ZIP 文件并获取要预览的文件内容
            ...
            #return render(request, 'preview_zip.html', {'file_content': file_content})
            pass
        else:
            return HttpResponse('Unsupported file type.', status=400)
    except Exception as e:
        return HttpResponse(f'Error: {e}', status=500)

@csrf_exempt
def get_data(request):
    limit = int(request.GET.get('page', 10))
    offset = int(request.GET.get('page_size', 0))
    startrow = int(request.GET.get('startRow', 10))
    endRow = int(request.GET.get('endRow', 10))
    leve_1_name = request.GET.get('leve_1_name','')
    print(leve_1_name)

    data = list(SystemContent.objects.values(
        'system_name',
        'leve_1_name',
        'leve_2_name',
        'leve_3_name',
        'leve_4_name',
        'function_name',
        'function_code',
        'importance_level'
    ))
    data = [
        {"system_name": '数据查询统计系统数据查询统计系统数据查询统计系统数据查询统计系统数据查询统计系统数据查询统计系统', "leve_1_name": '结算业务', "leve_2_name": '/',
         "leve_3_name": '/', "leve_4_name": '/', "function_name": 'a股份备付金', "function_code": 'za0001',
         "importance_level": '一般类—业务查询'},
        {"system_name": '数据查询统计系统', "leve_1_name": '结算业务', "leve_2_name": '港股通', "leve_3_name": '港股备份',
         "leve_4_name": '', "function_name": '支付金预付', "function_code": 'za0021', "importance_level": '一般类—业务类'},
        {"system_name": '数据查询统计系统', "leve_1_name": '结算业务', "leve_2_name": '港股通', "leve_3_name": '', "leve_4_name": '',
         "function_name": '银行预付', "function_code": 'Jx0021', "importance_level": ''},
        {"system_name": '数据查询统计系统', "leve_1_name": '支付业务', "leve_2_name": '', "leve_3_name": '', "leve_4_name": '',
         "function_name": '三级账户支付', "function_code": 'uu0001', "importance_level": ''},
        {"system_name": '风险监测系统', "leve_1_name": '等支付金', "leve_2_name": '等预算支付', "leve_3_name": '', "leve_4_name": '',
         "function_name": '二类账户', "function_code": 'hj0021', "importance_level": '重要类—业务类'},
        {"system_name": '风险监测系统', "leve_1_name": '', "leve_2_name": '', "leve_3_name": '', "leve_4_name": '',
         "function_name": '京杭账户', "function_code": 'hj0028', "importance_level": '重要类—业务类'},
        {"system_name": '风险监测系统', "leve_1_name": '', "leve_2_name": '', "leve_3_name": '', "leve_4_name": '',
         "function_name": '京杭账户等级支付', "function_code": 'hj0029', "importance_level": ''},
        {"system_name": '风险监测系统', "leve_1_name": '结算业务', "leve_2_name": '', "leve_3_name": '', "leve_4_name": '',
         "function_name": 'a股份备付金', "function_code": 'za0001', "importance_level": '一般类—业务查询'},
        {'system_name': '数据查询统计系统', 'leve_1_name': '结算业务', 'leve_2_name': '/', 'leve_3_name': '/', 'leve_4_name': '/',
         'function_name': 'a股份备付金', 'function_code': 'za0001', 'importance_level': '一般类—业务查询'},
        {'system_name': '数据查询统计系统', 'leve_1_name': '结算业务', 'leve_2_name': '港股通', 'leve_3_name': '港股备份',
         'leve_4_name': '', 'function_name': '支付金预付', 'function_code': 'za0021', 'importance_level': '一般类—业务类'},
        {'system_name': '风控系统', 'leve_1_name': '结算业务1', 'leve_2_name': '港股通2', 'leve_3_name': '港股备份',
         'leve_4_name': '四级目录', 'function_name': '支付金预付余额', 'function_code': 'za0022', 'importance_level': '重要类—业务类'},
        {"system_name": '风险监测系统', "leve_1_name": '', "leve_2_name": '', "leve_3_name": '', "leve_4_name": '',
         "function_name": '京杭账户等级支付', "function_code": 'hj0029', "importance_level": ''},
        {"system_name": '风险监测系统', "leve_1_name": '结算业务', "leve_2_name": '', "leve_3_name": '', "leve_4_name": '',
         "function_name": 'a股份备付金', "function_code": 'za0001', "importance_level": '一般类—业务查询'},
        {'system_name': '数据查询统计系统', 'leve_1_name': '结算业务', 'leve_2_name': '/', 'leve_3_name': '/', 'leve_4_name': '/',
         'function_name': 'a股份备付金', 'function_code': 'za0001', 'importance_level': '一般类—业务查询'},
        {'system_name': '数据查询统计系统', 'leve_1_name': '结算业务', 'leve_2_name': '港股通', 'leve_3_name': '港股备份',
         'leve_4_name': '', 'function_name': '支付金预付', 'function_code': 'za0021', 'importance_level': '一般类—业务类'},
        {'system_name': '风控系统', 'leve_1_name': '结算业务1', 'leve_2_name': '港股通2', 'leve_3_name': '港股备份',
         'leve_4_name': '四级目录', 'function_name': '支付金预付余额', 'function_code': 'za0022', 'importance_level': '重要类—业务类'},
        {"system_name": '风险监测系统', "leve_1_name": '', "leve_2_name": '', "leve_3_name": '', "leve_4_name": '',
         "function_name": '京杭账户等级支付', "function_code": 'hj0029', "importance_level": ''},
        {"system_name": '风险监测系统', "leve_1_name": '结算业务', "leve_2_name": '', "leve_3_name": '', "leve_4_name": '',
         "function_name": 'a股份备付金', "function_code": 'za0001', "importance_level": '一般类—业务查询'},
        {'system_name': '数据查询统计系统', 'leve_1_name': '结算业务', 'leve_2_name': '/', 'leve_3_name': '/', 'leve_4_name': '/',
         'function_name': 'a股份备付金', 'function_code': 'za0001', 'importance_level': '一般类—业务查询'},
        {'system_name': '数据查询统计系统', 'leve_1_name': '结算业务', 'leve_2_name': '港股通', 'leve_3_name': '港股备份',
         'leve_4_name': '', 'function_name': '支付金预付', 'function_code': 'za0021', 'importance_level': '一般类—业务类'},
        {'system_name': '风控系统', 'leve_1_name': '结算业务1', 'leve_2_name': '港股通2', 'leve_3_name': '港股备份',
         'leve_4_name': '四级目录', 'function_name': '支付金预付余额', 'function_code': 'za0022', 'importance_level': '重要类—业务类'},
        {"system_name": '风险监测系统', "leve_1_name": '', "leve_2_name": '', "leve_3_name": '', "leve_4_name": '',
         "function_name": '京杭账户等级支付', "function_code": 'hj0029', "importance_level": ''},
        {"system_name": '风险监测系统', "leve_1_name": '结算业务', "leve_2_name": '', "leve_3_name": '', "leve_4_name": '',
         "function_name": 'a股份备付金', "function_code": 'za0001', "importance_level": '一般类—业务查询'},
        {'system_name': '数据查询统计系统', 'leve_1_name': '结算业务', 'leve_2_name': '/', 'leve_3_name': '/', 'leve_4_name': '/',
         'function_name': 'a股份备付金', 'function_code': 'za0001', 'importance_level': '一般类—业务查询'},
        {'system_name': '数据查询统计系统', 'leve_1_name': '结算业务', 'leve_2_name': '港股通', 'leve_3_name': '港股备份',
         'leve_4_name': '', 'function_name': '支付金预付', 'function_code': 'za0021', 'importance_level': '一般类—业务类'},
        {'system_name': '风控系统', 'leve_1_name': '结算业务1', 'leve_2_name': '港股通2', 'leve_3_name': '港股备份',
         'leve_4_name': '四级目录', 'function_name': '支付金预付余额', 'function_code': 'za0022', 'importance_level': '重要类—业务类'},
        {"system_name": '风险监测系统', "leve_1_name": '', "leve_2_name": '', "leve_3_name": '', "leve_4_name": '',
         "function_name": '京杭账户等级支付', "function_code": 'hj0029', "importance_level": ''},
        {"system_name": '风险监测系统', "leve_1_name": '结算业务', "leve_2_name": '', "leve_3_name": '', "leve_4_name": '',
         "function_name": 'a股份备付金', "function_code": 'za0001', "importance_level": '一般类—业务查询'},
        {'system_name': '数据查询统计系统', 'leve_1_name': '结算业务', 'leve_2_name': '/', 'leve_3_name': '/', 'leve_4_name': '/',
         'function_name': 'a股份备付金', 'function_code': 'za0001', 'importance_level': '一般类—业务查询'},
        {'system_name': '数据查询统计系统', 'leve_1_name': '结算业务', 'leve_2_name': '港股通', 'leve_3_name': '港股备份',
         'leve_4_name': '', 'function_name': '支付金预付', 'function_code': 'za0021', 'importance_level': '一般类—业务类'},
        {'system_name': '风控系统', 'leve_1_name': '结算业务1', 'leve_2_name': '港股通2', 'leve_3_name': '港股备份',
         'leve_4_name': '四级目录', 'function_name': '支付金预付余额', 'function_code': 'za0022', 'importance_level': '重要类—业务类'},
        {"system_name": '风险监测系统', "leve_1_name": '', "leve_2_name": '', "leve_3_name": '', "leve_4_name": '',
         "function_name": '京杭账户等级支付', "function_code": 'hj0029', "importance_level": ''},
        {"system_name": '风险监测系统', "leve_1_name": '结算业务', "leve_2_name": '', "leve_3_name": '', "leve_4_name": '',
         "function_name": 'a股份备付金', "function_code": 'za0001', "importance_level": '一般类—业务查询'},
        {'system_name': '数据查询统计系统', 'leve_1_name': '结算业务', 'leve_2_name': '/', 'leve_3_name': '/', 'leve_4_name': '/',
         'function_name': 'a股份备付金', 'function_code': 'za0001', 'importance_level': '一般类—业务查询'},
        {'system_name': '数据查询统计系统', 'leve_1_name': '结算业务', 'leve_2_name': '港股通', 'leve_3_name': '港股备份',
         'leve_4_name': '', 'function_name': '支付金预付', 'function_code': 'za0021', 'importance_level': '一般类—业务类'},
        {'system_name': '风控系统', 'leve_1_name': '结算业务1', 'leve_2_name': '港股通2', 'leve_3_name': '港股备份',
         'leve_4_name': '四级目录', 'function_name': '支付金预付余额', 'function_code': 'za0022', 'importance_level': '重要类—业务类'},
        {"system_name": '风险监测系统', "leve_1_name": '', "leve_2_name": '', "leve_3_name": '', "leve_4_name": '',
         "function_name": '京杭账户等级支付', "function_code": 'hj0029', "importance_level": ''},
        {"system_name": '风险监测系统', "leve_1_name": '结算业务', "leve_2_name": '', "leve_3_name": '', "leve_4_name": '',
         "function_name": 'a股份备付金', "function_code": 'za0001', "importance_level": '一般类—业务查询'},
        {'system_name': '数据查询统计系统', 'leve_1_name': '结算业务', 'leve_2_name': '/', 'leve_3_name': '/', 'leve_4_name': '/',
         'function_name': 'a股份备付金', 'function_code': 'za0001', 'importance_level': '一般类—业务查询'},
        {'system_name': '数据查询统计系统', 'leve_1_name': '结算业务', 'leve_2_name': '港股通', 'leve_3_name': '港股备份',
         'leve_4_name': '', 'function_name': '支付金预付', 'function_code': 'za0021', 'importance_level': '一般类—业务类'},
        {'system_name': '风控系统', 'leve_1_name': '结算业务1', 'leve_2_name': '港股通2', 'leve_3_name': '港股备份',
         'leve_4_name': '四级目录', 'function_name': '支付金预付余额', 'function_code': 'za0022', 'importance_level': '重要类—业务类'},
        {"system_name": '风险监测系统', "leve_1_name": '', "leve_2_name": '', "leve_3_name": '', "leve_4_name": '',
         "function_name": '京杭账户等级支付', "function_code": 'hj0029', "importance_level": ''},
        {"system_name": '风险监测系统', "leve_1_name": '结算业务', "leve_2_name": '', "leve_3_name": '', "leve_4_name": '',
         "function_name": 'a股份备付金', "function_code": 'za0001', "importance_level": '一般类—业务查询'},
        {'system_name': '数据查询统计系统', 'leve_1_name': '结算业务', 'leve_2_name': '/', 'leve_3_name': '/', 'leve_4_name': '/',
         'function_name': 'a股份备付金', 'function_code': 'za0001', 'importance_level': '一般类—业务查询'},
        {'system_name': '数据查询统计系统', 'leve_1_name': '结算业务', 'leve_2_name': '港股通', 'leve_3_name': '港股备份',
         'leve_4_name': '', 'function_name': '支付金预付', 'function_code': 'za0021', 'importance_level': '一般类—业务类'},
        {'system_name': '风控系统', 'leve_1_name': '结算业务1', 'leve_2_name': '港股通2', 'leve_3_name': '港股备份',
         'leve_4_name': '四级目录', 'function_name': '支付金预付余额', 'function_code': 'za0022', 'importance_level': '重要类—业务类'},
        {"system_name": '风险监测系统', "leve_1_name": '', "leve_2_name": '', "leve_3_name": '', "leve_4_name": '',
         "function_name": '京杭账户等级支付', "function_code": 'hj0029', "importance_level": ''},
        {"system_name": '风险监测系统', "leve_1_name": '结算业务', "leve_2_name": '', "leve_3_name": '', "leve_4_name": '',
         "function_name": 'a股份备付金', "function_code": 'za0001', "importance_level": '一般类—业务查询'},
        {'system_name': '数据查询统计系统', 'leve_1_name': '结算业务', 'leve_2_name': '/', 'leve_3_name': '/', 'leve_4_name': '/',
         'function_name': 'a股份备付金', 'function_code': 'za0001', 'importance_level': '一般类—业务查询'},
        {'system_name': '数据查询统计系统', 'leve_1_name': '结算业务', 'leve_2_name': '港股通', 'leve_3_name': '港股备份',
         'leve_4_name': '', 'function_name': '支付金预付', 'function_code': 'za0021', 'importance_level': '一般类—业务类'},
        {'system_name': '风控系统', 'leve_1_name': '结算业务1', 'leve_2_name': '港股通2', 'leve_3_name': '港股备份',
         'leve_4_name': '四级目录', 'function_name': '支付金预付余额', 'function_code': 'za0022', 'importance_level': '重要类—业务类'},
        {"system_name": '风险监测系统', "leve_1_name": '', "leve_2_name": '', "leve_3_name": '', "leve_4_name": '',
         "function_name": '京杭账户等级支付', "function_code": 'hj0029', "importance_level": ''},
        {"system_name": '风险监测系统', "leve_1_name": '结算业务', "leve_2_name": '', "leve_3_name": '', "leve_4_name": '',
         "function_name": 'a股份备付金', "function_code": 'za0001', "importance_level": '一般类—业务查询'},
        {'system_name': '数据查询统计系统', 'leve_1_name': '结算业务', 'leve_2_name': '/', 'leve_3_name': '/', 'leve_4_name': '/',
         'function_name': 'a股份备付金', 'function_code': 'za0001', 'importance_level': '一般类—业务查询'},
        {'system_name': '数据查询统计系统', 'leve_1_name': '结算业务', 'leve_2_name': '港股通', 'leve_3_name': '港股备份',
         'leve_4_name': '', 'function_name': '支付金预付', 'function_code': 'za0021', 'importance_level': '一般类—业务类'},
        {'system_name': '风控系统', 'leve_1_name': '结算业务1', 'leve_2_name': '港股通2', 'leve_3_name': '港股备份',
         'leve_4_name': '四级目录', 'function_name': '支付金预付余额', 'function_code': 'za0022', 'importance_level': '重要类—业务类'},
        {"system_name": '风险监测系统', "leve_1_name": '', "leve_2_name": '', "leve_3_name": '', "leve_4_name": '',
         "function_name": '京杭账户等级支付', "function_code": 'hj0029', "importance_level": ''},
        {"system_name": '风险监测系统', "leve_1_name": '结算业务', "leve_2_name": '', "leve_3_name": '', "leve_4_name": '',
         "function_name": 'a股份备付金', "function_code": 'za0001', "importance_level": '一般类—业务查询'},
        {'system_name': '数据查询统计系统', 'leve_1_name': '结算业务', 'leve_2_name': '/', 'leve_3_name': '/', 'leve_4_name': '/',
         'function_name': 'a股份备付金', 'function_code': 'za0001', 'importance_level': '一般类—业务查询'},
        {'system_name': '数据查询统计系统', 'leve_1_name': '结算业务', 'leve_2_name': '港股通', 'leve_3_name': '港股备份',
         'leve_4_name': '', 'function_name': '支付金预付', 'function_code': 'za0021', 'importance_level': '一般类—业务类'},
        {'system_name': '风控系统', 'leve_1_name': '结算业务1', 'leve_2_name': '港股通2', 'leve_3_name': '港股备份',
         'leve_4_name': '四级目录', 'function_name': '支付金预付余额', 'function_code': 'za0022', 'importance_level': '重要类—业务类'},
        {"system_name": '风险监测系统', "leve_1_name": '', "leve_2_name": '', "leve_3_name": '', "leve_4_name": '',
         "function_name": '京杭账户等级支付', "function_code": 'hj0029', "importance_level": ''},
        {"system_name": '风险监测系统', "leve_1_name": '结算业务', "leve_2_name": '', "leve_3_name": '', "leve_4_name": '',
         "function_name": 'a股份备付金', "function_code": 'za0001', "importance_level": '一般类—业务查询'},
        {'system_name': '数据查询统计系统', 'leve_1_name': '结算业务', 'leve_2_name': '/', 'leve_3_name': '/', 'leve_4_name': '/',
         'function_name': 'a股份备付金', 'function_code': 'za0001', 'importance_level': '一般类—业务查询'},
        {'system_name': '数据查询统计系统', 'leve_1_name': '结算业务', 'leve_2_name': '港股通', 'leve_3_name': '港股备份',
         'leve_4_name': '', 'function_name': '支付金预付', 'function_code': 'za0021', 'importance_level': '一般类—业务类'},
        {'system_name': '风控系统', 'leve_1_name': '结算业务1', 'leve_2_name': '港股通2', 'leve_3_name': '港股备份',
         'leve_4_name': '四级目录', 'function_name': '支付金预付余额', 'function_code': 'za0022', 'importance_level': '重要类—业务类'},
        {"system_name": '风险监测系统', "leve_1_name": '', "leve_2_name": '', "leve_3_name": '', "leve_4_name": '',
         "function_name": '京杭账户等级支付', "function_code": 'hj0029', "importance_level": ''},
        {"system_name": '风险监测系统', "leve_1_name": '结算业务', "leve_2_name": '', "leve_3_name": '', "leve_4_name": '',
         "function_name": 'a股份备付金', "function_code": 'za0001', "importance_level": '一般类—业务查询'},
        {'system_name': '数据查询统计系统', 'leve_1_name': '结算业务', 'leve_2_name': '/', 'leve_3_name': '/', 'leve_4_name': '/',
         'function_name': 'a股份备付金', 'function_code': 'za0001', 'importance_level': '一般类—业务查询'},
        {'system_name': '数据查询统计系统', 'leve_1_name': '结算业务', 'leve_2_name': '港股通', 'leve_3_name': '港股备份',
         'leve_4_name': '', 'function_name': '支付金预付', 'function_code': 'za0021', 'importance_level': '一般类—业务类'},
        {'system_name': '风控系统', 'leve_1_name': '结算业务1', 'leve_2_name': '港股通2', 'leve_3_name': '港股备份',
         'leve_4_name': '四级目录', 'function_name': '支付金预付余额', 'function_code': 'za0022', 'importance_level': '重要类—业务类'},
    ]
    # a = (offset - 1) * limit
    # data =data[a:a + limit]
    if leve_1_name:
        data = [item for item in data if item['leve_1_name'] == leve_1_name]

    data_new = data[startrow:endRow]
    total_num = data.__len__()
    #total_num = 71
    print(data_new)
    return JsonResponse({'rows': data_new, 'totalCount': total_num}, safe=False)


