from typing import List, Tuple

import requests
from bs4 import BeautifulSoup
from requests import HTTPError

from lists.constants import NZD, Currency, GBP, CZK
from lists.models import Books, Prices


def _set_currency(url: str, currency: Currency, session: requests.Session):
    session.post(url=url, data={'selectCurrency': currency.abbreviation})


def _retrieve_page(url: str, session: requests.Session) -> BeautifulSoup:
    response = session.get(url=url)
    # This will raise if there is any 4xx or 5xx status codes
    response.raise_for_status()
    # Need to see if we land on a wishlist page. If not, whinge
    if response.url != url:
        raise HTTPError(
            'Redirected from wishlist to {new_url}. Wishlist probably does not exist'.format(new_url=response.url),
            response=response
        )
    return BeautifulSoup(markup=response.text, features="lxml")


def _retrieve_wishlist(url: str, currency: Currency) -> List[BeautifulSoup]:
    session = requests.Session()
    pages = []
    next_url = url
    _set_currency(url=url, currency=currency, session=session)
    while True:
        page = _retrieve_page(url=next_url, session=session)
        next = page.select('ul.pagination > li.next > a')
        pages.append(page)
        if not next:
            break
        next_url = next[0]['href']
    return pages


def _extract_books(wishlist_pages: List[BeautifulSoup]) -> List[BeautifulSoup]:
    books = []
    for page in wishlist_pages:
        books += page.select('div.book-item')
    return books


def _calculate_price(price_string: str, currency: Currency) -> float:
    price_string = price_string.splitlines()[0].replace(',', '.')
    numbers = price_string[currency.string_slice]
    return float(numbers)

def _create_book(book: BeautifulSoup, currency: Currency) -> Books:
    """Create a Books from html."""
    isbn = book.select('meta[itemprop="isbn"]')[0]['content']
    title = book.select('div.item-info h3 a')[0].text.strip()
    exiting_books = Books.objects.with_isbn(isbn=isbn)
    if exiting_books:
        new_book = exiting_books.first()
    else:
        new_book = Books.objects.create(isbn=isbn, title=title)
    print(book)
    prices = book.select('div.item-info div.price-wrap p.price')
    price = 0
    if prices:
        price = _calculate_price(price_string=prices[0].text.strip(), currency=currency)
    Prices.objects.set_price(currency=currency, price=new_book.prices, cost=price)
    return new_book


def process_wishlist(url: str, currency: Currency) -> List[str]:
    """Given a url to a Wishlist, return a list of ISBNs in that wishlist."""
    results_list = []
    try:
        wishlist_page = _retrieve_wishlist(url=url, currency=currency)
    except HTTPError:
        # TODO (Dylan): Need to log out here
        return []
    books = _extract_books(wishlist_pages=wishlist_page)
    for book in books:
        new_book = _create_book(book=book, currency=currency)
        results_list.append(new_book.isbn)
    return results_list
