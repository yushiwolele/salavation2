# -*- coding: utf-8 -*-            
# @Author : libeijie
# @Time : 2023/9/12 14:00

import json
from pathlib import Path
from django.views.decorators.csrf import csrf_exempt
from django.utils.encoding import escape_uri_path
from django.http.response import HttpResponseServerError
from django.shortcuts import render
from django.http import JsonResponse,HttpResponse,StreamingHttpResponse

from testcases.service.operation.reuseCommonTestCases_service import *
from testcases.service.operation.generateAutoTestCases_service import *
from testcases.service.operation.runEnvFree_service import *
from testcases.service.operation.runTestCases_service import *


@csrf_exempt
def reuseCommonTestCases(request):
    '''
    生成测试用例
    :param request:
    :return:
    '''
    # 【备注】：期望二期做成异步
    # 获取配置好的用例excel

    file = request.FILES.get('file', None)
    file_name = file.name
    #生成用例
    result_data = ReuseCommonTestCases().create_project_test_cases(file)
    if result_data['code'] == 0:  # 生成成功
        workbook = result_data['data']
        #当前时间
        time_now = str(time.time()).replace('.','_')
        excel_file_path = 'temp_test_cases_{0}.xlsm'.format(time_now) #临时文件
        workbook.save(excel_file_path)
        with open(excel_file_path, 'rb') as processed_file:
            response = HttpResponse(processed_file.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = 'attachment;filename={}'.format(escape_uri_path(file_name))
        #删除临时文件
        if (os.path.exists(excel_file_path)):
            os.remove(excel_file_path)
        return response
    else: #生成失败
        return HttpResponseServerError('自定义报错！')

@csrf_exempt
def generateScript(request):
    '''
    自动生成自动化用例，并生成zip文件下载
    :param request:
    :return:
    '''
    testcase_file = request.FILES.get('file', None) #用例文件
    system = request.POST.get('system', None)  # 系统类型
    script_baseline_id = request.POST.get('script_baseline_id', None)  # 基线包id
    gat = GenerateAutolestCases()
    result_data = gat.generate_auto_test_cases(system,testcase_file,script_baseline_id)


    if result_data['code'] == 0: #生成成功
        zip_file = result_data['data']['file']
        zip_folder_name = result_data['data']['file_name']
        # 构建HTTP响应，提供ZIP文件下载
        response = HttpResponse(zip_file.getvalue(), content_type="application/zip")
        response['Content-Disposition'] = 'attachment; filename={}.zip'.format(escape_uri_path(zip_folder_name))
        return response
    else: #生成失败
        return HttpResponseServerError()


@csrf_exempt
def runEnvFreeView(request):
    '''
    打包自动化脚本为exe文件
    :param request:
    :return:
    '''
    script_component_files = request.FILES.getlist('files[]', None)
    script_component_file_paths = request.POST.getlist('file_paths[]', None)
    folder_name = request.POST.get('folder_name', None)
    result_data = RunEnvFreeService().get_folder_run_pyinstall(script_component_files,script_component_file_paths,folder_name)
    #打包成zip下载
    if result_data['code'] == 0:  # 生成成功
        zip_file = result_data['msg']
        # 构建HTTP响应，提供ZIP文件下载
        response = HttpResponse(zip_file.getvalue(), content_type="application/zip")
        response['Content-Disposition'] = 'attachment; filename={}.zip'.format(escape_uri_path('RunEnvFree'))
        return response
    else: #生成失败
        return HttpResponseServerError()

def run_script_view(request):
    request.session.pop('folders_json', None)
    rerunflag = request.GET.get('rerunflag', None)
    context = {'rerunflag': rerunflag}
    return render(request, template_name='testcases/run_script.html', context=context)


@csrf_exempt
def uploadAutoScriptToShow(request):
    '''
    接收前端上传的自动化脚本文件，存入临时文件，并展示在前端
    :param request:
    :return:
    '''
    if request.user.is_authenticated:
        # 获取当前登录用户的用户名
        user_id = request.user.id
        auto_script_files = request.FILES.getlist('files[]', None)
        auto_script_file_paths = request.POST.getlist('file_paths[]', None)
        folder_name = request.POST.get('folder_name', None)
        # 存入临时文件夹，并获取文件结构
        result_script = RunTestCasesService().handle_auto_script(auto_script_files, auto_script_file_paths, folder_name,user_id)
        if result_script['code'] == 1:
            result = {'code': 201, 'data': result_script['data']}
        else:
            # 转json
            folders_json = folder_to_dict(result_script['data'])
            folders_json = [folders_json]
            result = {'code': 200, 'data': folders_json}
        return JsonResponse(result)
    else:
        result = {'code': 201, 'data': '用户未登录'}
        return JsonResponse(result)

@csrf_exempt
def lastst_script_to_show(request):
    '''
    重新执行最新执行过的脚本
    :param request:
    :return:
    '''
    if request.user.is_authenticated:
        # 获取当前登录用户的用户名
        user_id = request.user.id
        # 存入临时文件夹，并获取文件结构
        result_script = RunTestCasesService().get_latest_ran_script(user_id)
        if result_script['code'] == 1:
            result = {'code': 201, 'data': result_script['data']}
        else:
            # 转json
            folders_json = folder_to_dict(result_script['data'])
            folders_json = [folders_json]
            result = {'code': 200, 'data': folders_json}
        return JsonResponse(result)
    else:
        result = {'code': 201, 'data': '用户未登录'}
        return JsonResponse(result)

@csrf_exempt
def change_name(request):
    '''
    更改robot及testcases名字
    :param request:
    :return:
    '''
    parameters = json.loads(request.body.decode('utf8'))
    item_path = parameters.get('itemPath') #文件绝对路径
    initial_name = parameters.get('initialName') #修改前名字
    edited_text = parameters.get('editedText') #修改后名字
    robo_case_flag = parameters.get('robotCaseFlag') #0-robot文件名；1-文件内部名字
    content_flag = parameters.get('contentFlag') #0-testcase;1-keywords;2-variables
    RunTestCasesService().change_name_service(item_path,initial_name,edited_text,str(robo_case_flag),str(content_flag))
    result = {'code': 200}
    return JsonResponse(result)

@csrf_exempt
def delete_folder_file(request):
    '''
    删除文件夹或者文件
    :param request:
    :return:
    '''
    parameters = json.loads(request.body.decode('utf8'))
    item_path = parameters.get('itemPath')  # 文件绝对路径
    folder_root = parameters.get('folder_root')  # 文件绝对路径
    result = RunTestCasesService().delete_folder_file_service(item_path,folder_root)
    if result['code'] ==0:
        root_folder = result['data']
        folders_json = folder_to_dict(root_folder)
        folders_json = [folders_json]
        result_json = {'code': 200, 'data': folders_json}
    else:
        result_json = result
    return JsonResponse(result_json)

@csrf_exempt
def update_auto_script_file_content(request):
    '''
    根据path更新文件内容，不涉及数据库
    :param request:
    :return:
    '''
    parameters = json.loads(request.body.decode('utf8'))
    file_path = parameters.get('path')
    file_content = parameters.get('content')
    result_msg = RunTestCasesService().update_script_file_content_physically(file_path,file_content)
    result = {'code': 200, 'data': result_msg}
    return JsonResponse(result)

@csrf_exempt
def run_testcases(request):
    '''
    运行testcases
    :param request:
    :return:
    '''
    user_id = request.user.id
    data = json.loads(request.body.decode('utf-8'))
    # 获取 checked_testcases 和 extraString
    checked_testcases = data.get('checked_testcases', '')
    checked_testcases = json.loads(checked_testcases)
    folder_root = data.get('folder_root', '')
    execution_environment = data.get('execution_environment', 'TEST')
    browser = data.get('browser', 'Chrome')
    #生成argfile.txt文件：1、去掉脚本中${env}获取方法，给${env}赋值；2、去掉自定义用户关键字下的testcases3、将选中的testcase按固定格式写入argfile.txt
    exe_run = RunTestCasesService().run_testcases_service(checked_testcases,folder_root,execution_environment,browser,user_id)
    # 返回 StreamingHttpResponse，告诉客户端使用长轮询
    return StreamingHttpResponse(exe_run, content_type="text/plain")

def download_script_ran_folder(request):
    '''
    下载运行完的脚本项目
    :param request:
    :return:
    '''
    # 要下载的文件夹路径
    folder_path = request.GET.get('folder_path',None) #下载的文件夹的路径
    result = RunTestCasesService().rewirte_execu_browser(folder_path)
    if result['code'] == 1: #报错
        response = HttpResponse(content_type="application/zip")
        response.status_code = 226
        response['msg'] = escape_uri_path(result['msg'])
        return response
    else:
        # 生成zip文件
        zip_buffer = compress_file_to_zip(folder_path)
        response = HttpResponse(zip_buffer.getvalue(), content_type="application/zip")
        response['Content-Disposition'] = 'attachment; filename={}.zip'.format(escape_uri_path(Path(folder_path).name))
        return response

def get_failed_passed_case(request):
    '''
    获取运行成功/失败的case
    :param request:
    :return:
    '''
    folder_path = request.GET.get('folder_path', None)  # 下载的文件夹的路径
    # 获取当前登录用户的用户名
    user_id = request.user.id

    result_json = RunTestCasesService().get_classification_result(folder_path,user_id)
    result = {'code': 200, 'data': result_json}
    return JsonResponse(result)
