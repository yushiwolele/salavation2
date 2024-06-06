from django.db import models


class TestCaseConfigModel(models.Model):
    '''
    配置文件表
    '''
    config_file_name = models.CharField('配置文件名称',max_length=100,null=False)
    config_file_path = models.CharField('配置文件路径',max_length=1024,null=False)
    #1、文档验证&环境部署 WDBS 2、表定义 TABLE 3、视图定义 VIEW  4、宏定义 MACRO 5、函数定义 FUNCTION 6、存储过程定义 PROC  7、对外接口服务 JKFW 8、Automation任务 AUTO 9、统一监控 MON 10、前端功能页面 QDGN
    config_file_type = models.CharField('配置文件类型', max_length=100, null=True)
    batch_time = models.DateTimeField('修改时间',null=True)
    tags = models.CharField('文件标识',max_length=32,null=True) #0-配置文件；1-模板文件
    data_uuid = models.CharField('文件uuid', max_length=64, null=True)
    class Meta:
        db_table = 'testcase_configfile'

class ScriptConfig(models.Model):
    '''
    脚本测试用例表
    '''
    name = models.CharField('脚本测试套件名字', max_length=300, null=False)
    parent_id = models.IntegerField('父id', null=True)
    level = models.IntegerField('文件级别', default=0, null=True) #
    path = models.CharField('文件路径',max_length=1024,  null=True)
    tags = models.CharField('文件标识', max_length=32, null=True,default=0)  # 0-脚本测试套件；1-脚本基线包文件
    type = models.CharField('文件类型', max_length=32, null=True,default=0)  # 0-文件夹；1-文件
    class Meta:
        db_table = 'testcase_script_config'

class RanScriptResultModel(models.Model):
    '''
    测试结果表
    '''
    robot_path = models.TextField('脚本路径', null=True)
    test_name = models.CharField('用例名字', max_length=128, null=True)
    status = models.CharField('用例执行状态', max_length=32, null=True)
    data_uuid = models.CharField('数据执行批次', max_length=128, null=True)
    user_id = models.IntegerField('用户id', null=True)
    batch_time = models.DateTimeField('批次时间', null=True)
    class Meta:
        db_table = 'testcase_ran_script_result'








