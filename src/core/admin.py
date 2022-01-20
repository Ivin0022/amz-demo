from django.contrib import admin
from django.apps import apps
from django.db import models
from django.db.models.options import Options

LIST_FILTER = [
    models.DateField,
    models.DateTimeField,
    models.ForeignKey,
    models.BooleanField,
]

SEARCH_FIELD_NAMES = [
    'name',
    'slug',
]

DATE_HIERARCHY_NAMES = [
    'created_at',
    'updated_at',
    'joined_at',
]


class AdminModel:

    def __init__(self, model):
        self.model = model
        self.meta: Options = self.model._meta
        self.fields = self.model._meta.fields
        self.fk_fields = [
            field for field in self.fields
            if isinstance(field, models.ForeignKey)
        ]
        self.field_names = [field.name for field in self.meta.fields]

    @property
    def date_hierarchy(self):
        for name in self.field_names:
            if name in DATE_HIERARCHY_NAMES:
                return name

    @property
    def search_fields(self):
        list_types = (models.CharField, models.TextField)
        return [
            field.name for field in self.fields
            if isinstance(field, list_types)
        ][:3]

    def make(self):

        list_display = [field.name for field in self.fields]
        filter_horizontal = [
            field.name for field in self.meta.local_many_to_many
        ]

        return type(
            '%sAdmin' % self.model.__name__,
            (admin.ModelAdmin, ),
            dict(
                list_display=list_display,
                filter_horizontal=filter_horizontal,
                search_fields=self.search_fields,
                date_hierarchy=self.date_hierarchy,
            ),
        )


class AutoAdminMaker:

    def register(self, model):
        admin_class = AdminModel(model).make()

        if admin.site.is_registered(model):
            old_admin_class = admin.site._registry[model].__class__

            try:
                admin_class = type(
                    old_admin_class.__name__,
                    (old_admin_class, admin_class),
                    {},
                )
            except TypeError:
                admin_class = type(
                    old_admin_class.__name__,
                    (admin_class, old_admin_class),
                    {},
                )

            admin.site.unregister(model)

        admin.site.register(model, admin_class)

    def __call__(self, *args, **kwds):
        for model in apps.get_models():
            self.register(model)


make_admins = AutoAdminMaker()
