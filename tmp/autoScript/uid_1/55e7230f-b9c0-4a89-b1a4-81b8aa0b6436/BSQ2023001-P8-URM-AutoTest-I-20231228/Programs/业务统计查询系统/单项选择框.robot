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
单项选择框1
    run keyword unless    'asc' contains any asc 1    FAIL    不匹配
    Log    日志日志日志    # 向日志中添加信息
    Scroll Element Into View    xpath=//span[text()='导入检测组']
    log    换行通过
    sleep    2s
    Input Text    id=kw    robotframework
    sleep    2s
    click button    id=su
