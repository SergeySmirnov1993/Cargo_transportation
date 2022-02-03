from django import forms
from transportation.bl import functions


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
    reg_nam = forms.ChoiceField(required=False)


class Transport(forms.Form):
    reg_number = forms.CharField(label='Регистрационный знак:', max_length=10)
    brand = forms.CharField(label='Марка:', max_length=30)
    model = forms.CharField(label='Модель:', max_length=30)
    carrying = forms.FloatField(label='Грузоподъемность:')
