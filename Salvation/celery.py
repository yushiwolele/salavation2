# -*- coding: utf-8 -*-

import os
import shutil
from datetime import timedelta
from celery import Celery, platforms
from django.conf import settings
from Salvation.settings import BASE_DIR
# 支持root启动
platforms.C_FORCE_ROOT=True

# 指定Django默认配置文件模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Salvation.settings')

# 为我们的项目myproject创建一个Celery实例
app = Celery('Salvation')

# 这里指定从django的settings.py里读取celery配置
app.config_from_object('django.conf:settings',namespace='CELERY')

# 发现任务文件每个app下的task.py
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
