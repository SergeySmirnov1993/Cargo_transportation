from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator

from transportation.bl import functions
from datetime import datetime as dt


class Order(forms.Form):
    transports_choices = functions.get_reg_num_choices()['all_rn_choices']
    drivers_choices = functions.get_drivers_choices()
    number = forms.IntegerField(label='Номер заявки', required=False)
    cargo = forms.CharField(label='Груз:')
    weight = forms.FloatField(label='Масса/Объем:')
    shipper = forms.CharField(label='Грузоотправитель')
    consignee = forms.CharField(label='Грузополучатель')
    load_place = forms.CharField(label='Место загрузки:')
    unload_place = forms.CharField(label='Место выгрузки:')
    rates = forms.FloatField(label='Ставка:', required=False)
    tax = forms.BooleanField(label='с НДС', required=False)
    transport = forms.ChoiceField(label='Автомобиль:', choices=transports_choices, required=False)
    driver = forms.ChoiceField(label='Водитель:', choices=drivers_choices, required=False)
    loading_date = forms.DateField(label='Дата загрузки:', required=False)
    unloading_date = forms.DateField(label='Дата выгрузки:', required=False)
    duration = forms.IntegerField(label='Расстояние:', required=False)
    info = forms.CharField(label='Дополнительная информация', widget=forms.Textarea, required=False)


class AdditionalOrder(forms.Form):
    trucks = functions.get_busy_trucks()
    choices = tuple((truck.reg_number, truck.reg_number) for truck in trucks)
    reg_nam = forms.ChoiceField(label='Автомобиль:', choices=choices, required=False)


class Transport(forms.Form):
    brand = forms.CharField(label='Марка:', max_length=30)
    model = forms.CharField(label='Модель:', max_length=30)
    release_year = forms.IntegerField(label='Год выпуска:')
    reg_number = forms.CharField(label='Регистрационный знак:', max_length=10)
    carrying = forms.FloatField(label='Грузоподъемность:')


class Period(forms.Form):
    month = forms.IntegerField(label='', required=False, min_value=1, max_value=12, widget=forms.NumberInput(attrs={'placeholder': 'Месяц'}))
    quarter = forms.IntegerField(label='', min_value=1, max_value=4, required=False, widget=forms.NumberInput(attrs={'placeholder': 'Квартал'}))
    year = forms.IntegerField(label='', min_value=2021, max_value=dt.now().year, required=False, widget=forms.NumberInput(attrs={'placeholder': 'Год'}))


class TruckTrailer(forms.Form):
    transports_choices = functions.get_reg_num_choices()['all_rn_choices']
    brand = forms.CharField(label='Марка:', max_length=30)
    model = forms.CharField(label='Модель:', max_length=30)
    release_year = forms.IntegerField(label='Год выпуска:')
    reg_number = forms.CharField(label='Регистрационный знак:', max_length=10)
    trailer_type = forms.CharField(label='Тип прицепа:', max_length=30)
    carrying = forms.FloatField(label='Грузоподъемность:')
    transport = forms.ChoiceField(label='Автомобиль:', choices=transports_choices, required=False)
    info = forms.CharField(label='Дополнительная информация', widget=forms.Textarea, required=False)


class Driver(forms.Form):
    transports_choices = functions.get_reg_num_choices()['all_rn_choices']
    name = forms.CharField(label='Имя:', max_length=30)
    surname = forms.CharField(label='Фамилия:', max_length=30)
    patronymic = forms.CharField(label='Отчество:', max_length=30)
    birth_date = forms.DateField(label='Дата рождения:')
    phone_num = forms.IntegerField(label='Номер телефона:')
    address = forms.CharField(label='Адрес:', max_length=100)
    transport = forms.ChoiceField(label='Автомобиль:', choices=transports_choices, required=False)
