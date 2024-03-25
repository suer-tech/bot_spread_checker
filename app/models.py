from django.db import models


class Instrument(models.Model):
    name = models.CharField(max_length=100)
    base = models.DecimalField(max_digits=10, decimal_places=10)
    future = models.DecimalField(max_digits=10, decimal_places=10)

