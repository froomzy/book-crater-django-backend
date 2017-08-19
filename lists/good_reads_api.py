from queue import Queue
from time import sleep

import requests
from bs4 import BeautifulSoup
from lxml import etree
from typing import Tuple, Dict, Any, List

from __config.settings.base import GOODREADS_API_KEY
from lists.models import Books

works_cache = {}
series_cache = {}
book_cache = {}
isbn_cache = {}


class BookCacheItem:
    def __init__(self):
        self.isbns = []
        self.work_id = None
        self.book_id = None
        self.title = None
        self.series_position = None
        self.series = None
        self.series_title = None

    def __str__(self):
        if self.series_position:
            return '{title} ({series_title} #{position})'.format(
                title=self.title,
                series_title=self.series_title,
                position=self.series_position
            )
        return '{title} ({series_title})'.format(
            title=self.title,
            series_title=self.series_title,
        )


def goodreads_search(query: str) -> List[int]:
    url = 'https://www.goodreads.com/search/index.xml?key={api_key}&q={query}'.format(
        api_key=GOODREADS_API_KEY,
        query=query
    )
    response = requests.get(url=url)
    root = etree.fromstring(bytes(response.text, 'utf-8'))
    # TODO (Dylan): Handle the case when there is no results. Will it behave differently?
    work_ids = []
    works = root.findall('search/results/work')
    for work in works:
        work_id = int(work.find('id').text)
        work_ids.append(work_id)
    print(work_ids)
    return work_ids


def goodreads_series_work(work_id: int) -> List[Dict[str, Any]]:
    url = 'https://www.goodreads.com/work/{work_id}/series?format=xml&key={api_key}'.format(
        api_key=GOODREADS_API_KEY,
        work_id=work_id
    )
    response = requests.get(url=url)
    root = etree.fromstring(bytes(response.text, 'utf-8'))
    series = root.findall('series_works/series_work/series')
    new_requests = []
    for item in series:
        series_id = int(item.find('id').text)
        request = request_factory('series.show', series_id=series_id)
        new_requests.append(request)
    print(new_requests)
    return new_requests


def goodreads_series_show(series_id: int) -> List[Dict[str, Any]]:
    # TODO (Dylan): Figure out what it is that I need to return here
    url = 'https://www.goodreads.com/series/{series}?format=xml&key={api_key}'.format(
        series=series_id,
        api_key=GOODREADS_API_KEY
    )
    response = requests.get(url=url)

    soup = BeautifulSoup(response.text, 'lxml-xml')
    # print(soup.prettify())
    series_title = soup.series.title.string.strip()

    series = [soup.find_all('series_work')[-1]]
    for work in series:
        print(work.prettify())
        work_id = int(work.id.string)
        book_id = int(work.best_book.id.string)
        if book_cache.get(book_id):
            continue
        book = BookCacheItem()
        book.book_id = book_id
        book.work_id = work_id
        book.series_title = series_title
        try:
            book.series_position = int(work.user_position.string)
        except ValueError:
            try:
                book.series_position = float(work.user_position.string)
            except ValueError:
                book.series_position = None
        except TypeError:
            book.series_position = None
        title = work.work.original_title.string
        if not title:
            title = work.best_book.title.string
        if title:
            book.title = title.strip()

        print(book)

        # TODO (Dylan): Need to make this so that it will kick off the getting of the book so we can has the ISBNs


        # print(work.work.original_title.string)
        # print(work.user_position.string)
        # break

    # root = etree.fromstring(bytes(response.text, 'utf-8'))
    print('Trying to get series info for series id {id}'.format(id=series_id))
    return []


def goodreads_book_show(book_id: int) -> List[Dict[str, Any]]:
    return []


def request_factory(type: str, **kwargs) -> Dict[Any, Any]:
    request = {
        'type': type,
    }
    request.update(kwargs)
    return request


# NOTE (Dylan): These are all the calls to the GoodReads API that are allowed.
GOODREADS_CALLS = {
    'search': goodreads_search,
    'series.work': goodreads_series_work,
    'series.show': goodreads_series_show,
    'book.show': goodreads_book_show,
}


class GoodReadsApi:
    """Access the GoodReads API
    
    This class manages access to the GoodReads API. There is rate limiting that stops
    me from doing more than one request per second. To overcome that we want to do two
    things: queue requests so that any follow up requests can be handle in order to get
    information, and cache any results that we get, in case we try to get them again."""

    def __init__(self):
        # TODO (Dylan): Look to see what defaultdict might do for me here
        self._local_cache = {}
        self._local_cache['series'] = {}
        self._request_queue = Queue()

    def get_books_series(self, book: Books) -> Tuple[str, int]:
        """Return the series name and volume number.
        
        We need to get the series name and volume for a book. First we should look in out
        local cache to make sure that we don't have it already. If we do, return that. If
        not, then lets go talk to GoodReads and get the details. When we get the details
        for one book then we are likely to get the details for all the other books in the 
        series, so lets cache all that, in case we ask for any of those books as well.
        
        How to find a book's series and it's position:
        - search for the books isbn to get it's work_id (this could also be done in two steps with other calls)
        - for the work id returned do a call to series.work to find all series the book is in
        - for each series id returned do a call to series.show to get all the details about books in that series
        """

        details = self._local_cache['series'].get(book.isbn)
        if details:
            return details

        work_ids = goodreads_search(query=book.isbn)
        for work_id in work_ids:
            request = request_factory('series.work', work_id=work_id)
            self._request_queue.put(item=request)

        while not self._request_queue.empty():
            request = self._request_queue.get()
            self._process_request(request=request)

        details = self._local_cache['series'].get(book.isbn)
        if details:
            return details
        return None, None

    def _process_request(self, request: Dict[Any, Any]) -> None:
        # Make the call to GoodReads
        request_type = request['type']
        del request['type']
        requests = GOODREADS_CALLS.get(request_type)(**request)
        for request in requests:
            self._request_queue.put(request)
        sleep(1)
