try:
    from bs4 import BeautifulSoup
except ImportError:
    from BeautifulSoup import BeautifulSoup
import requests

DOMAIN_BASE = '4chan.org'
DOMAIN_BOARD = 'boards.%s' % DOMAIN_BASE
DOMAIN_IMAGES = 'images.%s' % DOMAIN_BASE
DOMAIN_WEB = 'www.%s' % DOMAIN_BASE

URL_BOARD = 'http://{domain_board}/{slug}/'
URL_BOARD_PAGE = URL_BOARD + '{page}'
URL_THREAD = URL_BOARD + 'res/{thread_id}'
URL_POST = URL_THREAD + '#p{post_id}'

class RequestError(Exception): pass

class SoupObject(object):
    _soup = None

    def _get_soup(self):
        if self._soup is None:
            req = requests.get(self.url)
            if req.ok:
                self._soup = BeautifulSoup(req.text)
            else:
                raise RequestError(req)
        return self._soup

    def refresh(self):
        self._soup = None

class Board(SoupObject):
    _pages = None

    def __init__(self, slug):
        self.slug = slug
        self._pages = [None for p in self.page_count]

    @property
    def url(self):
        return URL_BOARD.format(
            domain_board=DOMAIN_BOARD,
            slug=self.slug)

    @property
    def page_count(self):
        if self._pages is None:
            return 10
        return len(self._pages)

    def __len__(self):
        return self.page_count

    count = __len__

    def get_page(self, page):
        if self._pages[page] is None:
            #this should be a weakref
            self._pages[page] = BoardPage(self, page)
        return self._pages[page]

    __getitem__ = get_page

    def __iter__(self):
        return iter(self._pages)

    def __contains__(self, item):
        return item in self._pages.values()

class BoardPage(SoupObject):
    threads = None

    def __init__(self, board, page):
        self._board = board
        self.page = page

    @property
    def url(self):
        return URL_BOARD_PAGE.format(
            domain_board=DOMAIN_BOARD,
            slug=self._board.slug,
            page=self.page)

    def get_threads(self):
        return [Thread(self._board, int(tag['id'].lstrip('t'))) \
            for tag in self._get_soup().find_all('div', 'thread')]

class Thread(SoupObject):
    posts = None

    def __init__(self, board, id):
        self._board = board
        self.id = id

    @property
    def url(self):
        return URL_THREAD.format(
            domain_board=DOMAIN_BOARD,
            slug=self._board.slug,
            thread_id=self.id)

    def get_posts(self):
        return [Post(self, int(tag['id'].lstrip('pc'))) \
            for tag in self._get_soup().find_all('div', 'postContainer')]

class Post(SoupObject):
    def __init__(self, thread, id):
        self._thread = thread
        self.id = id

    @property
    def url(self):
        return URL_POST.format(
            domain_board=DOMAIN_BOARD,
            slug=self._thread._board.slug,
            thread_id=self._thread.id,
            post_id=self.id)

    def delete(self, password=''):
        pass
