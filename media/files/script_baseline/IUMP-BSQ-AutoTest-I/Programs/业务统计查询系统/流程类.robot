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
    Log    日志日志日志    # 向日志中添加信息
    sleep    2s
    Input Text    id=kw    robotframeworkride
    sleep    2s
    click button    id=su

关闭
    Close Browser
