import json
from pathlib import Path
from time import sleep

import requests
from bs4 import BeautifulSoup
from django.core import mail
from django.core.exceptions import ValidationError
from django.template import Context
from django.template.loader import get_template
from django.test import TestCase
from requests import HTTPError

from core.emails import send_email
from core.models import User
from lists.constants import NZD, GBP, CZK, USD
from lists.lists import generate_purchase_list, send_purchase_list_email
from lists.models import _validate_day_of_month, Lists, WishLists, Books, Prices
from lists.wishlists import process_wishlist, _retrieve_wishlist, _extract_books, _calculate_price

one_hundred_books_isbns = [
    '9780141361796',
    '9781473613492',
    '9781771642484',
    '9781784161071',
    '9780241232422',
    '9780141036137',
    '9780330463362',
    '9780718184452',
    '9780751557411',
    '9781408845653',
    '9781786482242',
    '9781856753531',
    '9780996099936',
    '9780241282588',
    '9781447274452',
    '9781612680019',
    '9781760340834',
    '9780006514008',
    '9780008164614',
    '9780062641540',
    '9780307719775',
    '9780716023715',
    '9780718184353',
    '9780761169086',
    '9781845290764',
    '9781408856772',
    '9780007158522',
    '9780552574235',
    '9781783782666',
    '9781910701881',
    '9780330463393',
    '9780753545669',
    '9781405284868',
    '9780091955106',
    '9780718184339',
    '9780141373010',
    '9780593077566',
    '9780723281481',
    '9781409313298',
    '9781409549475',
    '9781846276033',
    '9780718184261',
    '9780753557525',
    '9781847398789',
    '9780099549482',
    '9780241253052',
    '9780008221096',
    '9781406366990',
    '9781595620156',
    '9780330463317',
    '9781447294832',
    '9781784298463',
    '9780716021919',
    '9780753820162',
    '9780718183653',
    '9781472152756',
    '9781786482228',
    '9780349134284',
    '9781449474195',
    '9781471157790',
    '9781841215655',
    '9780747599876',
    '9781416947370',
    '9781786482266',
    '9781843446361',
    '9781853261589',
    '9780340733509',
    '9780008125417',
    '9780807014295',
    '9780718184377',
    '9781594746031',
    '9780007513765',
    '9781942993889',
    '9781786070173',
    '9780718185541',
    '9780241003008',
    '9780718184216',
    '9781784701994',
    '9780753545683',
    '9781862059580',
    '9780552779777',
    '9780008138301',
    '9780141033570',
    '9781527203341',
    '9781439199190',
    '9781786070159',
    '9781786330444',
    '9780099590088',
    '9781910192146',
    '9780593076446',
    '9781847923677',
    '9780141340555',
    '9780718184308',
    '9780241283912',
    '9781786483843',
    '9781785041273',
    '9780751565355',
    '9780730324218',
    '9781449474256',
    '9781408708989'
]


class ProcessListTests(TestCase):
    def test_wishlist_with_one_book(self):
        url = 'http://www.bookdepository.com/wishlists/WF90LH'
        results = process_wishlist(url=url, currency=NZD)
        self.assertEqual(1, len(results))
        self.assertEqual(['9781408708989'], results)

    def test_wishlist_with_two_books(self):
        url = 'http://www.bookdepository.com/wishlists/WF90L8'
        results = process_wishlist(url=url, currency=NZD)
        self.assertEqual(2, len(results))
        self.assertEqual(['9781847923677', '9781785041273'], results)

    def test_wishlist_with_two_books_using_czk(self):
        url = 'http://www.bookdepository.com/wishlists/WF90L8'
        results = process_wishlist(url=url, currency=CZK)
        self.assertEqual(2, len(results))
        self.assertEqual(['9781847923677', '9781785041273'], results)

    def test_wishlist_with_100_books(self):
        url = 'http://www.bookdepository.com/wishlists/WF9V76'
        results = process_wishlist(url=url, currency=NZD)
        self.assertEqual(100, len(results))
        self.assertEqual(one_hundred_books_isbns, results)

    def test_wishlist_that_doesnt_exist(self):
        url = 'http://www.bookdepository.com/wishlists/idontexist'
        results = process_wishlist(url=url, currency=NZD)
        self.assertEqual([], results)

    def test_retrieve_wishlist_fails_on_bad_url(self):
        url = 'http://www.bookdepository.com/wishlists/testmeplease'
        with self.assertRaises(HTTPError):
            _retrieve_wishlist(url=url, currency=NZD)

    def test_extract_books_returns_one_book(self):
        url = 'http://www.bookdepository.com/wishlists/WF90LH'
        wishlist_page = _retrieve_wishlist(url=url, currency=NZD)
        books = _extract_books(wishlist_pages=wishlist_page)
        self.assertEqual(1, len(books))

    def test_extract_books_returns_two_book(self):
        url = 'http://www.bookdepository.com/wishlists/WF90L8'
        wishlist_page = _retrieve_wishlist(url=url, currency=NZD)
        books = _extract_books(wishlist_pages=wishlist_page)
        self.assertEqual(2, len(books))

    def test_calculate_price_nzd(self):
        price_string = 'NZ$20.95'
        price = _calculate_price(price_string=price_string, currency=NZD)
        self.assertEqual(price, 20.95)

    def test_calculate_price_nzd_handles_newline(self):
        price_string = '''NZ$20.95
                            NZ$30.32
                        '''
        price = _calculate_price(price_string=price_string, currency=NZD)
        self.assertEqual(price, 20.95)

    def test_calculate_price_gbp(self):
        price_string = '£13.76'
        price = _calculate_price(price_string=price_string, currency=GBP)
        self.assertEqual(price, 13.76)

    def test_calculate_price_gbp_handles_newline(self):
        price_string = '''£14.01
                            £14.99
                        '''
        price = _calculate_price(price_string=price_string, currency=GBP)
        self.assertEqual(price, 14.01)

    def test_calculate_price_czk(self):
        price_string = '438,45 Kč'
        price = _calculate_price(price_string=price_string, currency=CZK)
        self.assertEqual(price, 438.45)

    def test_calculate_price_czk_handles_newline(self):
        price_string = '''446,41 Kč
                            477,64 Kč
                        '''
        price = _calculate_price(price_string=price_string, currency=CZK)
        self.assertEqual(price, 446.41)

    def test_calculate_price_usd(self):
        price_string = 'US$16.96'
        price = _calculate_price(price_string=price_string, currency=USD)
        self.assertEqual(price, 16.96)

    def test_calculate_price_usd_handles_newline(self):
        price_string = '''US$17.27
                            US$18.48
                        '''
        price = _calculate_price(price_string=price_string, currency=USD)
        self.assertEqual(price, 17.27)


class ListsTests(TestCase):
    def test_validate_day_of_month(self):
        to_small = -100
        to_big = 100
        min = 1
        min_minus_one = 0
        max = 28
        max_plus_one = 29
        self.assertIsNone(_validate_day_of_month(day_of_month=min))
        self.assertIsNone(_validate_day_of_month(day_of_month=max))
        with self.assertRaises(ValidationError):
            _validate_day_of_month(day_of_month=min_minus_one)
        with self.assertRaises(ValidationError):
            _validate_day_of_month(day_of_month=max_plus_one)
        with self.assertRaises(ValidationError):
            _validate_day_of_month(day_of_month=to_big)
        with self.assertRaises(ValidationError):
            _validate_day_of_month(day_of_month=to_small)


class PurchaseListTests(TestCase):
    def test_list_with_one_book_returns_that_book(self):
        user = User.objects.create_user(email='user@userville.com', password='Nope')
        list = Lists.objects.create(title='Simple Test', owner=user, currency=NZD, spend=50.00, day_of_month=5)
        wishlist = WishLists.objects.create(url='http://www.bookdepository.com/wishlists/WF90LH', list=list)
        results = generate_purchase_list(list=list)
        self.assertEqual(1, len(results))
        self.assertEqual('9781408708989', results[0].isbn)

    def test_list_with_one_book_returns_no_books(self):
        user = User.objects.create_user(email='user@userville.com', password='Nope')
        list = Lists.objects.create(title='Simple Test', owner=user, currency=NZD, spend=5.00, day_of_month=5)
        wishlist = WishLists.objects.create(url='http://www.bookdepository.com/wishlists/WF90LH', list=list)
        results = generate_purchase_list(list=list)
        self.assertEqual(0, len(results))

    def test_list_with_three_books_two_under_returns_those_two_books(self):
        user = User.objects.create_user(email='user@userville.com', password='Nope')
        list = Lists.objects.create(title='Simple Test', owner=user, currency=NZD, spend=18.00, day_of_month=5)
        wishlist = WishLists.objects.create(url='http://www.bookdepository.com/wishlists/WF9YR0', list=list)
        results = generate_purchase_list(list=list)
        self.assertEqual(2, len(results))
        self.assertCountEqual(['9780241003008', '9781853261589'], [book.isbn for book in results])

    def test_list_with_three_books_two_under_returns_one_book(self):
        user = User.objects.create_user(email='user@userville.com', password='Nope')
        list = Lists.objects.create(title='Simple Test', owner=user, currency=NZD, spend=10.00, day_of_month=5)
        wishlist = WishLists.objects.create(url='http://www.bookdepository.com/wishlists/WF9YR0', list=list)
        results = generate_purchase_list(list=list)
        self.assertEqual(1, len(results))
        self.assertIn(results[0].isbn, ['9780241003008', '9781853261589'])

    def test_list_with_two_wishlists_two_under_returns_one_both(self):
        user = User.objects.create_user(email='user@userville.com', password='Nope')
        list = Lists.objects.create(title='Simple Test', owner=user, currency=NZD, spend=16.00, day_of_month=5)
        wishlist = WishLists.objects.create(url='http://www.bookdepository.com/wishlists/WF9Y9R', list=list)
        wishlist = WishLists.objects.create(url='http://www.bookdepository.com/wishlists/WF9Y96', list=list)
        results = generate_purchase_list(list=list)
        self.assertEqual(2, len(results))
        self.assertCountEqual(['9780241003008', '9781853261589'], [book.isbn for book in results])

    def test_list_with_two_wishlists_with_duplicate_books_returns_one_book(self):
        user = User.objects.create_user(email='user@userville.com', password='Nope')
        list = Lists.objects.create(title='Simple Test', owner=user, currency=NZD, spend=80.00, day_of_month=5)
        wishlist = WishLists.objects.create(url='http://www.bookdepository.com/wishlists/WF90LH', list=list)
        wishlist = WishLists.objects.create(url='http://www.bookdepository.com/wishlists/WF90LH', list=list)
        results = generate_purchase_list(list=list)
        self.assertEqual(1, len(results))
        self.assertEqual('9781408708989', results[0].isbn)


class PurchaseListEmailTests(TestCase):
    def get_emails(self):
        url = 'http://localhost:1080/email'
        response = requests.get(url=url)
        return json.loads(response.text)

    def delete_emails(self):
        url = 'http://localhost:1080/email/all'
        response = requests.delete(url=url)

    def test_can_send_email(self):
        subject = 'Hello'
        text_content = 'This is an email!'
        recipients = ['dylan@dylan.com']
        self.delete_emails()
        send_email(subject=subject, recipients=recipients, text_content=text_content)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, subject)
        self.assertEqual(mail.outbox[0].body, text_content)
        self.assertEqual(mail.outbox[0].to, recipients)

    def test_can_send_email_with_alternatives(self):
        subject = 'Hello'
        text_content = 'This is an email!'
        html_content = '<p>This is an email!</p>'
        recipients = ['dylan@dylan.com']
        self.delete_emails()
        send_email(subject=subject, recipients=recipients, text_content=text_content, html_content=html_content)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, subject)
        self.assertEqual(mail.outbox[0].body, text_content)
        self.assertEqual(mail.outbox[0].to, recipients)
        self.assertEqual(mail.outbox[0].alternatives[0][0], html_content)
        self.assertEqual(mail.outbox[0].alternatives[0][1], 'text/html')

    def test_send_email_with_template_content(self):
        subject = 'Template Email'
        text_content = 'There is no text'

        template = get_template('emails/email-base.html')
        context = Context()
        rendered = template.render(context=context)

        html_content = rendered
        recipients = ['dylan@dylan.com']
        self.delete_emails()
        send_email(subject=subject, recipients=recipients, text_content=text_content, html_content=html_content)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, subject)
        self.assertEqual(mail.outbox[0].body, text_content)
        self.assertEqual(mail.outbox[0].to, recipients)
        self.assertEqual(mail.outbox[0].alternatives[0][0], html_content)
        self.assertEqual(mail.outbox[0].alternatives[0][1], 'text/html')

    def test_send_purchase_list_email_sends_right_number_of_books(self):
        self.maxDiff = None
        user = User.objects.create_user(email='user@userville.com', password='Nope')
        list = Lists.objects.create(title='Simple Test', owner=user, currency=NZD, spend=80.00, day_of_month=5)
        books = []
        book = Books.objects.create(isbn='1234567890123', title='Title')
        Prices.objects.set_nzd_price(price=book.prices, cost=10.00)
        books.append(book)
        book = Books.objects.create(isbn='0234567890023', title='Title 2')
        Prices.objects.set_nzd_price(price=book.prices, cost=20.00)
        books.append(book)
        send_purchase_list_email(list=list, books=books, user=user)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Monthly Purchase List From Book Crater')
        txt_path = Path(__file__).parent / 'test-text-generation-content.txt'
        with txt_path.open() as txt:
            self.assertEqual(txt.read(), mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].to, [user.email])
        self.assertEqual(mail.outbox[0].alternatives[0][1], 'text/html')
        soup = BeautifulSoup(mail.outbox[0].alternatives[0][0], 'lxml')
        self.assertEqual(2, len(soup.select('.book-item')))

    def test_send_purchase_list_email_no_books_(self):
        self.maxDiff = None
        user = User.objects.create_user(email='user@userville.com', password='Nope')
        list = Lists.objects.create(title='Simple Test', owner=user, currency=NZD, spend=80.00, day_of_month=5)
        wishlist = WishLists.objects.create(list=list, url='http://www.bookdepository.com/wishlists/WF9V76')
        books = []
        send_purchase_list_email(list=list, books=books, user=user)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Monthly Purchase List From Book Crater')
        txt_path = Path(__file__).parent / 'test-text-generation-content-no-books.txt'
        with txt_path.open() as txt:
            self.assertEqual(txt.read(), mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].to, [user.email])
        self.assertEqual(mail.outbox[0].alternatives[0][1], 'text/html')
        soup = BeautifulSoup(mail.outbox[0].alternatives[0][0], 'lxml')
        self.assertEqual(0, len(soup.select('.book-item')))
