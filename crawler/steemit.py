from crawler.util import get_json
from config import settings

_settings = settings['steemit']


def crawl_post_list(tag, count, start_author=None, start_permlink=None):
    payload = dict(_settings['payload_list'])
    payload['params'][2][0]['tag'] = tag
    payload['params'][2][0]['limit'] = count
    if start_author is not None:
        payload['params'][2][0]['start_author'] = start_author
        payload['params'][2][0]['start_permlink'] = start_permlink

    data = get_json(_settings['address'], payload)
    data = data['result']
    if start_author is not None:
        data = data[1:]

    return data


def crawl_post_content(url):
    payload = dict(_settings['payload_content'])
    payload['params'][2].append(url)
    data = get_json(_settings['address'], payload)

    content = data['result']['content']
    posts = [content[x]['body'] for x in content.keys()]

    return posts


