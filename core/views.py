from django.contrib.auth import login, logout, authenticate
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_json_api import serializers

from core.models import User


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['email']
        model = User


class UsersViewSet(viewsets.ModelViewSet):
    serializer_class = UsersSerializer
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        user = User.objects.create_user(**serializer.validated_data)

    def update(self, request, *args, **kwargs):
        return Response(data={'error': 'May not update user records'}, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        return Response(data={'error': 'May not update user records'}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        return Response(data={'error': 'May not delete user records'}, status=status.HTTP_400_BAD_REQUEST)


class SessionsSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class SessionsView(APIView):
    permission_classes = (AllowAny,)
    resource_name = 'sessions'
    serializer_class = SessionsSerializer

    def get(self, request, *args, **kwargs):
        if request.user.is_anonymous():
            return Response({'error': 'Session Expired'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        user = authenticate(email=request.POST.get('email'), password=request.POST.get('password'))
        if not user:
            return Response({'error': 'Incorrect email / password combination entered. Please try again.'}, status=status.HTTP_403_FORBIDDEN)
        login(request, user)
        return Response({}, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        logout(request)
        return Response({}, status=status.HTTP_204_NO_CONTENT)
