import requests
import json
import locale
import pytz

from datetime import datetime
from django.db.models import Q

from transportation import models

OSRM_SEARCH = 'https://nominatim.openstreetmap.org/search?city={}&format=json&polygon=1&addressdetails=1&type=administrative'
OSRM_ROUTE = 'https://router.project-osrm.org/route/v1/driving/{}?overview=false'
NB_API = 'https://www.nbrb.by/api/exrates/rates?periodicity=0'
# USD_API = 'https://www.nbrb.by/api/exrates/rates/431?periodicity=0'
# RUB_API = 'https://www.nbrb.by/api/exrates/rates/456?periodicity=0'
# EUR_API = 'https://www.nbrb.by/api/exrates/rates/451?periodicity=0'

KM_PRICE = 30
locale.setlocale(locale.LC_ALL, "")


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


def get_trucks_by_numbers(reg_numbers):
    return models.Transport.objects.filter(reg_number__in=reg_numbers)


def get_all_trucks():
    return models.Transport.objects.order_by('id').all()


def get_all_drivers():
    return models.Driver.objects.order_by('id').all()


def get_driver(driver_id):
    return models.Driver.objects.get(id=driver_id)


def get_free_trucks():
    busy_trucks = get_busy_trucks()
    exclude_vals = set(truck.reg_number for truck in busy_trucks)
    trucks = models.Transport.objects.exclude(reg_number__in=exclude_vals)
    return trucks


def get_all_reg_num():
    trucks = get_all_trucks()
    all_rn = set()
    for truck in trucks:
        all_rn.add(truck.reg_number)
    return all_rn


def get_busy_trucks():
    orders = get_not_completed_orders()
    busy_trucks = set()
    for order in orders:
        if order.transport:
            busy_trucks.add(order.transport)
    return busy_trucks


def get_reg_num_choices():
    busy_trucks = get_busy_trucks()
    busy_trucks_rn = set(truck.reg_number for truck in busy_trucks)
    all_trucks_rn = get_all_reg_num()
    free_trucks_rn = all_trucks_rn - busy_trucks_rn
    all_trucks_rn.add('')
    free_trucks_rn.add('')
    free_rn_choices = tuple((i, i) for i in free_trucks_rn)
    all_rn_choices = tuple((i, i) for i in all_trucks_rn)
    data = {'free_rn_choices': free_rn_choices, 'all_rn_choices': all_rn_choices}
    return data


def get_drivers_choices():
    drivers = models.Driver.objects.order_by('id').all()
    drivers_names = set(f'{driver.name} {driver.surname}' for driver in drivers)
    drivers_names.add('')
    choices = tuple((name, name) for name in drivers_names)
    return choices


def get_trailer_choices():
    trailers = models.TruckTrailer.objects.filter(transport=None)
    choices = tuple((trailer.reg_number, trailer.reg_number) for trailer in trailers)
    return choices + (('', ''), )


def get_trailer_by_number(number):
    return models.TruckTrailer.objects.filter(reg_number=number).first()


def get_driver_by_name(name, surname):
    driver = models.Driver.objects.filter(Q(name=name) & Q(surname=surname)).first()
    return driver


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


def exchange_rate():
    response = requests.get(NB_API)
    data = json.loads(response.content)
    new_data = {}
    count = 0
    for val in data:
        if count == 3:
            break
        if val["Cur_ID"] == 431:
            new_data['USD'] = (val["Cur_OfficialRate"], val["Cur_Scale"])
            count += 1
        elif val["Cur_ID"] == 451:
            new_data['EUR'] = (val["Cur_OfficialRate"], val["Cur_Scale"])
            count += 1
        elif val["Cur_ID"] == 456:
            new_data['RUB'] = (val["Cur_OfficialRate"], val["Cur_Scale"])
            count += 1
    return new_data


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
            if order.transport:
                same_dir_rn[order.transport.reg_number] = order.weight

        trucks = get_trucks_by_numbers(same_dir_rn.keys())
        reg_num = {}

        for truck in trucks:
            residual_weight = truck.carrying - current_order.weight - same_dir_rn[truck.reg_number]
            if residual_weight > 0:
                reg_num[truck.reg_number] = residual_weight

        data = tuple((key, key) for key in reg_num)
        return data

    return None


def current_datetime():
    tz = pytz.timezone('Europe/Minsk')
    now = datetime.now(tz)
    format_datetime = now.strftime("%d %B %Y (%A)")
    return format_datetime

