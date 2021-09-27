from django.db import models
from django.core.validators import MaxValueValidator
from apps.restaurants.models import Restaurants


class Foods(models.Model):
    name = models.CharField(max_length=255, help_text='Name', verbose_name='Name')
    restaurant = models.ForeignKey(Restaurants, on_delete=models.CASCADE, related_name='foods')
    description = models.CharField(max_length=255, help_text='Description', verbose_name='Description')
    calories = models.FloatField(default=0.0, validators=[MaxValueValidator(9999999)], null=False, help_text='Calories',
                                 verbose_name='Calories')

    def __str__(self):
        return self.name
