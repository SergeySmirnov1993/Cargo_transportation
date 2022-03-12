from django.contrib import admin
from transportation import models


# Register your models here.
admin.site.register(models.Transport)
admin.site.register(models.TruckTrailer)
admin.site.register(models.Driver)
admin.site.register(models.Order)
