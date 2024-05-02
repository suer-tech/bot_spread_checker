from django.db import models


class Instrument(models.Model):
    name = models.CharField(max_length=100)
    base = models.FloatField()
    future = models.FloatField()

    def __str__(self):
        return self.name


class Base(models.Model):
    asset_name = models.CharField(max_length=100)

    class Meta:
        abstract = True


class Spread(Base):
    spread = models.FloatField()


class EntriesPoint(Base):
    entry_point = models.FloatField()


class PercentSignal(Base):
    percent_signal = models.FloatField()


class ValueSignal(Base):
    value_signal = models.FloatField()
