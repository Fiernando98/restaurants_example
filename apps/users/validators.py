from django.contrib.auth import password_validation
from django.core import exceptions
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator


class UniqueUsernameValidator(UniqueValidator):
    message = 'This username already exists.'


class UniqueEmailValidator(UniqueValidator):
    message = 'This email already exists.'


class TokenPasswordValidator(object):
    message_expire = 'Token expired.'
    message_not_found = 'Invalid token.'

    def __init__(self, queryset):
        self.qs = queryset

    def __call__(self, value):
        try:
            token = self.qs.get(key=value)
            # check if it is still valid
            if token.expire():
                raise ValidationError(self.message_expire, code='expire')
        except exceptions.ObjectDoesNotExist:
            raise ValidationError(self.message_not_found, code='not_found')


class PasswordStrengthValidator(object):
    def __init__(self, user=None):
        self.user = user

    def __call__(self, value):
        password_validation.validate_password(password=value, user=self.user)
