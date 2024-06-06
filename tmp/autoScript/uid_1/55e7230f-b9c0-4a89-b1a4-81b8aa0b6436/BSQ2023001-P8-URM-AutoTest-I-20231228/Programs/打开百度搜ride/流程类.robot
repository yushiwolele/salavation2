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
    Log    日志日志日志ride    # 向日志中添加信息
    sleep    2s
    Input Text    id=kw    ride
    sleep    2s
    click button    id=su

打印日志
    Log    打印日志22ride
