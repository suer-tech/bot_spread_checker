from django.contrib import admin

from .forms import InstrumentForm
from .models import Instrument


class InstrumentAdmin(admin.ModelAdmin):
    form = InstrumentForm
    list_display = ('name',)

admin.site.register(Instrument, InstrumentAdmin)