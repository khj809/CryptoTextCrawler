import os
import re
import glob
import requests
from bs4 import BeautifulSoup

from config import settings
from .exceptions import *

_settings = settings['common']

regex_japanese = u'[\u4E00-\u9FFF\u3040-\u309Fー\u30A0-\u30FF]+'
regex_chinese = u'[⺀-⺙⺛-⻳⼀-⿕々〇〡-〩〸-〺〻㐀-䶵一-鿃豈-鶴侮-頻並-龎]+'
regex_korean = u'[ㄱ-ㅎㅏ-ㅣ가-힣]+'


def classify_locale(str):
    k = c = j = e = 0
    lines = str.split('\n')
    for line in lines:
        if re.search(regex_chinese, line, re.U):
            c += 1
        elif re.search(regex_japanese, line, re.U):
            j += 1
        elif re.search(regex_korean, line, re.U):
            k += 1
        else:
            e += 1

    max_locale = max(k,c,j,e)
    if max_locale == k:
        return 'korean'
    elif max_locale == c:
        return 'chinese'
    elif max_locale == j:
        return 'japanese'
    else:
        return 'english'


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


def save_result(result, file, locale=None):
    if isinstance(result, str):
        result_string = result
    elif isinstance(result, list):
        result_string = '\n'.join(result)
    else:
        logging.error('Invalid file is given with type "%s"' % type(result).__name__)
        return

    locale = locale or classify_locale(result_string)

    save_path = _settings['result_path'][locale]
    # filename = _get_new_filename(save_path, prefix)
    filename = os.path.join(save_path, '%s.txt' % file)

    with open(filename, 'w', encoding='utf8') as f:
        f.write(result_string)
