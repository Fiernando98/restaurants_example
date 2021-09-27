from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _
from drf_query_filter import fields
from knox.views import LoginView
from rest_framework import status, viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response


class LoginCustomView(LoginView):
    """
    This only overrides the original View for using the Basic Authentication instead of the
    default one
    """
    authentication_classes = (BasicAuthentication,)
