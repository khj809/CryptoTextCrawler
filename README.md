# CryptoTextCrawler

본 프로젝트는 가상화폐 관련 커뮤니티인 Steemit, 8btc, bitcointalk, 5ch cryptocoin 등에서 유저들이 올린 대량의 글과 댓글 등의 텍스트 데이터를 크롤링하기 위해 제작되었습니다.



## Installation

```shell
$ virtualenv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```



## Usage

#### Steemit

```python
from crawler.steemit import crawl_steemit
crawl_steemit(options='bitcoin_all,blockchain_50,cryptocurrency_all', refresh_db=False)
```

`options`은 `{tag}_{count}` 형태이며, `count=all` 인 경우 해당 태그의 모든 글을 크롤링합니다. 가령 위와 같은 옵션인 경우 *bitcoin*, *cryptocurrency* 태그의 글을 모두 크롤링하고, *blockchain* 태그의 글은 50개만 크롤링합니다.

steemit의 경우 페이지 개념이 없기 때문에 현재 어디까지 크롤링이 완료되었는지 정보를 sqlite DB에 저장하며, 프로세스가 재실행되는 경우 마지막에 크롤링했던 글부터 시작하여 크롤링을 시도합니다. 만약 DB를 초기화하고 처음부터 크롤링하기를 원한다면 `refresh_db=True`로 함수를 실행하면 됩니다.



#### 8btc

```python
from crawler.eightbtc import crawl_8btc
crawl_8btc(options='news_all,forum_1:50')
```

`options`은 `{type}_{range}`의 형태이며, `type`은 *news* 또는 *forum*만 허용되고, `range` 는 보통 `{start_page}:{end_page}`의 형태를 취합니다. `end_page=-1` 또는 `range=all`인 경우 모든 페이지의 글들을 크롤링합니다. 가령 위와 같은 옵션인 경우 news는 모든 페이지를 크롤링하고, forum은 1페이지부터 50페이지까지 크롤링합니다. (단 forum은 1000페이지까지만 크롤링이 가능합니다.)



#### Bitcointalk

```python
from crawler.bitcointalk import crawl_bitcointalk
crawl_bitcointalk(options='korean_all,japanese_1:-1,chinese_1:50,english_50:100')
```

`options`은 `{lang}_{range}`의 형태이며, `lang`은 *korean, japanese, chinese, english*만 허용되고, `range`는 `all`또는 `{start_page}:{end_page}`의 형태입니다. `end_page=-1`또는 `range=all`인 경우 모든 페이지의 글들을 크롤링합니다. 가령 위와 같은 옵션인 경우 korean 전체, japanese 전체, chinese 1~50페이지, english 50~100페이지까지 크롤링합니다. 



#### 5ch cryptocoin

```python
from crawler.fivech import crawl_5ch
crawl_5ch()
```

5ch는 게시물 양이 많지 않기 때문에 별도의 옵션을 두지 않았습니다.

