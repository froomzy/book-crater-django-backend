from typing import List

from django.core.exceptions import ValidationError
from django.db import models

from core.models import User
from lists.constants import NZD, GBP, USD, Currency, CZK


class BooksQuerySet(models.QuerySet):
    def with_isbn(self, isbn: str):
        return self.filter(isbn=isbn)

    def with_isbn_in(self, isbns: List[str]):
        return self.filter(isbn__in=isbns)

    def price_less_than(self, price: float, currency: Currency):
        return {
            NZD: self.filter(prices__nz_dollars__lt=price),
            GBP: self.filter(prices__uk_pounds__lt=price),
            USD: self.filter(prices__us_dollars__lt=price),
            CZK: self.filter(prices__cz_koruna__lt=price),
        }[currency]

    def price_less_than_or_equal(self, price: float, currency: Currency):
        return {
            NZD: self.filter(prices__nz_dollars__lte=price),
            GBP: self.filter(prices__uk_pounds__lte=price),
            USD: self.filter(prices__us_dollars__lte=price),
            CZK: self.filter(prices__cz_koruna__lte=price),
        }[currency]


class BooksManager(models.Manager):
    def create(self, isbn: str, title: str):
        book = Books()
        book.isbn = isbn
        book.title = title
        book.save()
        prices = Prices.objects.create(book=book)
        book.prices = prices
        book.save()
        book.prices = prices
        return book


class Books(models.Model):
    isbn = models.CharField(primary_key=True, max_length=13, verbose_name='ISBN')
    title = models.CharField(max_length=1000, blank=False, null=False)

    class Meta:
        verbose_name = 'book'
        verbose_name_plural = 'books'

    objects = BooksManager.from_queryset(BooksQuerySet)()

    def __str__(self):
        return '{title} ({isbn})'.format(title=self.title, isbn=self.isbn)


class PricesQuerySet(models.QuerySet):
    pass


class PricesManager(models.Manager):
    def create(self, book: Books):
        price = Prices()
        price.book = book
        price.save()
        return price

    def set_price(self, currency, price, cost):
        {
            NZD: self.set_nzd_price,
            GBP: self.set_gbp_price,
            USD: self.set_usd_price,
            CZK: self.set_czk_price,
        }.get(currency)(price, cost)

    def set_nzd_price(self, price: 'Prices', cost: float):
        price.nz_dollars = cost
        price.save()
        return price

    def set_gbp_price(self, price: 'Prices', cost: float):
        price.uk_pounds = cost
        price.save()
        return price

    def set_usd_price(self, price: 'Prices', cost: float):
        price.us_dollars = cost
        price.save()
        return price

    def set_czk_price(self, price: 'Prices', cost: float):
        price.cz_koruna = cost
        price.save()
        return price


class Prices(models.Model):
    book = models.OneToOneField(to='lists.Books', on_delete=models.CASCADE, primary_key=True)
    nz_dollars = models.DecimalField(verbose_name='NZ$', max_digits=12, decimal_places=2, blank=True, null=True)
    us_dollars = models.DecimalField(verbose_name='US$', max_digits=12, decimal_places=2, blank=True, null=True)
    uk_pounds = models.DecimalField(verbose_name='£', max_digits=12, decimal_places=2, blank=True, null=True)
    cz_koruna = models.DecimalField(verbose_name='Kč', max_digits=12, decimal_places=2, blank=True, null=True)

    class Meta:
        verbose_name = 'price'
        verbose_name_plural = 'prices'

    objects = PricesManager.from_queryset(PricesQuerySet)()

    def __str__(self):
        return 'Prices for {book}'.format(book=self.book)

    def get_price_for_currency(self, currency: Currency) -> float:
        return {
            NZD: self.nz_dollars,
            USD: self.us_dollars,
            GBP: self.uk_pounds,
            CZK: self.cz_koruna,
        }[currency]


def _validate_day_of_month(day_of_month):
    if 0 < day_of_month <= 28:
        return
    raise ValidationError('Day of Month must be between 1 and 28')


class ListsQuerySet(models.QuerySet):
    def for_owner(self, user: User):
        return self.filter(owner=user)


class ListsManager(models.Manager):
    def create(self, title: str, currency: Currency, spend: float, day_of_month: int, owner: User):
        list = Lists()
        list.title = title
        list.currency = currency.abbreviation
        list.spend = spend
        list.day_of_month = day_of_month
        list.owner = owner
        list.save()
        return list


class Lists(models.Model):
    title = models.CharField(max_length=1000, blank=False, null=False)
    currency = models.CharField(max_length=1000, blank=False, null=False)
    spend = models.DecimalField(max_digits=12, decimal_places=2, blank=False, null=False)
    day_of_month = models.IntegerField(validators=[_validate_day_of_month], blank=False, null=False)
    owner = models.ForeignKey(to='core.User')

    class Meta:
        verbose_name = 'list'
        verbose_name_plural = 'lists'

    objects = ListsManager.from_queryset(ListsQuerySet)()

    def __str__(self):
        return 'List {title} belonging to {user}'.format(title=self.title, user=self.owner)


class WishListQuerySet(models.QuerySet):
    def for_list(self, list: Lists):
        return self.filter(list=list)


class WishListManager(models.Manager):
    def create(self, list: Lists, url: str) -> 'WishLists':
        wishlist = WishLists()
        wishlist.list = list
        wishlist.url = url
        wishlist.save()
        return wishlist


class WishLists(models.Model):
    list = models.ForeignKey(to='lists.Lists', related_name='wishlists')
    url = models.URLField(max_length=1000, blank=False, null=False)

    class Meta:
        verbose_name = 'wish list'
        verbose_name_plural = 'wish lists'

    objects = WishListManager.from_queryset(WishListQuerySet)()

    def __str__(self):
        return 'Wishlist at {url}'.format(url=self.url)
