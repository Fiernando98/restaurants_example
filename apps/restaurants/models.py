from django.db import models
from django.core.validators import MaxValueValidator


class Restaurants(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, help_text='Name', verbose_name='Name')
    description = models.CharField(max_length=255, help_text='Description', verbose_name='Description')

    def __str__(self):
        return self.name
