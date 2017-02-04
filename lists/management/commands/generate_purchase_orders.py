from django.core.management import BaseCommand

from lists.lists import generate_purchase_list, send_purchase_list_email
from lists.models import Lists


class Command(BaseCommand):

    def handle(self, *args, **options):
        for list in Lists.objects.all().iterator():
            books = generate_purchase_list(list=list)
            send_purchase_list_email(list=list, books=books, user=list.owner)
