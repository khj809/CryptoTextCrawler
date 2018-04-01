import os
import re
import glob
import requests
from bs4 import BeautifulSoup

from config import settings
from .exceptions import *

_settings = settings['common']


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


def _get_new_filename(path, prefix):
    filenames = glob.glob(os.path.join(path, '%s_*.txt' % prefix))
    nums = sorted(list(map(lambda x: int(re.findall('\d+$', os.path.splitext(x)[0])[0]), filenames)) + [0])
    new_filename = '%s_%08d.txt' % (prefix, nums[-1] + 1)
    return os.path.join(path, new_filename)


def save_result(result, locale, prefix):
    save_path = _settings['result_path'][locale]
    filename = _get_new_filename(save_path, prefix)

    with open(filename, 'w', encoding='utf8') as f:
        if isinstance(result, str):
            f.write(result)
        elif isinstance(result, list):
            for s in result:
                f.write(s + '\n')
        else:
            pass
