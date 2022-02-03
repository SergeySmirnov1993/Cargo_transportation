from django.shortcuts import render, redirect
from transportation import forms, models
from transportation.bl import functions


def home_page(request):
    return render(request, 'home_page.html')


def show_orders(request):
    if request.method == 'GET':
        orders = functions.get_not_completed_orders()
        duration = {}
        for order in orders:
            duration[order.id] = functions.convert_time(order.duration)
        context = {'orders': orders, 'duration': duration}
        return render(request, 'orders.html', context)


def transport(request):
    if request.method == 'GET':
        free_transport = functions.get_free_trucks()
        busy_transport = functions.get_busy_trucks()
        context = {'busy_transport': busy_transport,
                   'free_transport': free_transport}
        return render(request, 'transport.html', context)


def reports(request):
    return render(request, 'reports.html')


def add_order(request):
    if request.method == 'GET':
        add_from = forms.Order()
        free_rn_choices = functions.get_reg_num_choices()['free_rn_choices']
        add_from.fields['transport'].choices = free_rn_choices
        context = {'form': add_from}
        if len(free_rn_choices) == 1:
            context['empty_trucks'] = True
        return render(request, 'add_order.html', context)

    elif request.method == 'POST':
        form = forms.Order(request.POST)
        new_order = models.Order()

        if form.is_valid():
            new_order.load_place = form.cleaned_data['load_place']
            new_order.unload_place = form.cleaned_data['unload_place']
            new_order.cargo = form.cleaned_data['cargo']
            new_order.weight = form.cleaned_data['weight']
            new_order.transport = form.cleaned_data['transport']
            new_order.tax = form.cleaned_data['tax']
            if form.cleaned_data['rates']:
                new_order.rates = form.cleaned_data['rates']
            else:
                data = functions.orders_calculations(new_order.load_place, new_order.unload_place)
                new_order.rates = data[0]
                new_order.duration = data[1]
            new_order.save()

            return redirect('orders')


def add_additional_order(request, order_id):
    if request.method == 'GET':
        order_id = functions.get_order(order_id).id
        suitable_trucks = functions.get_truck_for_additional_order(order_id)
        form = forms.AdditionalOrder()
        form.fields['reg_nam'].choices = suitable_trucks
        context = {'form': form, 'trucks': True if suitable_trucks else False}
        return render(request, 'add_additional_order.html', context)

    elif request.method == 'POST':
        updated_order = functions.get_order(order_id)
        form = forms.AdditionalOrder(request.POST)
        updated_order.transport = form.cleaned_data['reg_nam']
        updated_order.save()

        return redirect('orders')


def edit_order(request, order_id):
    if request.method == 'GET':
        order = functions.get_order(order_id)
        edit_form = forms.Order()
        free_rn_choices = functions.get_reg_num_choices()['free_rn_choices']
        curr_truck_choice = ((order.transport, order.transport),) if order.transport else ''
        choices = free_rn_choices + curr_truck_choice if order.transport else free_rn_choices
        edit_form.fields['transport'].choices = choices
        edit_form.fields['transport'].initial = order.transport
        edit_form.fields['load_place'].initial = order.load_place
        edit_form.fields['unload_place'].initial = order.unload_place
        edit_form.fields['cargo'].initial = order.cargo
        edit_form.fields['weight'].initial = order.weight
        edit_form.fields['rates'].initial = order.rates
        edit_form.fields['tax'].initial = order.tax
        context = {'form': edit_form, 'action': 'edit', 'order_id': order.id}
        if len(free_rn_choices) == 1:
            context['empty_trucks'] = True
        return render(request, 'add_order.html', context)

    elif request.method == 'POST':
        updated_order = functions.get_order(order_id)
        form = forms.Order(request.POST)

        if form.is_valid():
            updated_order.load_place = form.cleaned_data['load_place']
            updated_order.unload_place = form.cleaned_data['unload_place']
            updated_order.cargo = form.cleaned_data['cargo']
            updated_order.weight = form.cleaned_data['weight']
            updated_order.transport = form.cleaned_data['transport']
            updated_order.rates = form.cleaned_data['rates']
            updated_order.tax = form.cleaned_data['tax']
            updated_order.save()

            return redirect('orders')


def completed_order(request, order_id):
    if request.method == 'GET':
        updated_order = functions.get_order(order_id)
        updated_order.completed = True
        updated_order.save()
        return redirect('orders')


def delete_order(request, order_id):
    if request.method == 'GET':
        order = functions.get_order(order_id)
        order.delete()
        return redirect('orders')


def add_transport(request):
    if request.method == 'GET':
        add_from = forms.Transport()
        context = {'form': add_from}
        return render(request, 'add_transport.html', context)

    elif request.method == 'POST':
        form = forms.Transport(request.POST)
        new_transport = models.Transport()

        if form.is_valid():
            new_transport.reg_number = form.cleaned_data['reg_number']
            new_transport.brand = form.cleaned_data['brand']
            new_transport.model = form.cleaned_data['model']
            new_transport.carrying = form.cleaned_data['carrying']
            new_transport.save()

            return redirect('transport')


def edit_transport(request, truck_id):
    if request.method == 'GET':
        truck = functions.get_truck(truck_id)
        edit_form = forms.Transport(initial={'reg_number': truck.reg_number,
                                             'brand': truck.brand,
                                             'model': truck.model,
                                             'carrying': truck.carrying})
        context = {'form': edit_form, 'action': 'edit', 'truck_id': truck.id}
        return render(request, 'add_transport.html', context)

    elif request.method == 'POST':
        updated_truck = functions.get_truck(truck_id)
        form = forms.Transport(request.POST)

        if form.is_valid():
            updated_truck.reg_number = form.cleaned_data['reg_number']
            updated_truck.brand = form.cleaned_data['brand']
            updated_truck.model = form.cleaned_data['model']
            updated_truck.carrying = form.cleaned_data['carrying']
            updated_truck.save()

            return redirect('transport')


def delete_truck(request, truck_id):
    if request.method == 'GET':
        truck = functions.get_truck(truck_id)
        truck.delete()
        return redirect('transport')
