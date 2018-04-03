import logging
import time
import random
from crawler.util import get_soup, save_result
from config import settings

_settings = settings['5ch']


def crawl_thread_id_list():
    soup = get_soup(_settings['address']['list'], is_mobile=False, decode_utf8=False)
    links = soup.find('small', {'id': 'trad'}).find_all('a')
    thread_list = []
    for thread in links:
        thread_list.append(thread.attrs['href'].split('/')[0])

    return thread_list


def crawl_thread_content(thread_id):
    address = _settings['address']['thread'].format(thread_id=thread_id)
    soup = get_soup(address, is_mobile=False, decode_utf8=False)

    posts = soup.find('div', {'class': 'thread'}).find_all('div', {'class': 'post'})
    results = []
    for post in posts:
        message = post.find('div', {'class', 'message'}, recursive=False)
        results.append(message.get_text('\n'))

    return results


def crawl_5ch():
    logging.info('Start crawling 5ch threads...')
    try:
        logging.info('Getting thread id list..')
        thread_list = crawl_thread_id_list()
        num_total = len(thread_list)
        for idx, thread_id in enumerate(thread_list):
            header = '[{idx}/{total}]'.format(idx=idx+1, total=num_total)
            try:
                logging.info('{header} Requesting contents of thread {thread_id}'.format(header=header, thread_id=thread_id))
                contents = crawl_thread_content(thread_id)

                logging.info('{header} Saving contents of thread {thread_id}'.format(header=header, thread_id=thread_id))
                save_result(contents, '5ch_%s' % thread_id, 'japanese')
            except Exception as e:
                logging.error(e)
                logging.error('{header} Failed to request contents of thread {thread_id}'.format(header=header, thread_id=thread_id))
            finally:
                time.sleep(random.uniform(1.0, 1.5))

    except Exception as e:
        logging.error(e)
        logging.error('Failed to get thread id list')

    logging.info('Finished crawling 5ch threads!')
