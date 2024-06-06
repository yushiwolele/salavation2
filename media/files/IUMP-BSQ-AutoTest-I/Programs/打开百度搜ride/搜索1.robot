*** Settings ***
Library           Selenium2Library
Library           Collections
Library           OperatingSystem
Library           BuiltIn
Library           String
Library           Screenshot
Library           Reserved
Library           Easter

*** Test Cases ***
检查功能基本流程
    Log    日志日志日志搜索1    # 向日志中添加信息
    sleep    2s
    Input Text    id=kw    selenium
    sleep    2s
    click button    id=su

打印日志
    Log to console    打印日志22搜索1
