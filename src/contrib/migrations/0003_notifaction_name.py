# Generated by Django 4.0.1 on 2022-01-19 21:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0002_notifaction_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='notifaction',
            name='name',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
    ]
