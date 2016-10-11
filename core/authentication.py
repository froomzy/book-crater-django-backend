from rest_framework.authentication import SessionAuthentication


class CraterSessionAuthentication(SessionAuthentication):
    def authenticate_header(self, request):
        return 'session'