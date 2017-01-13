from django.conf.urls import url
from rest_framework.routers import DefaultRouter  # type: ignore

from core.views import UsersViewSet, SessionsView

router = DefaultRouter()
router.register(r'users', UsersViewSet,)

urlpatterns = [
    url(r'sessions/', SessionsView.as_view())
]

urlpatterns += router.urls
