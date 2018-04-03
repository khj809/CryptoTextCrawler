import logging
import time
import random
import copy
from crawler.util import get_json, get_soup, save_result, get_cursor
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


def save_to_db(id, tag, author, permlink):
    cur = get_cursor()
    cur.execute('INSERT INTO steemit (post_id, tag, author, permlink) '
                'VALUES (?, ?, ?, ?)',
                (id, tag, author, permlink))


def crawl_posts_in_tag(tag, count):
    cur = get_cursor()
    cur.execute('SELECT author, permlink FROM steemit WHERE tag=? ORDER BY id DESC LIMIT 1', (tag, ))
    last_crawled = cur.fetchone()
    if last_crawled:
        start_author = last_crawled[0]
        start_permlink = last_crawled[1]
    else:
        start_author = None
        start_permlink = None

    cur.execute('SELECT COUNT(id) FROM steemit WHERE tag=?', (tag, ))
    count_crawled = cur.fetchone()[0]

    logging.info('Start crawling {count} posts related to "{tag}" '.format(count=count, tag=tag) +
                 'from author={author}, permlink={permlink}'.format(
                     author=(start_author or 'None'), permlink=(start_permlink or 'None'))
                 )

    crawled = 0

    while True:
        try:
            logging.info('[{tag}] Getting next 20 discussions from author={author}, permlink={permlink}'.format(
                tag=tag, author=(start_author or 'None'), permlink=(start_permlink or 'None')))

            discussions = crawl_post_list(tag, 20, start_author, start_permlink)
            if len(discussions) == 0:
                logging.info('[{tag}] Got 0 discussions. Break..'.format(tag=tag))
                break

            finished = False
            for discussion in discussions:
                header = '[{tag}|{idx}]'.format(tag=tag, idx=count_crawled+crawled+1)

                if crawled >= count:
                    finished = True
                    break

                try:
                    logging.info('{header} Requesting post contents of {id}'.format(header=header, id=discussion['id']))
                    content = crawl_post_content(discussion['url'])
                    logging.info('{header} Saving post content of {id}'.format(header=header, id=discussion['id']))
                    save_result(content, 'steemit_{tag}_{id}'.format(tag=tag, id=discussion['id']))

                except Exception as e:
                    logging.error(e)
                    logging.error('{header} Failed to request post content of {id}'.format(header=header, id=discussion['id']))
                finally:
                    time.sleep(random.uniform(0.5, 1.0))
                    save_to_db(discussion['id'], tag, discussion['author'], discussion['permlink'])
                    crawled += 1

            if finished:
                break

            start_author = discussions[-1]['author']
            start_permlink = discussions[-1]['permlink']

        except:
            logging.error('[{tag}] Failed to get discussion list. Will be retried..'.format(tag=tag))
            time.sleep(random.uniform(1.5, 2.0))

    logging.info('Finished crawling {crawled} posts related to "{tag}"'.format(crawled=crawled, tag=tag))


def crawl_steemit(options='bitcoin_all,blockchain_all,cryptocurrency_all'):
    options = options.split(',')
    for option in options:
        [tag, count] = option.split('_')
        count = -1 if count == 'all' else int(count)
        crawl_posts_in_tag(tag, count)
