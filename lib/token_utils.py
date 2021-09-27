import binascii
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from django.db import models
from knox.crypto import sha

try:
    from hmac import compare_digest
except ImportError:
    def compare_digest(a, b):
        return a == b


class CONST:
    TOKEN_CHARACTER_LENGTH = 64
    TOKEN_KEY_LENGTH = 8
    DIGEST_LENGTH = 128
    SALT_LENGTH = 16


def create_token_string():
    return binascii.hexlify(
        os.urandom(int(CONST.TOKEN_CHARACTER_LENGTH / 2))
    ).decode()


def create_salt_string():
    return binascii.hexlify(
        os.urandom(int(CONST.SALT_LENGTH / 2))).decode()


def hash_token(token, salt):
    digest = hashes.Hash(sha(), backend=default_backend())
    digest.update(binascii.unhexlify(token))
    digest.update(binascii.unhexlify(salt))
    return binascii.hexlify(digest.finalize()).decode()


def generate_token_salt_digest():
    token = create_token_string()
    salt = create_salt_string()
    digest = hash_token(token, salt)

    return token, salt, digest


class AuthenticationError(BaseException):
    pass


class BaseTokenManager(models.Manager):
    def create(self, **kwargs):
        token, salt, digest = generate_token_salt_digest()

        instance = super(BaseTokenManager, self).create(
            key=token[:CONST.TOKEN_KEY_LENGTH], digest=digest, salt=salt, **kwargs
        )

        return instance, token

    def authenticate(self, token):
        for instance in self.filter(key=token[:CONST.TOKEN_KEY_LENGTH]):
            try:
                digest = hash_token(token, instance.salt)
            except (TypeError, binascii.Error):
                raise AuthenticationError('Error trying to hash the token')
            if compare_digest(digest, instance.digest):
                return instance
        raise AuthenticationError('Not found')