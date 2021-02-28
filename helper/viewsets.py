from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

class ModelInstanceViewSet(mixins.CreateModelMixin,
                                mixins.RetrieveModelMixin,
                                mixins.UpdateModelMixin,
                                mixins.DestroyModelMixin,
                                GenericViewSet):
    """
    A viewset that provides provide all actions EXCEPT `list()`
    """
    pass