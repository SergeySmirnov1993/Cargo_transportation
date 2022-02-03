from django.db import models


# Create your models here.
class Order(models.Model):
    load_place = models.CharField(max_length=100, null=False)
    unload_place = models.CharField(max_length=100, null=False)
    cargo = models.CharField(max_length=100, null=False)
    weight = models.FloatField(default=0.0)
    transport = models.CharField(max_length=100, null=True)
    rates = models.FloatField(default=0.0)
    tax = models.BooleanField(default=False)
    created_date = models.DateField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    duration = models.IntegerField(default=0)


class Transport(models.Model):
    reg_number = models.CharField(max_length=10, null=False)
    brand = models.CharField(max_length=30, null=False)
    model = models.CharField(max_length=30, null=False)
    carrying = models.FloatField(null=False)

