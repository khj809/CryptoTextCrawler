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


def crawl_forum_posts(forum_url, page=1):
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

    return posts


def crawl_8btc(news_page=None, forum_page=None):
    # logging.info('Start crawling 8btc news...')
    # page = news_page
    # while True:
    #     try:
    #         logging.info('Requesting news page {page}..'.format(page=page))
    #         posts = crawl_news(page)
    #
    #         logging.info('Saving news page {page}..'.format(page=page))
    #         save_result(posts, 'chinese', '8btc')
    #     except RequestException:
    #         logging.info('Reached the end of pages of news')
    #         break
    #     except Exception:
    #         logging.error('Failed to get news page {page}'.format(page=page))
    #         continue
    #     finally:
    #         time.sleep(random.uniform(0.5, 1.0))
    #         page += 1
    #
    # logging.info('Finished crawling 8btc news!')

    logging.info('Start crawling 8btc forum...')
    page = forum_page or 1
    # forum max page is 1000
    while page <= 1000:
        try:
            logging.info('Getting forum links on page {page}'.format(page=page))
            links = crawl_forum_links(page)

            for idx, (link, post_page) in enumerate(links):
                logging.info('Requesting forum content of %s' % link)
                total_posts = []
                for cur_post_page in range(1, post_page+1):
                    logging.info('Requesting forum content of %s (%d/%d)' % (link, cur_post_page, post_page))
                    try:
                        posts = crawl_forum_posts(link, cur_post_page)
                        total_posts = total_posts + posts
                    except Exception:
                        logging.error('Failed to get page %d/%d of forum content %s' % (cur_post_page, post_page, link))
                    finally:
                        time.sleep(random.uniform(1.0, 1.5))

                logging.info('Saving forum content of %s' % link)
                save_result(total_posts, 'chinese', '8btc_forum')
        except:
            logging.error('Failed to get forum links on page %s' % page)
        finally:
            time.sleep(random.uniform(1.0, 1.5))
            page += 1

    logging.info('Finished crawling 8btc forums!')
