*** Settings ***
Documentation    Проверка demo REST сервиса http://httpbin.org/
...            [https://jira.billing.ru/browse/PQAGAUTO-1752 | PQAGAUTO-1752]

Library  String
Library  RequestsChecker
Library  RequestsLogging
Library  HttpBinLib
Library  Collections

Test Setup  Set service name  http://httpbin.org

*** Keywords ***
Basic Auth Request Check Creds Test
    [Arguments]  ${url}  ${entered_login}  ${entered_password}  ${expected_resp_code}
    ${response}=   Send auth request  ${url}  ${entered_login}  ${entered_password}
    Check Status Code  ${expected_resp_code}  ${response}

*** Test Cases ***
Test_Data_For_Basic_Auth
    [Template]  Basic Auth Request Check Creds Test
    #url            #entered_login      #entered_password       #expected HTTP response code
    test/12345      test                12345                   200
    test/12345      invalidUser         12345                   401
    test/12345      test                InvalidPassword         401


Get Request Check Headers Test
    set test variable   ${header_key}    Name
    set test variable   ${header_value}  TestName
    ${headers}=  Create dictionary  ${header_key}=${header_value}
    ${response}=   Send get request  ${headers}
    Check Status Code  200  ${response}
    Dictionary should contain item  ${response.json()['headers']}  ${header_key}  ${header_value}


Stream Request Check Lines Number Test
    set test variable  ${lines_number}  5
    ${response}=  Send stream request  ${lines_number}
    Check Status Code  200  ${response}
    ${actual_lines_number}=  String.Get Line Count  ${response.text}
    Should be equal as integers  ${lines_number}  ${actual_lines_number}  msg=Incorrect number of lines
    RequestsLogging.Write Stream Logs  ${response}





