from decimal import Decimal, Context

from django.template import Context as TemplateContext

from django.template.loader import get_template

from core.emails import send_email
from core.models import User
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


def _create_context(list: Lists, books: List[Books], user: User) -> TemplateContext:
    processed_books = []
    currency = CURRENCIES[list.currency]
    for book in books:
        new_book = {}
        new_book['title'] = book.title
        new_book['isbn'] = book.isbn
        print(currency.string_format, book.prices.get_price_for_currency(currency=currency))
        new_book['price'] = currency.string_format.format(price=book.prices.get_price_for_currency(currency=currency))
        new_book['image'] = 'https://d1w7fb2mkkr3kw.cloudfront.net/assets/images/book/mid/{first}/{second}/{isbn}.jpg'.format(
            first=book.isbn[0:4],
            second=book.isbn[4:8],
            isbn=book.isbn
        )
        processed_books.append(new_book)

    context = TemplateContext({
        'books': processed_books,
        'user': user,
        'list': list,
    })
    return context

def _generate_text_content(context: TemplateContext):
    template = get_template('purchase-list-email.txt')
    rendered = template.render(context=context)
    return rendered


def _generate_html_content(context: TemplateContext):
    template = get_template('purchase-list-email.html')
    rendered = template.render(context=context)
    return rendered


def send_purchase_list_email(list: Lists, books: List[Books], user: User):
    context = _create_context(list=list, books=books, user=user)
    recipients = [user.email]
    subject = 'Monthly Purchase List From Book Crater'
    text_content = _generate_text_content(context=context)
    html_content = _generate_html_content(context=context)

    send_email(subject=subject, recipients=recipients, text_content=text_content, html_content=html_content)
