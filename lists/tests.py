from django.test import TestCase
from requests import HTTPError

from lists.constants import NZD
from lists.wishlists import process_wishlist, _retrieve_wishlist, _extract_books, _calculate_price


class ProcessListTests(TestCase):

    def test_wishlist_with_one_book(self):
        url = 'http://www.bookdepository.com/wishlists/WF90LH'
        results = process_wishlist(url=url)
        self.assertEqual(['9781408708989'], results)

    def test_wishlist_with_two_books(self):
        url = 'http://www.bookdepository.com/wishlists/WF90L8'
        results = process_wishlist(url=url)
        self.assertEqual(['9781847923677', '9781785041273'], results)

    def test_retrieve_wishlist_fails_on_bad_url(self):
        url = 'http://www.bookdepository.com/wishlists/testmeplease'
        with self.assertRaises(HTTPError):
            _retrieve_wishlist(url=url)

    def test_extract_books_returns_one_book(self):
        url = 'http://www.bookdepository.com/wishlists/WF90LH'
        wishlist_page = _retrieve_wishlist(url=url)
        books = _extract_books(wishlist_page=wishlist_page)
        self.assertEqual(1, len(books))

    def test_extract_books_returns_two_book(self):
        url = 'http://www.bookdepository.com/wishlists/WF90L8'
        wishlist_page = _retrieve_wishlist(url=url)
        books = _extract_books(wishlist_page=wishlist_page)
        self.assertEqual(2, len(books))

    def test_calculate_price_nzd(self):
        price_string = 'NZ$20.95'
        currency, price = _calculate_price(price_string=price_string)
        self.assertEqual(currency, NZD)
        self.assertEqual(price, 20.95)

    def test_calculate_price_nzd_handles_newline(self):
        price_string = '''NZ$20.95
                            NZ$30.32
                        '''
        currency, price = _calculate_price(price_string=price_string)
        self.assertEqual(currency, NZD)
        self.assertEqual(price, 20.95)
