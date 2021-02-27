from typing import Any, Callable, List, OrderedDict
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework.serializers import ValidationError

def qs_exists(queryset):
    try:
        return queryset.exists()
    except (TypeError, ValueError):
        return False

def qs_filter(queryset, **kwargs):
    try:
        return queryset.filter(**kwargs)
    except (TypeError, ValueError):
        return queryset.none()

class ExistValidator:
    message = _('This field must exists.')
    requires_context = True

    def __init__(self, queryset, field=None, message=None, lookup='exact') -> None:
        self.queryset = queryset
        self.message = message or self.message
        self.field = field
        self.lookup = lookup

    def filter_queryset(self, value, queryset, field_name) -> QuerySet:
        """
        Filter the queryset to all instances matching the given attribute.
        """
        filter_kwargs = {'%s__%s' % (field_name, self.lookup): value}
        return qs_filter(queryset, **filter_kwargs)

    def __call__(self, value, serializer_field) -> None:
        # Determine the underlying model field name. This may not be the
        # same as the serializer field name if `source=<>` is set.
        field_name = self.field if self.field is not None \
                else serializer_field.source_attrs[-1]
        # Determine the existing instance, if this is an update operation.
        # TODO: Use exclude_current_instance to exclude during update
        queryset = self.queryset
        queryset = self.filter_queryset(value, queryset, field_name)

        if not qs_exists(queryset):
            raise ValidationError(self.message, code='exist')

class NestedDataUnqiueValidator:
    """
        Ensures that all the attributes present in the 
        payload have unique values, only works for 1 level deep. 
        (dict within a dict NOT supported)
    """
    def __init__(self, ignore : List = None) -> None:
        self.ignore = set(ignore) if ignore is not None else set()

    def __call__(self, value : OrderedDict) -> None:
        req : dict = dict()

        for layer in value:
            for key, val in layer.items():
                if key not in self.ignore:
                    if key in req.keys():
                        if val in req[key]:
                            raise ValidationError(
                                _('%s field with %s value already exists!' % (key, val)), 
                                code='unique'
                            )
                        else: req[key].add(val)
                    else: req[key]  = {val}

class InListValidator:
    """
        Value of a parameter should be in a given
        list of valid values
    """
    def __init__(self, valid_list : List, case_sensitive : bool = True) -> None:
        self.valid_list = valid_list
        self.case_sensitive = case_sensitive

    def __call__(self, value : str, *args: Any, **kwds: Any) -> None:
        if self.case_sensitive:
            self.valid_list, value = [v.lower() for v in self.valid_list], value.lower()

        unique_valid_list = set(self.valid_list)
        if value not in unique_valid_list:
            raise ValidationError(
                _('Invalid value! valid values are :' % (', '.join(unique_valid_list))), 
                code='invalid'
            )
