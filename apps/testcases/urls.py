from django.urls import path

from testcases.views import config_views,operation_views,script_views,test_query_views,managetool_data_file_views

app_name = 'testcases'
urlpatterns=[
    path('testcase_config/',config_views.config_list_view,name='testcase_config'),
    path('config_data/',config_views.get_all_config_file,name='config_data'),
    path('config_upload/',config_views.config_upload,name='config_upload'),
    path('config_delete_file/',config_views.config_delete_file,name='config_delete_file'),
    path('download_config_template_file/',config_views.download_config_template_file,name='download_config_template_file'),
    path('testcase_template/',config_views.template,name='testcase_template'),
    path('template_delete_file/',config_views.template_delete_file,name='template_delete_file'),
    path('related/',config_views.related,name='related'),
    #操作
    path('reuseCommonTestCases/',operation_views.reuseCommonTestCases,name='reuseCommonTestCases'),
    path('generateScript/',operation_views.generateScript,name='generateScript'),
    path('runEnvFree/',operation_views.runEnvFreeView,name='runEnvFree'),
    path('uploadAutoScriptToShow/',operation_views.uploadAutoScriptToShow,name='uploadAutoScriptToShow'),
    path('lastst_script_to_show/',operation_views.lastst_script_to_show,name='lastst_script_to_show'),
    path('run_script/', operation_views.run_script_view, name='run_script'),
    path('change_name/', operation_views.change_name, name='change_name'),
    path('delete_folder_file/', operation_views.delete_folder_file, name='delete_folder_file'),
    path('update_auto_script_file_content/', operation_views.update_auto_script_file_content, name='update_auto_script_file_content'),
    path('run_testcases/', operation_views.run_testcases, name='run_testcases'),
    path('download_script_ran_folder/', operation_views.download_script_ran_folder, name='download_script_ran_folder'),
    path('get_failed_passed_case/', operation_views.get_failed_passed_case, name='get_failed_passed_case'),

    #脚本测试套件
    path('script_config/',script_views.script_config,name='script_config'),
    path('get_script_list/',script_views.get_script_list,name='get_script_list'),
    path('get_script_file_content/',script_views.get_script_file_content,name='get_script_file_content'),
    path('update_script_file_content/',script_views.update_script_file_content,name='update_script_file_content'),
    path('upload_script_component/',script_views.upload_script_component,name='upload_script_component'),
    path('upload_script_file_component/',script_views.upload_script_file_component,name='upload_script_file_component'),
    path('download_script_folder/',script_views.download_script_folder,name='download_script_folder'),
    path('delete_script_folder/',script_views.delete_script_folder,name='delete_script_folder'),
    #脚本基线包
    path('script_baseline/',script_views.script_baseline,name='script_baseline'),
    path('upload_script_baseline_component/',script_views.upload_script_baseline_component,name='upload_script_baseline_component'),
    path('get_script_baseline_name/', script_views.get_script_baseline_name, name='get_script_baseline_name'),

    #测试查询
    path('test_query/', test_query_views.test_query, name='test_query'),

    path('managetool_data_file_page/', managetool_data_file_views.managetool_data_file_page_view, name='managetool_data_file_page'),
    path('managetool_data_file_get_data/', managetool_data_file_views.managetool_data_file_get_data_view, name='managetool_data_file_get_data'),
    #path('managetool_data_file_get_data/', managetool_data_file_views.managetool_data_file_get_data_view1, name='managetool_data_file_get_data'),
    path('managetool_data_file_getall_structure_filetype/', managetool_data_file_views.managetool_data_file_getall_structure_filetype_view, name='managetool_data_file_getall_structure_filetype'),
    path('managetool_data_file_add_page/', managetool_data_file_views.managetool_data_file_add_page_view, name='managetool_data_file_add_page'),
    path('managetool_data_file_preview_page/', managetool_data_file_views.managetool_data_file_preview_page_view, name='managetool_data_file_preview_page'),
    path('get_data/', managetool_data_file_views.get_data, name='get_data'),
]