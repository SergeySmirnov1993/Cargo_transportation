import requests
import json
from django.db.models import Q

from transportation import models

OSRM_SEARCH = 'https://nominatim.openstreetmap.org/search?city={}&format=json&polygon=1&addressdetails=1&type=administrative'
OSRM_ROUTE = 'https://router.project-osrm.org/route/v1/driving/{}?overview=false'
KM_PRICE = 30


def get_order(order_id):
    return models.Order.objects.get(id=order_id)


def get_orders_by_reg_num(reg_num):
    return models.Order.objects.filter(transport__in=reg_num)


def get_not_completed_orders():
    return models.Order.objects.exclude(completed=True)


def get_orders_by_places(load_place, unload_place):
    return models.Order.objects.filter(Q(Q(load_place=load_place) & Q(unload_place=unload_place))
                                       | Q(Q(load_place=unload_place) & Q(unload_place=load_place)))


def get_free_orders():
    return models.Order.objects.filter(transport__in=(None, ''))


def get_truck(truck_id):
    return models.Transport.objects.get(id=truck_id)


def get_truck_by_numbers(reg_numbers):
    return models.Transport.objects.filter(reg_number__in=reg_numbers)


def get_all_trucks():
    return models.Transport.objects.order_by('id').all()


def get_free_trucks():
    exclude_vals = get_busy_reg_num()
    trucks = models.Transport.objects.exclude(reg_number__in=exclude_vals)
    return trucks


def get_busy_trucks():
    reg_nums = get_busy_reg_num()
    trucks = models.Transport.objects.filter(reg_number__in=reg_nums)
    return trucks


def get_all_reg_num():
    trucks = get_all_trucks()
    all_rn = set()
    for truck in trucks:
        all_rn.add(truck.reg_number)
    return all_rn


def get_busy_reg_num():
    orders = get_not_completed_orders()
    busy_rn = set()
    for order in orders:
        if order.transport != '':
            busy_rn.add(order.transport)
    return busy_rn


def get_reg_num_choices():
    busy_trucks_rn = get_busy_reg_num()
    all_trucks_rn = get_all_reg_num()
    free_trucks_rn = all_trucks_rn - busy_trucks_rn
    all_trucks_rn.add('')
    free_trucks_rn.add('')
    free_rn_choices = tuple((i, i) for i in free_trucks_rn)
    all_rn_choices = tuple((i, i) for i in all_trucks_rn)
    data = {'free_rn_choices': free_rn_choices, 'all_rn_choices': all_rn_choices}
    return data


def convert_time(sec):
    days = sec // (24 * 3600)
    hours = (sec % (24 * 3600)) // 3600
    sec %= 3600
    min = sec // 60
    time = ''
    if days > 0:
        time = f'{days} д '
    if hours > 0:
        time += f'{hours} ч '
    if min > 0:
        time += f'{min} мин'
    return time


def get_coordinates(locality):
    response = requests.get(OSRM_SEARCH.format(locality))
    locations_data = json.loads(response.content)
    for location in locations_data:
        if location['display_name'].find('Беларусь') and location['type'] == 'administrative':
            coordinates = (location["lon"], location["lat"])
            return coordinates


def get_distance_data(*args):
    coordinates = ''
    for i in range(len(args)):
        coordinates += f'{args[i][0]},{args[i][1]};'
    coordinates = coordinates[:-2]
    response = requests.get(OSRM_ROUTE.format(coordinates))
    data = json.loads(response.content)
    distance = data["routes"][0]["distance"]
    duration = data["routes"][0]["duration"]
    return distance, duration


def orders_calculations(first_location, second_location):
    first_points = get_coordinates(first_location)
    second_points = get_coordinates(second_location)
    data = get_distance_data(first_points, second_points)
    distance, duration = data[0], data[1]
    rates = int(KM_PRICE * (distance / 1000))
    return rates, duration


def get_truck_for_additional_order(order_id):
    current_order = get_order(order_id)
    same_dir_orders = get_orders_by_places(current_order.load_place, current_order.unload_place)

    if same_dir_orders:
        same_dir_rn = {}
        for order in same_dir_orders:
            if order.transport in same_dir_rn:
                same_dir_rn[order.transport] += order.weight
            else:
                same_dir_rn[order.transport] = order.weight

        trucks = get_truck_by_numbers(same_dir_rn.keys())
        reg_num = {}

        for truck in trucks:
            residual_weight = truck.carrying - current_order.weight - same_dir_rn[truck.reg_number]
            if residual_weight > 0:
                reg_num[truck.reg_number] = residual_weight

        data = tuple((key, key) for key in reg_num)
        return data

    return None

