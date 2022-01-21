from django.db import models


class Question(models.Model):
    """Model definition for Questions."""

    class KIND(models.TextChoices):
        TEXT = 't'
        MCQ = 'm'

    title = models.CharField(max_length=50)
    kind = models.CharField(max_length=1, choices=KIND.choices)
    text = models.TextField()

    class Meta:
        """Meta definition for Questions."""

        verbose_name = 'Question'
        verbose_name_plural = 'Questions'

    def __str__(self):
        """Unicode representation of Questions."""
        return f'{self.title}'

    class API:
        search_fields = ('title',)


class Answer(models.Model):
    """Model definition for Answer."""

    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    text = models.TextField()

    class Meta:
        """Meta definition for Answer."""

        verbose_name = 'Answer'
        verbose_name_plural = 'Answers'

    def __str__(self):
        """Unicode representation of Answer."""
        return f'{self.text}'