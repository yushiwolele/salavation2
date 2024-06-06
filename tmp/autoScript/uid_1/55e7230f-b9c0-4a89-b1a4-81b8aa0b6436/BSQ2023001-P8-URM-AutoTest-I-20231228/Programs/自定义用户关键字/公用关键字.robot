*** Settings ***
Library           Selenium2Library
Library           Dialogs
Variables         ../../Conf/env.py

*** Variables ***
@{textarea_dw}    证券代码    证券账户DW    主体名称DW    #多行文本控件
${CHROME_OPTIONS}    add_argument("--headless")

*** Keywords ***
登录
    open browser    https://www.baidu.com    chrome_options=${CHROME_OPTIONS}
    # 添加日志或打印语句
    Log    浏览器已成功打开    # 向日志中添加信息
    Log To Console    浏览器已成功打开    # 打印信息到控制台

退出
    close all browsers

登录2
     @{env}        Create List        TEST       Chrome
    BuiltIn.Set Global Variable    ${env}
    open browser    ${${env}[0]}[支撑平台门户路径]    ${env}[1]
    Log To Console    ${${env}[0]}
