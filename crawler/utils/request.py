import requests
from bs4 import BeautifulSoup
from ..exceptions import *
from . import _settings


def get_session(is_mobile=True):
    s = requests.Session()
    if is_mobile:
        s.headers = {
            'User-Agent': _settings['user-agent']
        }
    return s


def get_soup(url, params=None, is_mobile=True, decode_utf8=True):
    s = get_session(is_mobile)
    s.params = params if params is not None and isinstance(params, dict) else {}

    resp = s.get(url, timeout=_settings['request_timeout'])
    if resp.status_code >= 400:
        raise RequestException(url=url, response=resp)

    if decode_utf8:
        html = resp.content.decode('utf8', errors='ignore')
    else:
        html = resp.content

    try:
        soup = BeautifulSoup(html, 'html5lib')
    except Exception as e:
        raise ParsingException(html=html)

    return soup


def get_json(url, data):
    s = get_session()
    headers = {
        'content-type': 'application/json'
    }

    payload = json.dumps(data)
    resp = s.request('POST', url, data=payload, headers=headers)
    if resp.status_code >= 400:
        raise PostRequestException(url=url, response=resp, payload=payload)

    return resp.json()


