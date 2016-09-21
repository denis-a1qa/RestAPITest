# -*- coding: utf-8 -*-
from robot.api import logger
import json
from xml.dom import minidom
import decorator
import re

"""
Library for logging request and response, which based on [ http://docs.python-requests.org/en/latest| requests ]  library.
"""


def write_stream_logs(response):
    """
    Logging of http-request and response for streams (multiple jsons in response)

    *Args:*\n
    _response_ - object [ http://docs.python-requests.org/en/latest/api/#requests.Response | "Response" ]

    *Response:*\n
    Formatted output of request and response in test log

    Example:
    | *Test cases* | *Action*                          | *Argument*            | *Argument*                | *Argument*  |
    | Simple Test  | RequestsLibrary.Create session    | Alias                 | http://www.example.com    |             |
    |              | ${response}=                      | RequestsLibrary.Get request       | Alias         | /           |
    |              | RequestsLogger.Write stream logs          | ${response}           |                           |             |
    """
    write_log(response, is_stream=True)

def write_log(response,  is_stream=False):
    """
    Logging of http-request and response

    *Args:*\n
    _response_ - object [ http://docs.python-requests.org/en/latest/api/#requests.Response | "Response" ]
    _isStream_ -

    *Response:*\n
    Formatted output of request and response in test log

    Example:
    | *Test cases* | *Action*                          | *Argument*            | *Argument*                | *Argument*  |
    | Simple Test  | RequestsLibrary.Create session    | Alias                 | http://www.example.com    |             |
    |              | ${response}=                      | RequestsLibrary.Get request       | Alias         | /           |
    |              | RequestsLogger.Write log          | ${response}           |                           |             |
    """

    msg = request_log(response)
    # тело ответа
    converted_string = ''
    if response.content:
        # получение кодировки входящего сообщения
        response_content_type = response.headers.get('content-type')
        if 'application/json' in response_content_type:
            response_content = get_decoded_response_body(response.content, response_content_type)
            if is_stream:
                for line in response.iter_lines():
                    jsonString = json.loads(line)
                    jsonString = json.dumps(jsonString, sort_keys=True,
                                            ensure_ascii=False, indent=4,
                                            separators=(',', ': '))
                    converted_string += jsonString
            else:
                jsonString = json.loads(response_content)
                jsonString = json.dumps(jsonString, sort_keys=True,
                                            ensure_ascii=False, indent=4,
                                        separators=(',', ': '))
            converted_string=jsonString
        elif 'application/xml' in response_content_type:
            response_content = get_decoded_response_body(response.content, response_content_type)
            xml = minidom.parseString(response_content)
            converted_string = xml.toprettyxml()
        else:
            response_content = get_decoded_response_body(response.content, response_content_type)
            msg.append(response_content)
    # вывод сообщения в лог
    logger.info('\n'.join(msg))
    if converted_string:
        logger.info(converted_string)


def request_log(response):
    msg = []
    # информация о запросе
    msg.append(
        '> {0} {1}'.format(response.request.method, response.request.url))
    for req_key, req_value in response.request.headers.iteritems():
        msg.append('> {header_name}: {header_value}'.format(header_name=req_key,
                                                            header_value=req_value))
    msg.append('>')
    if response.request.body:
        msg.append(response.request.body)
    msg.append('* Elapsed time: {0}'.format(response.elapsed))
    msg.append('>')
    # информация о ответе
    msg.append('< {0} {1}'.format(response.status_code, response.reason))
    for res_key, res_value in response.headers.iteritems():
        msg.append('< {header_name}: {header_value}'.format(header_name=res_key,
                                                            header_value=res_value))
    msg.append('<')
    return msg


def get_decoded_response_body(response_content, responce_content_type):
    match = re.findall(re.compile('charset=(.*)'),
                       responce_content_type)
    # перекодирование тела ответа в соответствие с кодировкой, если она присутствует в ответе
    if len(match) == 0:
        return response_content
    else:
        responce_charset = match[0]
        return response_content.decode(responce_charset)


def _log_decorator(func, *args, **kwargs):
    response = func(*args, **kwargs)
    write_log(response)
    return response


def _log_decorator_stream(func, *args, **kwargs):
    response = func(*args, **kwargs)
    write_stream_logs(response)
    return response


def log_decorator(func):
    """
    Decorator for http-requests. Logging request and response.
    Decorated function must return response object [ http://docs.python-requests.org/en/latest/api/#requests | Response ]

    Example:

    | @RequestsLogger.log_decorator
    | def get_data(alias, uri)
    |     response = _request_lib_instance().get_request(alias, uri)
    |     return response

    Output:
    Formatted output of request and response in test log
    """
    func.cache = {}
    return decorator.decorator(_log_decorator, func)


def log_stream_decorator(func):
    func.cache = {}
    return decorator.decorator(_log_decorator_stream, func)