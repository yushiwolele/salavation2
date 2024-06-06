# -*- coding: utf-8 -*-            
# @Author : libeijie
# @Time : 2023/12/22 16:28

import json
import asyncio

from celery import shared_task

from channels.generic.websocket import AsyncWebsocketConsumer

from testcases.service.operation.runTestCases_service import *

class LogConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("建立日志连接")
        await self.accept()

    async def send_logs(self, log_content):
        await self.channel_layer.group_add("some_group", self.channel_name)
        await self.channel_layer.group_send(
            "some_group",
            {
                "type": "send_logs",
                "log_content": log_content,
            },
        )

    async def disconnect(self, close_code):
        print("日志连接断开")

    async def send_logs_handler(self, event):
        log_content = event["log_content"]
        await self.send(text_data=json.dumps({"log_content": log_content}))



class ScriptConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("来建立连接啦")
        await self.accept()

    async def disconnect(self, close_code):
        print("连接disconnect")
        pass

    async def receive(self, text_data=None, bytes_data=None):
        print('receive建立')
        data = json.loads(text_data)
        checked_testcases = data.get('checked_testcases')
        checked_testcases = json.loads(checked_testcases)
        folder_root = data.get('folder_root')
        execution_environment = data.get('execution_environment')
        browser = data.get('browser')
        rtcs = RunTestCasesService()
        try:
            # 去掉脚本中和用户交互的内容
            rtcs.remove_interaction_script(folder_root, execution_environment, browser)
            # 去掉参数robot中的testcases
            rtcs.process_folders(folder_root)
            # 生成参数文件argfile.txt
            rtcs.generate_testcase_files(folder_root, checked_testcases)
        except Exception as e:
            logger.error('报错信息：' + repr(e) + ',报错的行号:' + str(e.__traceback__.tb_lineno))
            #msg = f"发生错误：{str(e)}"
            await self.send(text_data=json.dumps({'execution_status': 'completed', 'log_content': 'error_occurred'}))
            return
        command = [
            'robot',
            '--argumentfile', os.path.join(folder_root, rtcs.argfile),
            folder_root
        ]
        shell = False
        if "Windows" in platform.platform():
            shell = True

        log_path = codecs.open(os.path.join(folder_root,'Logs','logs.log'), "a+", "utf-8")
        process = subprocess.Popen(command, shell=shell, stdout=log_path, stderr=subprocess.STDOUT)
        # 获取初始文件指针位置
        initial_position = log_path.tell()
        print(process.poll())
        log_consumer = LogConsumer()
        await log_consumer.connect()
        await self.channel_layer.group_add("some_group", self.channel_name)
        while process.poll() is None:
            # 移动文件指针到当前位置
            log_path.seek(initial_position)
            #读取文件
            log_content = log_path.read()
            if log_content:
                print(log_content)
                log_consumer.send_logs(log_content)
                await asyncio.sleep(1)
            # 更新文件指针位置
            initial_position = log_path.tell()
            await asyncio.sleep(1)
        await log_consumer.disconnect()
        # 执行完成后，你也可以读取一次最终的日志内容
        log_path.seek(initial_position)
        final_log_content = log_path.read()
        print(final_log_content)
        log_path.close()

        await self.send(text_data=json.dumps({'log_content': final_log_content}))
        # Execution completed, send a message to the frontend
        await self.send(text_data=json.dumps({'execution_status': 'completed','log_content': '执行完成'}))

