from decimal import Decimal

from lists.constants import CURRENCIES
from lists.models import Lists, Books
from typing import List

from lists.wishlists import process_wishlist


def generate_purchase_list(list: Lists) -> List[Books]:
    wishlists = list.wishlists.all()
    available_spend = Decimal(list.spend)
    currency = CURRENCIES[list.currency]
    selected_books = []
    isbns = []
    for wishlist in wishlists:
        isbns += process_wishlist(url=wishlist.url, currency=currency)
    isbns = set(isbns)
    while True:
        books = set(Books.objects.with_isbn_in(isbns=isbns).price_less_than(price=available_spend, currency=currency))
        if len(books) == 0:
            break
        book = books.pop()
        selected_books.append(book)
        isbns.remove(book.isbn)
        available_spend -= book.prices.get_price_for_currency(currency=currency)
    return selected_books
