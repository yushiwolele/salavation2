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
����ѡ���1�޸ĺ�s
    Log    ��־��־��־    # ����־�������Ϣ
    sleep    2s
    Input Text    id=kw    robotframework
    sleep    2s
    click button    id=su
����ѡ���2
    close window
	sleep   2s		����ѡ���1
*** Keywords ***
����ѡ���1
	Log		����ѡ���1