from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MaxValueValidator
from django.db import models

from lib.token_utils import BaseTokenManager, AuthenticationError, CONST


class User(models.Model):
    REQUIRED_FIELDS = ('User',)

    class UserType(models.IntegerChoices):
        SUPERUSER = 0
        RESTAURANT = 1
        COSTUMER = 2

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[UnicodeUsernameValidator()],
        error_messages={
            'unique': 'Username unique.'
        },
        verbose_name='username'
    )
    email = models.EmailField(unique=True, verbose_name='email')

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def get_full_name(self):
        """
        Concatenate the first name and second name with a space in between.
        """
        return ('%s %s' % (self.first_name, self.last_name)).strip()

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
                                verbose_name='user')
    date_created = models.DateTimeField(auto_now_add=True, verbose_name='date created')

    # token information
    digest = models.CharField(max_length=CONST.DIGEST_LENGTH, unique=True)
    key = models.CharField(max_length=CONST.TOKEN_KEY_LENGTH, db_index=True)
    salt = models.CharField(max_length=CONST.SALT_LENGTH, unique=True)

    objects = PasswordTokenManager()

    class Meta:
        verbose_name = 'password token'
        verbose_name_plural = 'password tokens'

    def __str__(self):
        return "token: %s, user: %s" % (self.key, self.user)
