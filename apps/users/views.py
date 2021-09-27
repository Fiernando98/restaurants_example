from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _
from drf_query_filter import fields
from knox.views import LoginView
from rest_framework import status, viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from django_files.settings import RESET_PASSWORD_URL
from apps.users.filter_fields import UserNamesField
from apps.users.models import User
from apps.users.serializers import (
    ChangeEmailSerializer,
    ChangePasswordSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetEmailSerializer,
    UserCheckSerializer,
    UserSerializer,
    UserUpdateSerializer,
)
from lib.utils import send_mail, raise_non_field_error


class LoginCustomView(LoginView):
    """
    This only overrides the original View for using the Basic Authentication instead of the
    default one
    """
    authentication_classes = (BasicAuthentication,)


class PasswordResetViewSet(viewsets.GenericViewSet):
    """
    Allows the user to request a password reset
    """
    permission_classes = (AllowAny,)

    @action(detail=False, methods=['post'])
    def send_request(self, request):
        """
        Send the password request to the user's email if it exists
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token_instance, token_key = serializer.save()

            template = {'text': get_template('email/password_reset.txt')}
            token_path = RESET_PASSWORD_URL % token_key
            send_mail(template, 'Reseteo de contraseña', [user.email], {'token': token_path})

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'])
    def confirm_request(self, request):
        """
        With the given `password-reset-token` we reset the password of the user
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_class(self):
        return {
            'send_request': PasswordResetEmailSerializer,
            'confirm_request': PasswordResetConfirmSerializer,
        }.get(self.action, None)


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
        fields.Field('username', 'username__icontains') &
        fields.Field('first_name', 'first_name__icontains') &
        fields.Field('last_name', 'last_name__icontains'),
        fields.ExistsField('is_superuser', 'is_superuser', return_value=True),
        UserNamesField('name'),
    ]

    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.all()

        if user.type == User.Types.PRINCIPAL:
            queryset = queryset.filter(id=user.id)

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
            'unique_validation': AllowAny,
            'change_password': IsAuthenticated,
            'change_email': IsAuthenticated,
            'retrieve': IsAuthenticated,
            'partial_update': IsAuthenticated,
            'update': IsAuthenticated,
        }.get(self.action, IsAuthenticated)

        return [permission() for permission in permissions]

    def get_serializer_class(self):
        return {
            'unique_validation': UserCheckSerializer,
            'change_password': ChangePasswordSerializer,
            'change_email': ChangeEmailSerializer,
        }.get(self.action, UserSerializer)  # by default give the UserSerialize
