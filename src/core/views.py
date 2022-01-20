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

    def get_viewset(self, model):

        class Meta:
            model = self.models[0]
            fields = '__all__'

        serializer_class = type(
            f'{self.get_class_name(model)}Serializer',
            (ModelSerializer, ),
            dict(Meta=Meta, ),
        )

        viewset = type(
            f'{self.get_class_name(model)}ViewSet',
            (ModelViewSet, ),
            dict(
                queryset=model.objects.all(),
                serializer_class=serializer_class,
            ),
        )

        return viewset

    @property
    def urls(self):
        for model in self.models:
            viewset = self.get_viewset(model)
            self.router.register(self.get_api_name(model), viewset)
        return self.router.urls
