import re
import logging
import time
import random
from crawler.util import get_soup, save_result
from config import settings
from .exceptions import RequestException, ElementNotFoundException

_settings = settings['8btc']


def crawl_news(page=1):
    soup = get_soup(_settings['address']['news'].format(page=page))
    article_list = soup.find('div', {'id': 'list_content_all'})
    if article_list is None:
        raise ElementNotFoundException(target=('div', {'id': 'list_content_all'}), body=soup)

    article_list = article_list.find_all('article')
    posts = []
    for article in article_list:
        posts.append(article.find('section').get_text('\n').strip())

    return posts


def crawl_forum_links(page=1):
    soup = get_soup(_settings['address']['forum'].format(page=page), is_mobile=False)
    thread_list = soup.find('div', {'id': 'threadlist'}).find_all('div', {'id': re.compile('normalthread_(\d)+$')})
    links = []
    for thread in thread_list:
        link = thread.find('div', {'class': 'title-info'}).find('a').attrs['href']
        tps = thread.find('span', {'class': 'tps'})
        post_page = 1 if tps is None else int(tps.find_all('a')[-1].text)
        links.append((link, post_page))

    return links


def crawl_forum_post(forum_url, page=1):
    tmp = forum_url.split('/')[-1].split('-')
    tmp[2] = str(page)
    url = '/'.join([_settings['address']['base'], '-'.join(tmp)])

    soup = get_soup(url)
    post_list = soup.find('div', {'class': 'postlist'}).find_all('div', {'class': 'plc cl'})
    posts = []
    for post in post_list:
        script = post.find('script')
        if script is not None:
            script.decompose()
        text = post.find('div', {'class': 'message'}).get_text('\n').strip()
        posts.append(text)

    return '\n'.join(posts)


def crawl_8btc_news(start_page=1, end_page=-1):
    logging.info('Start crawling 8btc news...')
    if end_page == -1:
        end_page = 1000

    page = start_page
    while page <= end_page:
        try:
            logging.info('Requesting news page {page}..'.format(page=page))
            posts = crawl_news(page)

            logging.info('Saving news page {page}..'.format(page=page))
            save_result(posts, 'chinese', '8btc_news_%s' % page)

            time.sleep(random.uniform(0.5, 1.0))
            page += 1
        except RequestException:
            logging.info('Reached the end of pages of news')
            break
        except Exception:
            logging.error('Failed to get news page {page}'.format(page=page))

    logging.info('Finished crawling 8btc news!')


def crawl_8btc_forums(start_page=1, end_page=1000):
    logging.info('Start crawling 8btc forum...')
    end_page = min(1000, end_page)
    page = start_page
    while page <= end_page:
        try:
            logging.info('Getting forum links on page {page}'.format(page=page))
            links = crawl_forum_links(page)
            num_links = len(links)

            for idx, (link, num_pages) in enumerate(links):
                header = '[Page {page} | {idx}/{links}]'.format(page=page, idx=idx+1, links=num_links)
                forum_id = int(link.split('/')[-1].split('-')[1])
                forum_contents = []
                for cur_post_page in range(1, num_pages+1):
                    logging.info('{header} Requesting forum content of {id} ({cur}/{pages})'.format(
                        header=header, id=forum_id, cur=cur_post_page, pages=num_pages
                    ))
                    try:
                        post = crawl_forum_post(link, cur_post_page)
                        forum_contents.append(post)
                    except Exception:
                        logging.error('{header} Failed to get forum content of {id} ({cur}/{pages})'.format(
                            header=header, id=forum_id, cur=cur_post_page, pages=num_pages
                        ))
                    finally:
                        time.sleep(random.uniform(1.0, 1.5))

                if len(forum_contents) != 0:
                    logging.info('{header} Saving forum content of {id}'.format(header=header, id=forum_id))
                    save_result(forum_contents, 'chinese', '8btc_forum_%s' % forum_id)

            page += 1

        except Exception as e:
            logging.error(e)
            logging.error('Failed to get forum links on page %s. Will be retried..' % page)

    logging.info('Finished crawling 8btc forums!')


def crawl_8btc(options='news:all,forum:all'):
    options = options.split(',')
    for option in options:
        [target, pages] = option.split(':')
        if target == 'news':
            if pages == 'all':
                start_page, end_page = 1, -1
            else:
                [start_page, end_page] = list(map(lambda x: int(x), pages.split('-')))
            crawl_8btc_news(start_page, end_page)
        elif target == 'forum':
            if pages == 'all':
                start_page, end_page = 1, -1
            else:
                [start_page, end_page] = list(map(lambda x: int(x), pages.split('-')))
            crawl_8btc_forums(start_page, end_page)
        else:
            pass
