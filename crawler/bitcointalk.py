import re
import math
import logging
import time
import random
from config import settings
from crawler.util import get_soup, save_result
from .exceptions import ElementNotFoundException

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

    form = bodyarea.find('form')
    table = form.find('table', {'class': 'bordercolor'})
    if table is None:
        raise ElementNotFoundException(('table', {'class': 'bordercolor'}), form)

    trs = table.find_all('tr')
    trs = list(filter(lambda x: 'class' in x.attrs.keys() and x.attrs['class'] == trs[0].attrs['class'], trs))
    posts = []
    for tr in trs:
        posts.append(tr.find('div', {'class': 'post'}).get_text('\n'))

    return '\n'.join(posts)


def crawl_bitcointalk_board(board, locale, start_page=1, end_page=-1):
    page = start_page

    logging.info('Start crawling {locale} board from page {start_page} to {end_page}'.format(
        locale=locale, start_page=start_page, end_page=('end page' if end_page == -1 else end_page)
    ))
    while True:
        try:
            logging.info('[{locale}|{page}] Getting post links..'.format(locale=locale, page=page))
            posts, is_last = crawl_board_posts(board, page)
            num_posts = len(posts)

            for idx, (link, num_pages) in enumerate(posts):
                post_id = int(link.split('=')[-1].split('.')[0])
                header = '[{locale}|{page}|{idx}/{links}]'.format(
                    locale=locale, page=page, idx=idx+1, links=num_posts
                )
                post_contents = []
                for cur_post_page in range(1, num_pages+1):
                    try:
                        logging.info('{header} Requesting post contents of {id} ({cur}/{pages})'.format(
                            header=header, id=post_id, cur=cur_post_page, pages=num_pages
                        ))
                        post = crawl_post(link, cur_post_page)
                        post_contents.append(post)
                    except ElementNotFoundException as e:
                        logging.error('{header} Skipping this post because it requires login..'.format(header=header))
                        break
                    except:
                        logging.error('{header} Failed to request contents of {id} ({cur}/{pages})'.format(
                            header=header, id=post_id, cur=cur_post_page, pages=num_pages
                        ))
                    finally:
                        time.sleep(random.uniform(0.5, 1.0))

                if len(post_contents) != 0:
                    logging.info('{header} Saving post contents of {id}'.format(header=header, id=post_id))
                    save_result(post_contents, locale, 'bitcointalk_%s' % post_id)

            if is_last or (end_page != -1 and page >= end_page):
                break
            else:
                page += 1

        except Exception as e:
            logging.error(e)
            logging.error('[{locale}|{page}] Failed to get post links. Will be retried..'.format(locale=locale, page=page))

    logging.info('Finished crawling {locale} board!'.format(locale=locale))


def crawl_bitcointalk(options='korean:all,japanese:all,chinese:all,english:all'):
    options = list(map(lambda x: x.lower(), options.split(',')))
    boards = []

    for option in options:
        [locale, pages] = option.split(':')
        if locale not in ['korean', 'japanese', 'chinese', 'english']:
            logging.error('Invalid locale given: %s' % locale)
        else:
            if pages == 'all':
                boards.append((locale, _settings['address'][locale], 1, -1))
            else:
                [start_page, end_page] = list(map(lambda x: int(x), pages.split('-')))
                boards.append((locale, _settings['address'][locale], start_page, end_page))

    for (locale, url, start_page, end_page) in boards:
        crawl_bitcointalk_board(url, locale, start_page, end_page)
