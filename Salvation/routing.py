# -*- coding: utf-8 -*-            
# @Author : libeijie
# @Time : 2023/12/22 16:38

from django.urls import re_path
from apps.testcases.views.script_consumer import *
from apps.testcases.views.script_test import *

websocket_urlpatterns = [
    re_path(r'ws/ws_run_script/$', ScriptConsumer.as_asgi()),
    re_path(r'ws/ws_test/$', ScriptTest.as_asgi()),
]