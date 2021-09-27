from django.shortcuts import render
from drf_query_filter import fields
from knox.views import LoginView
from rest_framework import status, viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from apps.users.models import User


class LoginCustomView(LoginView):
    """
    This only overrides the original View for using the Basic Authentication instead of the
    default one
    """
    authentication_classes = (BasicAuthentication,)


class UserViewSet(viewsets.ModelViewSet):
    """
    All related User actions are written here
    """

    ordering_fields = {
        'id': 'id',
        'username': 'username',
    }
    query_params = [
        fields.IntegerField('id') & fields.IntegerField('user', 'id'),
        fields.Field('username', 'username__icontains')
    ]

    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.all()

        # if user.type == User.UserType.RESTAURANT:
        # queryset = queryset.filter(id=user.id)

        return queryset

    @action(detail=False, methods=['post'])
    def unique_validation(self, request):
        """
        This is for checking dynamically the existence of some values
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """
        Change the password of the current logged user
        """
        user = self.request.user
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'])
    def change_email(self, request):
        """
        Change the email address of the current logged user
        """
        user = self.request.user
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        permissions = {
            'unique_validation': (AllowAny,),
            'change_password': (IsAuthenticated,),
            'change_email': (IsAuthenticated,),
            'retrieve': (IsAuthenticated, IsAdmin),
            'partial_update': (IsAuthenticated, IsAdmin),
            'update': (IsAuthenticated, IsAdmin),
        }.get(self.action, (IsAuthenticated, IsAdmin))

        return [permission() for permission in permissions]

    def get_serializer_class(self):
        return {
            'unique_validation': UserCheckSerializer,
            'change_password': ChangePasswordSerializer,
            'change_email': ChangeEmailSerializer,
        }.get(self.action, UserSerializer)  # by default give the UserSerializer
