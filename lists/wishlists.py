import requests
from bs4 import BeautifulSoup
from requests import HTTPError

from lists.constants import NZD
from lists.models import Books, Prices


def _retrieve_wishlist(url: str):
    response = requests.get(url=url)
    # This will raise if there is any 4xx or 5xx status codes
    response.raise_for_status()
    # Need to see if we land on a wishlist page. If not, whinge
    if response.url != url:
        raise HTTPError(
            'Redirected from wishlist to {new_url}. Wishlist probably does not exist'.format(new_url=response.url),
            response=response
        )
    return BeautifulSoup(markup=response.text, features="lxml")


def _extract_books(wishlist_page: BeautifulSoup):
    books = wishlist_page.select('div.book-item')
    return books


def _calculate_price(price_string: str):
    if price_string.startswith('NZ$'):
        currency = NZD
        # numbers = price_string[3:]
        numbers = price_string[3:].splitlines()[0]
        price = float(numbers)
        return currency, price


def _create_book(book: BeautifulSoup):
    isbn = book.select('meta[itemprop="isbn"]')[0]['content']
    title = book.select('div.item-info h3 a')[0].text.strip()
    exiting_books = Books.objects.with_isbn(isbn=isbn)
    if exiting_books:
        new_book = exiting_books.first()
    else:
        new_book = Books.objects.create(isbn=isbn, title=title)
    currency, price = _calculate_price(price_string=book.select('div.item-info div.price-wrap p.price')[0].text.strip())
    Prices.objects.set_price(currency=currency, price=new_book.prices, cost=price)
    return new_book


def process_wishlist(url: str):
    results_list = []
    # Request the page, return a BS4 object of its html
    wishlist_page = _retrieve_wishlist(url=url)
    # Extract book objects from page, return as list
    books = _extract_books(wishlist_page=wishlist_page)
    # Iterate list, create book model from each (with prices??), add isbn to results list
    for book in books:
        new_book = _create_book(book=book)
        results_list.append(new_book.isbn)
    # Return results list
    return results_list
