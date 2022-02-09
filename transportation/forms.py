from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator

from transportation.bl import functions
from datetime import datetime as dt


class LoginForm(forms.Form):
    username = forms.CharField(
        label='', min_length=4, max_length=50, required=True, widget=forms.TextInput(attrs={'placeholder': 'User name'}))
    password = forms.CharField(label='', min_length=4, widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class Order(forms.Form):
    load_place = forms.CharField(label='Место загрузки:')
    unload_place = forms.CharField(label='Место выгрузки:')
    cargo = forms.CharField(label='Груз:')
    weight = forms.FloatField(label='Масса/Объем:')
    all_trucks_reg_num = functions.get_reg_num_choices()['all_rn_choices']
    rates = forms.FloatField(label='Ставка:', required=False)
    transport = forms.ChoiceField(label='Автомобиль:', choices=all_trucks_reg_num, required=False)
    tax = forms.BooleanField(label='с НДС', required=False)


class AdditionalOrder(forms.Form):
    trucks_rn = functions.get_busy_reg_num()
    choices = tuple((key, key) for key in trucks_rn)
    reg_nam = forms.ChoiceField(label='Автомобиль:', choices=choices, required=False)


class Transport(forms.Form):
    reg_number = forms.CharField(label='Регистрационный знак:', max_length=10)
    brand = forms.CharField(label='Марка:', max_length=30)
    model = forms.CharField(label='Модель:', max_length=30)
    carrying = forms.FloatField(label='Грузоподъемность:')


class Period(forms.Form):
    month = forms.IntegerField(label='', required=False, min_value=1, max_value=12, widget=forms.NumberInput(attrs={'placeholder': 'Месяц'}))
    quarter = forms.IntegerField(label='', min_value=1, max_value=4, required=False, widget=forms.NumberInput(attrs={'placeholder': 'Квартал'}))
    year = forms.IntegerField(label='', min_value=2021, max_value=dt.now().year, required=False, widget=forms.NumberInput(attrs={'placeholder': 'Год'}))
