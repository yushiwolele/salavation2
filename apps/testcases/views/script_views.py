# -*- coding: utf-8 -*-            
# @Author : libeijie
# @Time : 2023/9/19 15:29

import json
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse,HttpResponse,FileResponse
from django.utils.encoding import escape_uri_path
from django.contrib.auth.decorators import login_required

from testcases.service.script.script_service import *

@login_required
def script_config(request):
    '''
    脚本测试套件列表页
    :param request:
    :return:
    '''
    response =render(request, template_name='testcases/script_config.html', context={})
    return response

def get_script_list(request):
    '''
    获取db配置文件数据并跳转至配置文件列表页
    :param request:
    :return:
    '''
    #获取数据
    tags = request.GET.get('tags','0') #0-脚本套件；1-基线包
    scrser = ScriptService()
    if tags == '0':
        scirpt_component_list = scrser.get_all_script_component_path_data()
    else:
        scirpt_component_list = scrser.get_all_script_baseline_path_data()
    folders = scrser.build_folder_structure(scirpt_component_list)
    #转json
    folder_structure_dict = [scrser.folder_to_dict(folder) for folder in folders]
    result = {'code':200,'data':folder_structure_dict}
    return JsonResponse(result)

def get_script_file_content(request):
    '''
    获取脚本文件内容
    :param request:
    :return:
    '''
    #获取id
    script_path = request.GET.get('path',None)
    script_tags = request.GET.get('tags',0)
    scrser = ScriptService()
    data = scrser.get_script_content_by_path(script_path,int(script_tags))
    result = {'code': 200, 'data': data}
    return JsonResponse(result)

@csrf_exempt
def update_script_file_content(request):
    '''
    根据path更新文件内容，不涉及数据库
    :param request:
    :return:
    '''
    parameters = json.loads(request.body.decode('utf8'))
    file_path = parameters.get('path')
    file_content = parameters.get('content')
    scrser = ScriptService()
    result_msg = scrser.update_script_file_content_physically(file_path,file_content)
    result = {'code': 200, 'data': result_msg}
    return JsonResponse(result)

@csrf_exempt
def upload_script_component(request):
    '''
    上传脚本套件
    :param request:
    :return:
    '''
    upload_script_component_files = request.FILES.getlist('files[]', None)
    upload_script_component_file_paths = request.POST.getlist('file_paths[]', None)
    update_item_id = request.POST.get('update_item_id', '0') #如果是上传，则为0，如果是更新则为更新的数据id
    scrser = ScriptService()
    if update_item_id == '0': #上传
        result_msg = scrser.insert_script_component_folder(upload_script_component_files,upload_script_component_file_paths)
    else: #更新
        result_msg = scrser.update_script_component_folder(update_item_id,upload_script_component_files,upload_script_component_file_paths)
    result = {'code': 200, 'data': result_msg}
    return JsonResponse(result)

@csrf_exempt
def upload_script_file_component(request):
    '''
    上传脚本套件
    :param request:
    :return:
    '''
    upload_script_component_files = request.FILES.get('file', None)
    update_item_id = request.POST.get('update_item_id', '0') #如果是上传，则为0，如果是更新则为更新的数据id
    scrser = ScriptService()
    result_msg = scrser.update_script_component_file(update_item_id,upload_script_component_files)
    result = {'code': 200, 'data': result_msg}
    return JsonResponse(result)

def download_script_folder(request):
    '''
    下载文件（夹）
    :param request:
    :return:
    '''
    folder_id = request.GET.get('folder_id',None) #下载的文件（夹）id
    folder_tags = request.GET.get('tags',0) # 0-脚本套件；1-基线包
    folder,folder_name,flag = ScriptService().download_script_folder(folder_id,int(folder_tags))
    if flag: #文件
        if os.path.exists(folder):
            response = FileResponse(open(folder, 'rb'))
            response['Content-Type'] = 'application/octet-stream'  # 二进制文件
            response['Content-Disposition'] = 'attachment; filename={}'.format(escape_uri_path(folder_name))
    else: #文件夹打包成的zip
        # 构建HTTP响应，提供ZIP文件下载
        response = HttpResponse(folder.getvalue(), content_type="application/zip")
        response['Content-Disposition'] = 'attachment; filename={}.zip'.format(escape_uri_path(folder_name))
    return response

@csrf_exempt
def delete_script_folder(request):
    '''
    删除文件（夹）
    :param request:
    :return:
    '''
    parameters = json.loads(request.body.decode('utf8'))
    folder_id = parameters.get('folder_id') # 删除的文件（夹）id
    folder_tags = parameters.get('tags',0) # 删除的文件（夹）id
    result_msg = ScriptService().delete_script_folder(folder_id,int(folder_tags))
    result = {'code': 200, 'data': result_msg}
    return JsonResponse(result)

@login_required
def script_baseline(request):
    '''
    脚本基线包列表页
    :param request:
    :return:
    '''
    response =render(request, template_name='testcases/script_baseline.html', context={})
    return response

@csrf_exempt
def upload_script_baseline_component(request):
    '''
    上传脚本基线包
    :param request:
    :return:
    '''
    upload_script_baseline_component_files = request.FILES.get('zipFile', None)
    scrser = ScriptService()
    result_msg = scrser.upload_script_baseline_folder(upload_script_baseline_component_files)
    result = {'code': 200, 'data': result_msg}
    return JsonResponse(result)


def get_script_baseline_name(request):
    '''
    获取基线包名称
    :param request:
    :return:
    '''
    level = request.GET.get('level', None)
    tags = request.GET.get('tags', None)
    script_baseline_names_ids = get_script_baselines_service(level,tags)
    result = {'code': 200, 'data': script_baseline_names_ids}
    return JsonResponse(result)

