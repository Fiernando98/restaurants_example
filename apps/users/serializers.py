import datetime

from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_text
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_decode as uid_decoder
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.users.models import User, PasswordToken
from apps.users.validators import UniqueEmailValidator, PasswordStrengthValidator, UniqueUsernameValidator
from lib.token_utils import AuthenticationError


class UserBaseSerializer(serializers.ModelSerializer):
    extra_kwargs = {
        'id': {'read_only': True},
        'username': {
            'read_only': True,
            'validators': (UniqueUsernameValidator(User.objects.all()),)
        },
        'email': {'required': True},
        'password': {
            'required': False,
            'write_only': True,
            'validators': (PasswordStrengthValidator(),)
        },
    }

    def __init__(self, *args, **kwargs):
        setattr(self.Meta, 'extra_kwargs', self.extra_kwargs)
        super().__init__(*args, **kwargs)

    class Meta:
        model = User


class UserSerializer(UserBaseSerializer):

    def create(self, validated_data):
        model = self.Meta.model
        return model.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        assert True, ('`%s` cannot perform an update action.' % self.__class__.__name__)


class UserForStaffSerializer(UserSerializer):
    extra_kwargs = {
        'id': {'read_only': True},
        'username': {
            'read_only': True,
            'validators': (UniqueUsernameValidator(User.objects.all()),)
        },
        'email': {'required': True},
        'password': {
            'required': False,
            'write_only': True,
            'validators': (PasswordStrengthValidator(),)
        },
    }

    def create(self, validated_data):
        model = self.Meta.model
        return model.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        assert True, ('`%s` cannot perform an update action.' % self.__class__.__name__)


class UserUpdateSerializer(UserBaseSerializer):
    extra_kwargs = {
        'id': {'read_only': True},
        'username': {'read_only': True},
        'email': {'required': False},
        'password': {
            'required': False,
            'write_only': True,
            'validators': (PasswordStrengthValidator(),),
        }
    }

    def update(self, instance: User, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

    def create(self, validated_data):
        assert True, ('`%s` cannot perform an update action.' % self.__class__.__name__)


class UserCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')
        qs = model.objects.all()
        extra_kwargs = {
            'username': {
                'required': False,
                'validators': [UniqueUsernameValidator(queryset=qs)]
            },
            'email': {
                'required': False,
                'validators': [UniqueEmailValidator(queryset=qs)]
            },
        }

        def update(self, instance, validated_data):
            assert True, ('`%s` cannot perform an update action.' % self.__class__.__name__)

        def create(self, validated_data):
            assert True, ('`%s` cannot perform a create action.' % self.__class__.__name__)


class PasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = '__all__'

    def validate(self, attrs):
        model = self.Meta.model
        email = attrs['email']
        try:
            user = model.objects.get(email=email)
        except model.DoesNotExist:
            msg = 'Email `%s` is not in use' % email
            raise serializers.ValidationError(msg, 'not_found')
        attrs['user'] = user
        return attrs

    def update(self, instance, validated_data):
        assert True, ('`%s` cannot perform an update action.' % self.__class__.__name__)

    def create(self, validated_data):
        """Create a Token for this action"""
        return PasswordToken.objects.create(user=validated_data['user'])


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=128, required=True)
    new_password = serializers.CharField(
        trim_whitespace=False,
        required=True,
        write_only=True,
        validators=[PasswordStrengthValidator(User)]
    )

    class Meta:
        model = PasswordToken
        fields = ('token', 'new_password')

    def validate(self, attrs):
        model = self.Meta.model

        try:
            token = model.objects.authenticate(token=attrs['token'])
        except AuthenticationError:
            raise serializers.ValidationError('Token invalido', 'invalid_token')

        self.instance = token.user
        token.delete()  # immediately destroy it
        return attrs

    def update(self, instance, validated_data):
        # update the value of the password in said user
        instance.set_password(validated_data['new_password'])
        instance.save()

        return instance

    def create(self, validated_data):
        assert True, ('`%s` cannot perform a create action.' % self.__class__.__name__)


class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(
        trim_whitespace=False,
        required=True,
        write_only=True,
    )
    new_password = serializers.CharField(
        trim_whitespace=False,
        required=True,
        write_only=True,
        validators=[PasswordStrengthValidator(User)]
    )

    class Meta:
        model = User
        fields = ('old_password', 'new_password')

    def validate_old_password(self, value):
        if not self.instance:
            raise Exception('No instance was given to the serializer')

        if not self.instance.check_password(value):
            msg = 'Contraseña invalida'
            raise serializers.ValidationError(msg, 'invalid')

        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance

    def create(self, validated_data):
        assert True, ('`%s` cannot perform a create action.' % self.__class__.__name__)


class ChangeEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email',)
        extra_kwargs = {
            'email': {
                'validators': [UniqueEmailValidator(queryset=model.objects.all())]
            }
        }

    def create(self, validated_data):
        assert True, ('`%s` cannot perform a create action.' % self.__class__.__name__)


class PasswordSetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password_reset_form_class = PasswordResetForm

    def get_email_options(self):
        return {}

    def validate_email(self, value):
        self.reset_form = self.password_reset_form_class(data=self.initial_data)
        if not self.reset_form.is_valid():
            raise serializers.ValidationError(self.reset_form.errors)
        return value

    def save(self, request):
        opts = {
            'use_https': request.is_secure(),
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
            'subject_template_name': 'subject_set_email.txt',
            'email_template_name': strip_tags('password_set_email.html'),
            'html_email_template_name': 'password_set_email.html',
            'request': request,
        }

        opts.update(self.get_email_options())
        self.reset_form.save(**opts)


class PasswordSetConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=128)
    uid = serializers.CharField()
    token = serializers.CharField()

    set_password_form_class = SetPasswordForm

    def custom_validation(self, attrs):
        pass

    def validate(self, attrs):
        self._errors = {}
        try:
            uid = force_text(uid_decoder(attrs['uid']))
            self.user = User._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise ValidationError({'uid': ['Valor inválido']})

        self.custom_validation(attrs)
        self.set_password_form = self.set_password_form_class(
            user=self.user, data=attrs
        )
        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)
        if not default_token_generator.check_token(self.user, attrs['token']):
            raise ValidationError({'token': ['Valor inválido']})

        return attrs

    def save(self):
        return self.set_password_form.save()
