from django.contrib import admin  # type: ignore

from lists.models import Books, Prices, WishLists, Lists

admin.site.register(Books)
admin.site.register(Prices)
admin.site.register(Lists)
admin.site.register(WishLists)
