from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from lib.token_utils import BaseTokenManager, AuthenticationError, CONST


class User(AbstractUser):
    """
    This implements from the AbstractBaseUser so we don't have to get all the fields that we don't
    really care about. This is also based on the AbstractUser
    """

    class UserType(models.IntegerChoices):
        ADMIN = 0
        RESTAURANT = 1
        COSTUMER = 2

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[username_validator],
        verbose_name='username'
    )
    email = models.EmailField(unique=True, verbose_name='email', blank=True)
    type = models.SmallIntegerField(choices=UserType.choices, verbose_name='user type', default=0)

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def get_full_name(self):
        """
        Concatenate the first name and second name with a space in between.
        """
        return ('%s %s' % (self.first_name, self.last_name)).strip()

    def get_short_name(self):
        return self.first_name

    def __str__(self):
        return self.username

    def __repr__(self):
        return self.get_full_name()


class PasswordTokenManager(BaseTokenManager):

    def create(self, user=None):
        assert user, 'User was not given as an argument'

        try:
            instance = self.get(user=user)
            instance.delete()
        except self.model.DoesNotExist:
            pass

        return super(PasswordTokenManager, self).create(user=user)

    def authenticate(self, token):
        instance = super(PasswordTokenManager, self).authenticate(token)
        return instance


class PasswordToken(models.Model):
    """
    Custom Token System for the password
    """
    user = models.OneToOneField(to=User, related_name='password_token', on_delete=models.CASCADE,
                                verbose_name=_('user'))
    date_created = models.DateTimeField(auto_now_add=True, verbose_name=_('date created'))

    # token information
    digest = models.CharField(max_length=CONST.DIGEST_LENGTH, unique=True)
    key = models.CharField(max_length=CONST.TOKEN_KEY_LENGTH, db_index=True)
    salt = models.CharField(max_length=CONST.SALT_LENGTH, unique=True)

    objects = PasswordTokenManager()

    class Meta:
        verbose_name = _('password token')
        verbose_name_plural = _('password tokens')

    def __str__(self):
        return "token: %s, user: %s" % (self.key, self.user)
