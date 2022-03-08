from django.db import models


# Create your models here.
class TruckTrailer(models.Model):
    brand = models.CharField(max_length=20, null=False)
    model = models.CharField(max_length=20, null=False)
    release_year = models.IntegerField(default=0)
    reg_number = models.CharField(max_length=10, null=False)
    trailer_type = models.CharField(max_length=20, null=False)
    carrying = models.FloatField(null=False)
    info = models.CharField(max_length=500, null=True)


class Transport(models.Model):
    brand = models.CharField(max_length=30, null=False)
    model = models.CharField(max_length=30, null=False)
    release_year = models.IntegerField(default=0)
    reg_number = models.CharField(max_length=10, null=False)
    trailer = models.OneToOneField(
        'TruckTrailer',
        null=True,
        on_delete=models.SET_NULL,
        related_name='transport'
    )
    carrying = models.FloatField(null=False)


class Driver(models.Model):
    name = models.CharField(max_length=30, null=False)
    surname = models.CharField(max_length=30, null=False)
    patronymic = models.CharField(max_length=30, null=True)
    birth_date = models.DateField()
    phone_num = models.CharField(max_length=11, null=True)
    address = models.CharField(max_length=100, null=True)
    transport = models.ManyToManyField(
        'Transport',
        related_name='drivers'
    )


class Order(models.Model):
    number = models.IntegerField(default=0)
    cargo = models.CharField(max_length=500, null=False)
    weight = models.FloatField(default=0.0)
    shipper = models.CharField(max_length=300, null=False)
    consignee = models.CharField(max_length=300, null=False)
    load_place = models.CharField(max_length=300, null=False)
    unload_place = models.CharField(max_length=300, null=False)
    rates = models.FloatField(default=0.0)
    tax = models.BooleanField(default=False)
    transport = models.ForeignKey(
        Transport,
        null=True,
        on_delete=models.SET_NULL,
        related_name='tr_orders'
    )
    driver = models.ForeignKey(
        Driver,
        null=True,
        on_delete=models.SET_NULL,
        related_name='dr_orders'
    )
    loading_date = models.DateField()
    unloading_date = models.DateField()
    created_date = models.DateField(auto_now_add=True)
    duration = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    info = models.CharField(max_length=500, null=True)
