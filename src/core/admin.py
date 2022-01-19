from django.contrib import admin
from django.apps import apps


class AutoAdminMaker:

    def __call__(self, *args, **kwds):

        models = (m for m in apps.get_models()
                  if not admin.site.is_registered(m))

        admin.site.register(models)


make_admins = AutoAdminMaker()
