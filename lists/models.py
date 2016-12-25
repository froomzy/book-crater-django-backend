from django.db import models

from lists.constants import NZD, GBP, USD, Currency


class BooksQuerySet(models.QuerySet):
    def with_isbn(self, isbn: str):
        return self.filter(isbn=isbn)

    def price_less_than(self, price: float, currency: Currency):
        if NZD:
            return self.filter(prices__nz_dollars__lte=price)
        elif GBP:
            return self.filter(prices__uk_pounds__lte=price)
        elif USD:
            return self.filter(prices__usd__lte=price)
        else:
            raise ValueError('Currency {currency} not supported'.format(currency=currency))


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
            NZD: self.set_nzd_price
        }.get(currency)(price, cost)

    def set_nzd_price(self, price: 'Prices', cost: float):
        price.nz_dollars = cost
        price.save()
        return price


class Prices(models.Model):
    book = models.OneToOneField(to='lists.Books', on_delete=models.CASCADE, primary_key=True)
    nz_dollars = models.DecimalField(verbose_name='NZ$', max_digits=12, decimal_places=2, blank=True, null=True)
    us_dollars = models.DecimalField(verbose_name='US$', max_digits=12, decimal_places=2, blank=True, null=True)
    uk_pounds = models.DecimalField(verbose_name='UK£', max_digits=12, decimal_places=2, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'prices'

    objects = PricesManager.from_queryset(PricesQuerySet)()

    def __str__(self):
        return 'Prices for {book}'.format(book=self.book)
