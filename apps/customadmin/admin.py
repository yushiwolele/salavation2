from django.contrib import admin
from .models import RunningProcessInfo,SystemContent,FileType

#2
@admin.register(RunningProcessInfo)
class CustomAdminAdmin(admin.ModelAdmin):
    """
    用户展示类
    """
    #model = Users
    list_display = ['batch_id', 'data_id', 'url_all', 'param_all', 'identify']
    search_fields = ('batch_id','param_all')
    list_filter = ( 'data_id','url_all',)
    list_per_page = 20

@admin.register(SystemContent)
class SystemContentAdmin(admin.ModelAdmin):
    """
    系统结构配置表
    """

    list_display = ['system_name', 'leve_1_name', 'leve_2_name', 'leve_3_name', 'leve_4_name','importance_level','function_name','function_code']
    search_fields = ('system_name','leve_1_name','function_name')
    list_filter = ( 'system_name','leve_3_name',)
    list_editable = ['importance_level', 'leve_2_name']
    ordering = ('id',)
    list_per_page = 20

@admin.register(FileType)
class FileTypeAdmin(admin.ModelAdmin):
    """
    系统结构配置表
    """

    list_display = ['filetype', 'update_time']
    search_fields = ('filetype','update_time')
    list_filter = ( 'filetype','update_time')
    ordering = ('id',)
    list_per_page = 20


admin.site.site_header = '自动化测试平台后台1111'
admin.site.site_title = '自动化测试平台后台222'
admin.site.index_title = '自动化测试平台后台333'

