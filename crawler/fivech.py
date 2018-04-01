import logging
from crawler.util import get_soup, save_result
from config import settings

_settings = settings['5ch']


def crawl_threads():
    soup = get_soup(_settings['address'], is_mobile=False, decode_utf8=False)
    thread_contents = soup.find_all('div', {'class': 'THREAD_CONTENTS'})
    threads = []
    for thread_content in thread_contents:
        dds = thread_content.find_all('dd')
        thread = []
        for dd in dds:
            thread.append(dd.text.strip())
        threads.append('\n'.join(thread))

    return threads


def crawl_5ch():
    logging.info('Start crawling 5ch threads...')
    threads = crawl_threads()
    logging.info('Saving result of 5ch data...')
    save_result(threads, 'japanese', '5ch')
    logging.info('Finished crawling 5ch threads!')
