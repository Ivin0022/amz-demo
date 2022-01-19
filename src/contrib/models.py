from django.db import models
from django.contrib.auth import get_user_model


class Notifaction(models.Model):
    """Model definition for Notifaction."""

    name = models.CharField(max_length=50)
    text = models.TextField()
    user = models.ManyToManyField(get_user_model())
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        """Meta definition for Notifaction."""

        verbose_name = 'Notifaction'
        verbose_name_plural = 'Notifactions'

    def __str__(self):
        """Unicode representation of Notifaction."""
        return f'{self.text}'
