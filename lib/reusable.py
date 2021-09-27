from rest_framework.serializers import PrimaryKeyRelatedField
from django.core.exceptions import ObjectDoesNotExist


class PkRelatedSerializerField(PrimaryKeyRelatedField):
    """
    An extension to the PrimaryKeyRelatedField where the return value is the serializer
    representation of the instance.
    """

    def __init__(self, **kwargs):
        self.instance_serializer = kwargs.pop('instance_serializer', None)
        super().__init__(**kwargs)

    def bind(self, field_name, parent):
        super(PkRelatedSerializerField, self).bind(field_name, parent)
        self.instance_serializer.parent = self.root

    def to_representation(self, value):
        data = value.pk
        if self.instance_serializer is not None:
            queryset = self.get_queryset()
            try:
                return self.instance_serializer.to_representation(queryset.get(pk=data))
            except ObjectDoesNotExist:
                self.fail('does_not_exist', pk_value=data)
            except (TypeError, ValueError):
                self.fail('incorrect_type', data_type=type(data).__name__)
        return value.pk
