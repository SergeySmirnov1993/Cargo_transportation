from django.contrib import admin
from transportation import models


# Register your models here.
admin.site.register(models.Order)
admin.site.register(models.Transport)
