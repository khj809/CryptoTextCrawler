import logging
import time
import random
import copy
from crawler.util import get_json, get_soup, save_result
from config import settings

_settings = settings['steemit']


def crawl_post_count(tag):
    soup = get_soup(_settings['address']['tag'])
    table = soup.find('div', {'class': 'App__content'}).find('table')
    tag_list = list(filter(lambda x: x.find('a').text == tag, table.find_all('tr')))
    if len(tag_list) == 0:
        logging.error('Invalid tag: %s' % tag)
        return 0
    else:
        tds = tag_list[0].find_all('td')
        return int(tds[1].text.replace(',', ''))


def crawl_post_list(tag, count, start_author=None, start_permlink=None):
    payload = copy.deepcopy(_settings['payload_list'])
    payload['params'][2][0]['tag'] = tag
    payload['params'][2][0]['limit'] = count
    if start_author is not None:
        payload['params'][2][0]['start_author'] = start_author
        payload['params'][2][0]['start_permlink'] = start_permlink

    data = get_json(_settings['address']['api'], payload)
    data = data['result']
    if start_author is not None:
        data = data[1:]

    return data


def crawl_post_content(url):
    payload = copy.deepcopy(_settings['payload_content'])
    payload['params'][2].append(url)
    # logging.debug(payload)
    data = get_json(_settings['address']['api'], payload)
    # logging.debug(data)

    content = data['result']['content']
    posts = [content[x]['body'] for x in content.keys()]

    return posts


def crawl_posts_in_tag(tag, count):
    if count == -1:
        count = crawl_post_count(tag)
    else:
        count = min(count, crawl_post_count(tag))

    logging.info('Start crawling {count} posts related to "{tag}"'.format(count=count, tag=tag))

    start_author = None
    start_permlink = None
    num_crawled = 0
    num_failed = 0
    while num_crawled+num_failed < count:
        try:
            logging.info('Getting next 20 posts..')
            posts = crawl_post_list(tag, 20, start_author, start_permlink)
            for post in posts:
                if num_crawled+num_failed >= count:
                    break

                header = '[{crawled}/{total}]'.format(crawled=num_crawled+1, total=count)
                try:
                    logging.info('{header} Requesting post contents of {id}'.format(header=header, id=post['id']))
                    content = crawl_post_content(post['url'])
                    logging.info('{header} Saving post content of {id}'.format(header=header, id=post['id']))
                    save_result(content, 'english', 'steemit_{tag}_{id}'.format(tag=tag, id=post['id']))

                    num_crawled += 1
                except Exception as e:
                    logging.error(e)
                    logging.error('{header} Failed to request post content of {id}'.format(header=header, id=post['id']))
                    num_failed += 1
                finally:
                    time.sleep(random.uniform(0.5, 1.0))

            start_author = posts[-1]['author']
            start_permlink = posts[-1]['permlink']

        except:
            logging.error('Failed to get post list. Will be retried..')

    logging.info('Finished crawling {crawled} posts among {total} posts'.format(crawled=num_crawled, total=count))


def crawl_steemit(options='bitcoin_all,blockchain_all,cryptocurrency_all'):
    options = options.split(',')
    for option in options:
        [tag, count] = option.split('_')
        count = -1 if count == 'all' else int(count)
        crawl_posts_in_tag(tag, count)
