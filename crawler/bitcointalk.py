import re
import math
import logging
import time
import random
from config import settings
from crawler.util import get_soup, save_result

_settings = settings['bitcointalk']


def crawl_board_posts(board_url, page=1):
    paged_url = re.sub(r'.(\d)+$', '.%s' % ((page-1)*40), board_url)
    soup = get_soup(paged_url)
    bodyarea = soup.find('div', {'id': 'bodyarea'})

    # get links of posts
    table = bodyarea.find('div', {'class': 'tborder', 'style': None}).table
    trs = table.find_all('tr', {'class': None})[1:]
    posts = []
    for tr in trs:
        td = tr.find_all('td', {'class': ['windowbg3', 'windowbg']})
        link = td[0].span.a.attrs['href']
        pages = math.ceil(int(td[1].text)/20)
        posts.append((link, pages))

    # check if this page is the last one
    next_page = bodyarea.find('td', {'class': 'middletext'}).find('a', text='»')

    return posts, next_page is None


def crawl_post(post_url, page=1):
    paged_url = re.sub(r'.(\d)+$', '.%s' % ((page-1)*20), post_url)
    soup = get_soup(paged_url)
    bodyarea = soup.find('div', {'id': 'bodyarea'})

    table = bodyarea.find('form').find('table', {'class': 'bordercolor'})
    trs = table.find_all('tr')
    trs = list(filter(lambda x: 'class' in x.attrs.keys() and x.attrs['class'] == trs[0].attrs['class'], trs))
    posts = []
    for tr in trs:
        posts.append(tr.find('div', {'class': 'post'}).get_text('\n'))

    return '\n'.join(posts)


def crawl_bitcointalk_board(board, locale, start_page=1):
    page = start_page

    logging.info('Start crawling korean board')
    while True:
        try:
            logging.info('Getting post links of page {page}..'.format(page=page))
            posts, is_last = crawl_board_posts(board, page)

            for idx, (link, post_pages) in enumerate(posts):
                total_posts = []
                for cur_post_page in range(1, post_pages+1):
                    try:
                        logging.info('Requesting post contents of %s (%d/%d)' % (link, cur_post_page, post_pages))
                        post = crawl_post(link, cur_post_page)
                        total_posts.append(post)
                    except:
                        logging.error('Failed to request contents of %s (%d/%d)' % (link, cur_post_page, post_pages))
                    finally:
                        time.sleep(random.uniform(0.5, 1.0))

                if len(total_posts) != 0:
                    logging.info('Saving post contents of %s' % link)
                    save_result(total_posts, locale, 'bitcointalk')

            if is_last:
                break
            else:
                page += 1

        except:
            logging.error('Failed to get links of page {page}'.format(page=page))

    logging.info('Finished crawling korean board!')


def crawl_bitcointalk():
    boards = [
        ('korean', _settings['address']['korean']),
        ('japanese', _settings['address']['japanese']),
        ('chinese', _settings['address']['chinese']),
        ('english', _settings['address']['english'])
    ]

    for (locale, url) in boards:
        crawl_bitcointalk_board(url, locale, 1)
