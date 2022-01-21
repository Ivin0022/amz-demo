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

    @property
    def filterset_fields(self):
        return

    @property
    def search_fields(self):
        list_types = (models.CharField, models.TextField)
        return [field.name for field in self.fields if isinstance(field, list_types)][:3]

    @property
    def ordering_fields(self):
        return


class AutoAPIView:

    def __init__(self) -> None:
        self.router = DefaultRouter()
        self.models = [m for m in apps.get_models()]

    def get_api_name(self, model):
        meta: Options = model._meta
        name: str = meta.verbose_name_plural
        return name.lower().replace(' ', '/')

    def get_class_name(self, model):
        meta: Options = model._meta
        return meta.model_name.title()

    def get_API_options(self, model) -> dict:
        API = getattr(model, 'API', None)
        return getattr(API, '__dict__', {})

    def get_serializer_options(self, model):

        default_options = SerializerOpitons(model).__dict__
        options: dict = self.get_API_options(model)
        options = {**default_options, **options}

        return {k: v for k, v in options.items() if k in SERIALIZER_OPTIONS}

    def get_viewset_options(self, model):

        default_options = ViewSetOpitons(model).__dict__
        options: dict = self.get_API_options(model)
        options = {**default_options, **options}

        return {k: v for k, v in options.items() if k in VIEWSET_OPTIONS}

    def get_serializer_meta_class(self, model):

        return type(
            'DefaultMeta',
            (),
            self.get_serializer_options(model),
        )

    def get_serializer_class(self, model):

        return type(
            f'{self.get_class_name(model)}Serializer',
            (ModelSerializer,),
            dict(Meta=self.get_serializer_meta_class(model),),
        )

    def get_viewset(self, model):
        return type(
            f'{self.get_class_name(model)}ViewSet',
            (ModelViewSet,),
            dict(
                queryset=model.objects.all(),
                serializer_class=self.get_serializer_class(model),
                **self.get_viewset_options(model)
            ),
        )

    @property
    def urls(self):
        for model in self.models:
            viewset = self.get_viewset(model)
            self.router.register(self.get_api_name(model), viewset)
        return self.router.urls
