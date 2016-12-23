import requests
from bs4 import BeautifulSoup
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'Retrieves books from the specified wishlist'

    def add_arguments(self, parser):
        parser.add_argument('wishlist')

    def handle(self, *args, **options):
        # make a request to the given wishlist, getting back it's html
        url = "http://www.bookdepository.com/wishlists/{wishlist}".format(wishlist=options.get('wishlist'))
        response = requests.get(url)
        # parse the html
        soup = BeautifulSoup(response.text, 'html.parser')
        # find all the books, and book links, in the wishlist
        wishlist_items = soup.select('div.book-item')
        # for each book in the list, go and get its details
        for book in wishlist_items:
            title = book.select('div.item-info h3 a')[0].text.strip()
            author = book.select('div.item-info p.author a')[0].text.strip()
            isbn = book.select('meta[itemprop="isbn"]')[0]['content']
            price = book.select('div.item-info div.price-wrap p.price')[0].text.strip()
            link = book.select('div.item-info h3 a')[0]['href']

            self.stdout.write(str(title))
            self.stdout.write(str(author))
            self.stdout.write(str(isbn))
            self.stdout.write(str(price))
            self.stdout.write(str(link))
