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
    :FOR    ${i}    IN    @{list}
	    点击查询
	    ...    AND    Run Keyword And Continue On Failure    Alert Should not Be Present
		sleep    3
		点击最大化
	退出

退出
    close all browsers

登录2
    ${env}    Get Selections From User    请选择环境：    TEST    DEV    BETA    请选择浏览器：    Firefox    headlessChrome    Chrome
    BuiltIn.Set Global Variable    ${env}
    open browser    ${${env}[0]}[支撑平台门户路径]    ${env}[1]
    Log To Console    ${${env}[0]}
