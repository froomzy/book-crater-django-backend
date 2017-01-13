from rest_framework.authentication import SessionAuthentication  # type: ignore


class CraterSessionAuthentication(SessionAuthentication):
    def authenticate_header(self, request):
        return 'session'
