import json
import logging


class CustomException(Exception):
    def __init__(self, log):
        super().__init__(log)
        logging.error(log)


class RequestException(CustomException):
    def __init__(self, url, response):
        log = 'Request Failed: {code}\n'.format(code=response.status_code) + \
                'URL: {url}\n'.format(url=url) + \
                'response: {resp}\n'.format(resp=response.content.decode('utf8'))
        super().__init__(log)


class PostRequestException(CustomException):
    def __init__(self, url, response, payload):
        log = 'POST Request Failed: {code}\n'.format(code=response.status_code) + \
                'URL: {url}\n'.format(url=url) + \
                'data: {data}\n'.format(data=json.dumps(payload)) + \
                'response: {resp}\n'.format(resp=response.content.decode('utf8'))
        super().__init__(log)


class ParsingException(CustomException):
    def __init__(self, html):
        log = 'Parsing HTML Failed\n' + \
            '{document}\n'.format(document=html)
        super().__init__(log)


class ElementNotFoundException(CustomException):
    def __init__(self, target, body):
        log = 'Element Not Found\n' + \
            'target: {target} {attrs}\n'.format(target=target[0], attrs=json.dumps(target[1])) + \
            'body: {body}\n'.format(body=body)
        super().__init__(log)
