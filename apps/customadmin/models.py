
from django.db import models



class RunningProcessInfo(models.Model):
    batch_id = models.CharField(verbose_name='批次id', max_length=128)
    data_id = models.CharField(verbose_name='数据批次id', max_length=128, null=True)
    url_all = models.TextField(verbose_name='baseline_url', null=True)
    param_all = models.TextField(verbose_name='baseline_参数', null=True)
    identify = models.CharField(verbose_name='标识-baseline/exp', max_length=64, null=True)

    class Meta:
        db_table = 'running_process_data_table'
        verbose_name = verbose_name_plural = '执行过程记录表'

class SystemContent(models.Model):
    '''
    系统结构表
    '''
    system_name =  models.CharField(verbose_name='系统名称', max_length=128, null=True)
    leve_1_name =  models.CharField(verbose_name='一级目录', max_length=128, null=True)
    leve_2_name =  models.CharField(verbose_name='二级目录', max_length=128, null=True)
    leve_3_name =  models.CharField(verbose_name='三级目录', max_length=128, null=True)
    leve_4_name =  models.CharField(verbose_name='四级目录', max_length=128, null=True)
    importance_level =  models.CharField(verbose_name='重要级别', max_length=128, null=True)
    function_name =  models.CharField(verbose_name='功能名称', max_length=128)
    function_code =  models.CharField(verbose_name='功能编号', max_length=128, null=True)
    update_time = models.DateTimeField('更新时间', null=True)
    class Meta:
        db_table = 'system_content_table'
        verbose_name = verbose_name_plural = '系统结构表'

class FileType(models.Model):
    '''
    文件类型表
    '''
    filetype = models.CharField(verbose_name='文件类型', max_length=128, null=True)
    update_time = models.DateTimeField('更新时间', null=True)
    class Meta:
        db_table = 'file_type_table'
        verbose_name = verbose_name_plural = '文件类型表'
