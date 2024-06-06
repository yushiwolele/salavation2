*** Settings ***
Suite Setup       登录2
Suite Teardown    退出
Resource          自定义用户关键字/公用关键字.robot
Library           Selenium2Library
*** Test Cases ***
Empty Test Case For Catch Error
