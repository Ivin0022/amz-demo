from django.db import models


class Question(models.Model):
    """Model definition for Questions."""

    title = models.CharField(max_length=50)
    text = models.TextField()

    class Meta:
        """Meta definition for Questions."""

        verbose_name = 'Question'
        verbose_name_plural = 'Questions'

    # class API:
    # fields = ('title',)
    # search_fields = ('title',)

    def __str__(self):
        """Unicode representation of Questions."""
        return f'{self.title}'


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