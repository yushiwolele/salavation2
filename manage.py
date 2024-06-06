#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

from Salvation.settings import *


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Salvation.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':

    # 获取日志配置
    log_config = LOGGING
    # 获取日志处理器
    log_handlers = log_config.get('handlers', {})
    # 为每个文件处理器执行轮转操作
    for handler_name, handler_settings in log_handlers.items():
        if handler_settings['class'] == 'logging.handlers.TimedRotatingFileHandler':
            # 如果log文件年月日是小于当前服务器年月日，则执行日志轮转
            filename = handler_settings['filename'] #日志地址
            file_mtime = os.path.getmtime(filename)
            # 将文件的修改时间戳转换为日期对象
            file_mtime_date = datetime.fromtimestamp(file_mtime).date()
            # 获取当前日期
            current_date = datetime.now().date()
            # 比较文件日期和当前日期
            is_date_earlier = file_mtime_date < current_date
            if is_date_earlier:
                handler = TimedRotatingFileHandler(handler_settings['filename'])
                handler.doRollover()

    main()


