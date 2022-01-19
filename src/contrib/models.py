from django.db import models


class Notifaction(models.Model):
    """Model definition for Notifaction."""

    text = models.TextField()

    class Meta:
        """Meta definition for Notifaction."""

        verbose_name = 'Notifaction'
        verbose_name_plural = 'Notifactions'

    def __str__(self):
        """Unicode representation of Notifaction."""
        return f'{self.text}'
