# builtins
from dataclasses import asdict, dataclass
from typing import Union, Callable, List

# django
from django.apps import apps
from django.db.models.options import Options
from django.db import models

# django filters
from django_filters.rest_framework import FilterSet

# rest framework
from rest_framework.pagination import BasePagination
from rest_framework.permissions import BasePermission
from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import ModelViewSet
from rest_framework.serializers import ModelSerializer

FIELDS_OR_ALL = Union[str, List, tuple]
FIELDS = Union[List, tuple]

VIEWSET_OPTIONS = [
    'pagination_class',
    'permission_classes',
    'filterset_fields',
    'filterset_class',
    'search_fields',
    'ordering_fields',

    # callable
    'get_queryset',
    'get_serializer_class',
]


@dataclass
class BaseOptions:
    model: models.Model

    def to_dict(self) -> dict:
        API = getattr(self.model, 'API', None)
        options: dict = getattr(API, '__dict__', {})
        options = {k: options.get(k) or v for k, v in asdict(self).items()}

        # filter None values in dict
        return {k: v for k, v in options.items() if v is not None}


@dataclass
class SerializerOpitons(BaseOptions):
    fields: FIELDS_OR_ALL = '__all__'
    read_only_fields: FIELDS = None
    depth: int = None


@dataclass
class ViewSetOpitons(BaseOptions):

    queryset: models.QuerySet = None
    pagination_class: List[BasePagination] = None
    permission_classes: List[BasePermission] = None
    filterset_class: FilterSet = None
    filterset_fields: FIELDS = None
    search_fields: FIELDS = None
    ordering_fields: FIELDS = None

    get_queryset: Callable = None
    get_serializer_class: Callable = None

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.meta: Options = self.model._meta
        self.fields = self.meta.fields

    def _get_field_names_for_type(self, types):
        return [field.name for field in self._get_fields_for_type(types)]

    def _get_fields_for_type(self, types):
        return [field for field in self.fields if isinstance(field, types)]

    def _get_choices_field_names(self):
        fields = self._get_fields_for_type(models.CharField)
        return [i.name for i in fields if getattr(i, 'choices', None)]

    @property
    def filterset_fields(self):
        types = (models.ForeignKey, models.DateField, models.DateTimeField)
        field_names = self._get_field_names_for_type(types)
        choices_field_names = self._get_choices_field_names()

        return [*field_names, *choices_field_names]

    @property
    def search_fields(self):
        types = (models.CharField, models.TextField)
        return self._get_field_names_for_type(types)[:3]

    @property
    def ordering_fields(self):
        types = (models.DateField, models.DateTimeField)
        return self._get_field_names_for_type(types)

    @property
    def queryset(self):
        return self.model._default_manager.all()


class ModelAPI:

    def __init__(self, model) -> None:
        self.model: models.Model = model
        self.meta: Options = self.model._meta

        self.api_name: str = self.meta.verbose_name_plural.lower().replace(' ', '/')
        self.model_name: str = self.meta.model_name.title()
        self.basename: str = self.api_name

        self.serializer_options = SerializerOpitons(self.model).to_dict()
        self.viewset_options = ViewSetOpitons(self.model).to_dict()

    def get_serializer_meta_class(self):
        return type(
            'DefaultMeta',
            (),
            self.serializer_options,
        )

    def get_serializer_class(self):

        return type(
            f'{self.model_name}Serializer',
            (ModelSerializer,),
            dict(Meta=self.get_serializer_meta_class(),),
        )

    def get_viewset(self):
        return type(
            f'{self.model_name}ViewSet',
            (ModelViewSet,),
            dict(
                serializer_class=self.get_serializer_class(),
                **self.viewset_options,
            ),
        )


class AutoAPIView:

    def __init__(self) -> None:
        self.router = DefaultRouter()
        self.models = apps.get_models()

    @property
    def urls(self):

        for model in self.models:
            _model = ModelAPI(model)
            self.router.register(_model.api_name, _model.get_viewset(), _model.basename)

        return self.router.urls
