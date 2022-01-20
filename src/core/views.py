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
        return name.replace(' ', '/')

    @property
    def urls(self):

        class s(ModelSerializer):

            class Meta:
                model = self.models[0]
                fields = '__all__'

        class a(ModelViewSet):
            queryset = self.models[0].objects.all()
            serializer_class = s

        self.router.register(self.get_api_name(self.models[0]), a)
        return self.router.urls
