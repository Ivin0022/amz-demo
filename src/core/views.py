# django
from django.apps import apps
from django.db.models.options import Options
from django.db import models

# rest framework
from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import ModelViewSet
from rest_framework.serializers import ModelSerializer

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

SERIALIZER_OPTIONS = [
    'model',
    'fields',
    'read_only_fields',
    'depth',
]


class SerializerOpitons:

    def __init__(self, model) -> None:
        self.model = model
        self.fields = '__all__'


class ViewSetOpitons:

    def __init__(self, model) -> None:
        self.model = model
        self.meta: Options = self.model._meta
        self.fields = self.meta.fields
        self.fk_fields = [field for field in self.fields if isinstance(field, models.ForeignKey)]
        self.field_names = [field.name for field in self.fields]

    def _get_field_names_for_type(self, types):
        return [field.name for field in self.fields if isinstance(field, types)]

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


class ModelAPI:

    def __init__(self, model) -> None:
        self.model: models.Model = model
        self.meta: Options = self.model._meta
        self.api_name: str = self.meta.verbose_name_plural.lower().replace(' ', '/')
        self.basename: str = self.api_name
        self.model_name: str = self.meta.model_name.title()
        self.API = getattr(self.model, 'API', None)
        self.options: dict = getattr(self.API, '__dict__', {})

    def get_serializer_options(self):

        default_options = SerializerOpitons(self.model)
        default_options = {k: getattr(default_options, k) for k in SERIALIZER_OPTIONS if hasattr(default_options, k)}

        return {**default_options, **self.options}

    def get_viewset_options(self):

        default_options = ViewSetOpitons(self.model)
        default_options = {k: getattr(default_options, k) for k in VIEWSET_OPTIONS if hasattr(default_options, k)}

        return {**default_options, **self.options}

    def get_serializer_meta_class(self):

        return type(
            'DefaultMeta',
            (),
            self.get_serializer_options(),
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
                queryset=self.model._default_manager.all(),
                serializer_class=self.get_serializer_class(),
                **self.get_viewset_options(),
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
