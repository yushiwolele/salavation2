# -*- coding: utf-8 -*-            
# @Author : libeijie
# @Time : 2023/12/22 16:28

import json
import subprocess
import time
from channels.generic.websocket import AsyncWebsocketConsumer

from testcases.service.operation.runTestCases_service import *


class ScriptTest(AsyncWebsocketConsumer):
    async def connect(self):
        print("来建立连接了")
        await self.accept()

    async def disconnect(self, close_code):
        print("连接disconnect")
        pass

    async def receive(self, text_data=None, bytes_data=None):
        print('test_receive建立')
        for i in range(10):
            print(i)
            await self.send(text_data=json.dumps({'execution_status': 'completed', 'log_content': '执行完成'}))
            time.sleep(3)
            if i == 9:
                await self.close()

