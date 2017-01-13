from django.contrib import admin # type: ignore

from core.models import User, UserProfile

admin.site.register(User)
admin.site.register(UserProfile)
