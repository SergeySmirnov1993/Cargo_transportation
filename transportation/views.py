import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from transportation import forms, models
from transportation.bl import functions, reports


def home_page(request):
    context = {}
    date_time_now = functions.current_datetime()
    # exchange_data = functions.exchange_rate()
    # context['exchange_data'] = exchange_data
    context['date_time_now'] = date_time_now
    return render(request, 'home_page.html', context)


@login_required
def show_orders(request):
    if request.method == 'GET':
        orders = functions.get_not_completed_orders()
        duration = {}
        for order in orders:
            duration[order.id] = functions.convert_time(order.duration)
        context = {'orders': orders, 'duration': duration}
        return render(request, 'orders.html', context)


@login_required
def transport(request):
    if request.method == 'GET':
        trailer_form = forms.TruckTrailer()
        free_transport = functions.get_free_trucks()
        busy_transport = functions.get_busy_trucks()
        context = {'busy_transport': busy_transport,
                   'free_transport': free_transport,
                   'form': trailer_form}
        return render(request, 'transport.html', context)

    if request.method == 'POST':
        form = forms.TruckTrailer(request.POST)
        new_trailer = models.TruckTrailer()

        if form.is_valid():
            new_trailer.brand = form.cleaned_data['brand']
            new_trailer.model = form.cleaned_data['model']
            new_trailer.release_year = form.cleaned_data['release_year']
            new_trailer.reg_number = form.cleaned_data['reg_number']
            new_trailer.trailer_type = form.cleaned_data['trailer_type']
            new_trailer.carrying = form.cleaned_data['carrying']
            new_trailer.info = form.cleaned_data['info']
            new_trailer.save()

            return redirect('transport')


@login_required
def show_drivers(request):
    if request.method == 'GET':
        context = {}
        form = forms.Driver()
        drivers = functions.get_all_drivers()
        context['drivers'] = drivers
        context['form'] = form
        return render(request, 'drivers.html', context)

    elif request.method == 'POST':
        pass


def edit_driver(request, driver_id):
    if request.method == 'GET':
        driver = functions.get_driver(driver_id)
        form = forms.Driver()

        form.fields['name'].initial = driver.name
        form.fields['surname'].initial = driver.surname
        form.fields['patronymic'].initial = driver.patronymic
        form.fields['birth_date'].initial = driver.birth_date
        form.fields['phone_num'].initial = driver.phone_num
        form.fields['address'].initial = driver.address
        form.fields['transport'].initial = driver.transport.all()

        context = {'form': form}
        return render(request, 'edit_drivers.html', context)

    elif request.method == 'POST':
        updated_driver = functions.get_order(driver_id)
        form = forms.Driver(request.POST)

        if form.is_valid():
            updated_driver.name = form.cleaned_data['name']
            updated_driver.surname = form.cleaned_data['surname']
            updated_driver.patronymic = form.cleaned_data['patronymic']
            updated_driver.birth_date = form.cleaned_data['birth_date']
            updated_driver.phone_num = form.cleaned_data['phone_num']
            updated_driver.address = form.cleaned_data['address']
            updated_driver.transport = form.cleaned_data['transport']
            updated_driver.save()

            return redirect('drivers')


@login_required
def reports_dash(request, type='empty'):
    if request.method == 'GET':
        context = {}
        if type == 'empty':
            context['text'] = 'Выберите позицию отчета:'
        elif type == 'number':
            data = reports.process_data(reports.number_of_transportation_by_months())
            context = {'data': data, 'change_tmpl': False}
        elif type == 'rubles':
            data = reports.process_data(reports.volume_rubles_by_months())
            context = {'data': data, 'change_tmpl': False}
        elif type == 'period':
            default_period = {'year': datetime.datetime.now().year}
            data = reports.distribution_by_directions(default_period)
            form = forms.Period()
            context = {'data': data, 'change_tmpl': True, 'form': form, 'period_info': default_period}
        return render(request, 'reports.html', context)

    elif request.method == "POST":
        form = forms.Period(request.POST)
        if form.is_valid():
            month = form.cleaned_data['month']
            quarter = form.cleaned_data['quarter']
            year = form.cleaned_data['year']

            form = forms.Period()

            if month and year:
                period = {'month': (month, year)}
                data = reports.distribution_by_directions(period)
                context = {'data': data, 'change_tmpl': True, 'form': form, 'period_info': period}

            elif quarter and year:
                period = {'quarter': (quarter, year)}
                data = reports.distribution_by_directions(period)
                context = {'data': data, 'change_tmpl': True, 'form': form, 'period_info': period}

            elif year and quarter is None and month is None:
                period = {'year': year}
                data = reports.distribution_by_directions(period)
                context = {'data': data, 'change_tmpl': True, 'form': form, 'period_info': period}

            return render(request, 'reports.html', context)


@login_required
def add_order(request):
    if request.method == 'GET':
        add_from = forms.Order()
        free_rn_choices = functions.get_reg_num_choices()['free_rn_choices']
        add_from.fields['transport'].choices = free_rn_choices
        add_from.fields['driver'].choices = functions.get_drivers_choices()
        context = {'form': add_from}
        if len(free_rn_choices) == 1:
            context['empty_trucks'] = True
        return render(request, 'add_order.html', context)

    elif request.method == 'POST':
        form = forms.Order(request.POST)
        new_order = models.Order()

        if form.is_valid():
            new_order.number = form.cleaned_data['number']
            new_order.cargo = form.cleaned_data['cargo']
            new_order.weight = form.cleaned_data['weight']
            new_order.shipper = form.cleaned_data['shipper']
            new_order.consignee = form.cleaned_data['consignee']
            new_order.load_place = form.cleaned_data['load_place']
            new_order.unload_place = form.cleaned_data['unload_place']

            if form.cleaned_data['rates']:
                new_order.rates = form.cleaned_data['rates']
            else:
                data = functions.orders_calculations(new_order.load_place, new_order.unload_place)
                new_order.rates = data[0]
                new_order.duration = data[1]

            if form.cleaned_data['duration']:
                new_order.duration = form.cleaned_data['duration']

            new_order.tax = form.cleaned_data['tax']

            if form.cleaned_data['transport']:
                reg_num = set()
                reg_num.add(form.cleaned_data['transport'])
                transport = functions.get_trucks_by_numbers(reg_num)[0]
                new_order.transport = transport

            if form.cleaned_data['driver']:
                driver_data = form.cleaned_data['driver'].split()
                name, surname = driver_data[0], driver_data[1]
                new_order.driver = functions.get_driver_by_name(name, surname)

            new_order.loading_date = form.cleaned_data['loading_date']
            new_order.unloading_date = form.cleaned_data['unloading_date']
            new_order.info = form.cleaned_data['info']
            new_order.save()

            return redirect('orders')


@login_required
def add_additional_order(request, order_id):
    if request.method == 'GET':
        suitable_trucks = functions.get_truck_for_additional_order(order_id)
        if suitable_trucks:
            form = forms.AdditionalOrder()
            form.fields['reg_nam'].choices = suitable_trucks
            context = {'form': form, 'trucks': True}
        else:
            context = {'trucks': False}
        return render(request, 'add_additional_order.html', context)

    elif request.method == 'POST':
        updated_order = functions.get_order(order_id)
        form = forms.AdditionalOrder(request.POST)
        if form.is_valid():
            truck = functions.get_trucks_by_numbers([form.cleaned_data['reg_nam']])
            updated_order.transport = truck[0]
            updated_order.save()

        return redirect('orders')


@login_required
def edit_order(request, order_id):
    if request.method == 'GET':
        order = functions.get_order(order_id)
        edit_form = forms.Order()

        free_rn_choices = functions.get_reg_num_choices()['free_rn_choices']
        curr_truck_choice = ((order.transport.reg_number, order.transport.reg_number),) if order.transport else ''
        choices = free_rn_choices + curr_truck_choice if order.transport else free_rn_choices

        drivers = functions.get_drivers_choices()

        edit_form.fields['number'].initial = order.number
        edit_form.fields['cargo'].initial = order.cargo
        edit_form.fields['weight'].initial = order.weight
        edit_form.fields['shipper'].initial = order.shipper
        edit_form.fields['consignee'].initial = order.consignee
        edit_form.fields['load_place'].initial = order.load_place
        edit_form.fields['unload_place'].initial = order.unload_place
        edit_form.fields['rates'].initial = order.rates
        edit_form.fields['tax'].initial = order.tax
        edit_form.fields['transport'].choices = choices
        if order.transport:
            edit_form.fields['transport'].initial = order.transport.reg_number
        if order.driver:
            edit_form.fields['driver'].choices = drivers
            edit_form.fields['driver'].initial = f'{order.driver.name} {order.driver.surname}'
        edit_form.fields['loading_date'].initial = order.loading_date
        edit_form.fields['unloading_date'].initial = order.unloading_date
        edit_form.fields['duration'].initial = order.duration
        edit_form.fields['info'].initial = order.info

        context = {'form': edit_form, 'action': 'edit', 'order_id': order.id}
        if len(free_rn_choices) == 1:
            context['empty_trucks'] = True
        return render(request, 'add_order.html', context)

    elif request.method == 'POST':
        updated_order = functions.get_order(order_id)
        form = forms.Order(request.POST)

        if form.is_valid():
            updated_order.number = form.cleaned_data['number'] if form.cleaned_data['number'] else updated_order.id
            updated_order.cargo = form.cleaned_data['cargo']
            updated_order.weight = form.cleaned_data['weight']
            updated_order.shipper = form.cleaned_data['shipper']
            updated_order.consignee = form.cleaned_data['consignee']
            updated_order.load_place = form.cleaned_data['load_place']
            updated_order.unload_place = form.cleaned_data['unload_place']

            if form.cleaned_data['rates']:
                updated_order.rates = form.cleaned_data['rates']
            else:
                data = functions.orders_calculations(updated_order.load_place, updated_order.unload_place)
                updated_order.rates = data[0]
                updated_order.duration = data[1]

            if form.cleaned_data['duration']:
                updated_order.duration = form.cleaned_data['duration']

            updated_order.tax = form.cleaned_data['tax'] if form.cleaned_data['tax'] else False

            if form.cleaned_data['transport']:
                truck = functions.get_trucks_by_numbers([form.cleaned_data['transport']])
                updated_order.transport = truck[0]
            else:
                updated_order.transport = None

            if form.cleaned_data['driver']:
                driver_data = form.cleaned_data['driver'].split()
                name, surname = driver_data[0], driver_data[1]
                updated_order.driver = functions.get_driver_by_name(name, surname)
            else:
                updated_order.driver = None

            updated_order.info = form.cleaned_data['info'] if form.cleaned_data['info'] else ''
            updated_order.save()

            return redirect('orders')


@login_required
def completed_order(request, order_id):
    if request.method == 'GET':
        updated_order = functions.get_order(order_id)
        updated_order.completed = True
        updated_order.save()
        return redirect('orders')


@login_required
def delete_order(request, order_id):
    if request.method == 'GET':
        order = functions.get_order(order_id)
        order.delete()
        return redirect('orders')


@login_required
def add_transport(request):
    if request.method == 'GET':
        add_from = forms.Transport()
        context = {'form': add_from}
        return render(request, 'add_transport.html', context)

    elif request.method == 'POST':
        form = forms.Transport(request.POST)
        new_transport = models.Transport()

        if form.is_valid():
            new_transport.brand = form.cleaned_data['brand']
            new_transport.model = form.cleaned_data['model']
            new_transport.release_year = form.cleaned_data['release_year']
            new_transport.reg_number = form.cleaned_data['reg_number']
            new_transport.carrying = form.cleaned_data['carrying']
            if form.cleaned_data['trailer']:
                trailer = functions.get_trailer_by_number(form.cleaned_data['trailer'])
                new_transport.trailer = trailer
            else:
                new_transport.trailer = None
            new_transport.save()

            return redirect('transport')


@login_required
def edit_transport(request, truck_id):
    if request.method == 'GET':
        choices = functions.get_trailer_choices()
        truck = functions.get_truck(truck_id)
        edit_form = forms.Transport()
        edit_form.fields['brand'].initial = truck.brand
        edit_form.fields['model'].initial = truck.model
        edit_form.fields['release_year'].initial = truck.release_year
        edit_form.fields['reg_number'].initial = truck.reg_number
        edit_form.fields['carrying'].initial = truck.carrying

        if truck.trailer:
            current_choice = ((truck.trailer.reg_number, truck.trailer.reg_number),)
            edit_form.fields['trailer'].choices = choices + current_choice
            edit_form.fields['trailer'].initial = truck.trailer.reg_number

        context = {'form': edit_form, 'action': 'edit', 'truck_id': truck.id}
        return render(request, 'add_transport.html', context)

    elif request.method == 'POST':
        updated_truck = functions.get_truck(truck_id)
        form = forms.Transport(request.POST)

        if form.is_valid():
            updated_truck.brand = form.cleaned_data['brand']
            updated_truck.model = form.cleaned_data['model']
            updated_truck.release_year = form.cleaned_data['release_year']
            updated_truck.reg_number = form.cleaned_data['reg_number']
            updated_truck.carrying = form.cleaned_data['carrying']
            if form.cleaned_data['trailer']:
                trailer = functions.get_trailer_by_number(form.cleaned_data['trailer'])
                updated_truck.trailer = trailer
            updated_truck.save()

            return redirect('transport')


@login_required
def delete_truck(request, truck_id):
    if request.method == 'GET':
        truck = functions.get_truck(truck_id)
        truck.delete()
        return redirect('transport')


@login_required
def charts(request):
    if request.method == 'GET':
        num_data = reports.number_of_transportation_by_months()
        proc_num_data = reports.process_data_for_charts(num_data)
        rub_data = reports.volume_rubles_by_months()
        proc_rub_data =reports.process_data_for_charts(rub_data)
        period_data = [['Направление', 'Кол-во']] + reports.distribution_by_directions({'year': 2022})
        context = {'period_data': period_data, 'proc_num_data': proc_num_data, 'proc_rub_data': proc_rub_data}
        return render(request, 'charts.html', context)

