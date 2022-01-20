# django
from django.apps import apps
from django.db.models.options import Options

# rest framework
from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import ModelViewSet
from rest_framework.serializers import ModelSerializer


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

    def get_API_options(self, model):
        default_options = dict(model=model, fields='__all__')

        API = getattr(model, 'API', None)
        options = getattr(API, '__dict__', {})

        return {**default_options, **options}

    def get_serializer_meta_class(self, model):

        return type(
            'DefaultMeta',
            (),
            self.get_API_options(model),
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
            ),
        )

    @property
    def urls(self):
        for model in self.models:
            viewset = self.get_viewset(model)
            self.router.register(self.get_api_name(model), viewset)
        return self.router.urls
