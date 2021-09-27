import re
from datetime import datetime
from typing import List

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from rest_framework.exceptions import ValidationError


def send_mail(templates: dict, subject: str, to: List[str], context: dict = None) -> None:
    """
    Utility function. It just create an email response with the given templates and information.
    :param templates: Dictionary containing text and html templates for then email
    :param subject: The Subject of the mail
    :param to: The email target
    :param context: Information for the context
    """

    return

    _context = {'date': datetime.today()}

    # If the target is only one then give the email address in the context
    if len(to) == 1 and 'email' not in _context:
        _context['email'] = to[0]

    if context:
        _context.update(context)

    text_content = templates['text'].render(_context)

    email = EmailMultiAlternatives(subject=subject, body=text_content, to=to)
    if templates.get('html', None):
        html_content = templates['html'].render(_context)
        email.attach_alternative(html_content, 'text/html')

    email.send()


def raise_non_field_error(message, code, key='non_field_error'):
    raise ValidationError({key: [ValidationError(message, code).detail]})


def get_templates(curl: str) -> dict:
    """
    Search for the two version of the template in the project's directory
    :param curl: The directory to sai files without the extension
    :return dict: A dictionary with the found text and html templates
    """
    return {
        'text': get_template('%s.txt' % curl),
        # 'html': get_template('%s.html' % curl)
    }
