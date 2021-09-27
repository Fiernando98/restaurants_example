import re

from django.db.models import Value
from drf_query_filter.fields import ConcatField


class UserNamesField(ConcatField):
    """ Custom Field to be used in views """

    def __init__(self, *args, **kwargs):
        path = kwargs.pop('path', '')
        if path:
            path = '%s__' % path
        kwargs['target_fields'] = ['%s%s' % (path, value) if isinstance(value, str) else value for value in
                                   ['first_name', Value(' '), 'last_name']]
        kwargs['target_field_name'] = re.sub(r'__+', '_', '%s%s' % (path, 'first_name_and_last_name'))
        kwargs['lookup'] = 'icontains'
        super().__init__(*args, **kwargs)
