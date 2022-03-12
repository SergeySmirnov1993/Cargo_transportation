from django.db.models import Q
from transportation import models

YEAR = 'year'
MONTH = 'month'
QUARTER = 'quarter'


def number_of_transportation_by_months():
    all_orders = models.Order.objects.all().order_by('-created_date')
    monthly_data = {}
    for order in all_orders:
        created_month, created_year = order.created_date.month, order.created_date.year
        if created_year in monthly_data:
            if created_month in monthly_data[created_year]:
                monthly_data[created_year][created_month] += 1
            else:
                monthly_data[created_year][created_month] = 1
        else:
            monthly_data[created_year] = {created_month: 1}

    return monthly_data


def volume_rubles_by_months():
    all_orders = models.Order.objects.all().order_by('created_date')
    monthly_data = {}
    for order in all_orders:
        created_month, created_year = order.created_date.month, order.created_date.year
        if created_year in monthly_data:
            if created_month in monthly_data[created_year]:
                monthly_data[created_year][created_month] += order.rates
            else:
                monthly_data[created_year][created_month] = order.rates
        else:
            monthly_data[created_year] = {created_month: order.rates}

    return monthly_data


def process_data(data):
    table = []
    for key, val in data.items():
        year_data = {val: '0' for val in range(1, 13)}
        for k, v in val.items():
            if k in year_data.keys():
                year_data[k] = v
        row = [val for val in year_data.values()]
        row.append(key)
        table.append(row)
    return table


def process_data_for_charts(data):
    table = []
    years = [str(key) for key in sorted(data.keys())]
    title_row = ['Месяц'] + years
    table.append(title_row)
    jan = ['Январь']
    feb = ['Февраль']
    mar = ['Март']
    apr = ['Аперель']
    may = ['Май']
    jun = ['Июнь']
    jul = ['Июль']
    aug = ['Август']
    sep = ['Сентябрь']
    oct = ['Октябрь']
    nov = ['Ноябрь']
    dec = ['Декабрь']
    for year in years:
        months_data = data[int(year)]
        jan.append(months_data.get(1, 0))
        feb.append(months_data.get(2, 0))
        mar.append(months_data.get(3, 0))
        apr.append(months_data.get(4, 0))
        may.append(months_data.get(5, 0))
        jun.append(months_data.get(6, 0))
        jul.append(months_data.get(7, 0))
        aug.append(months_data.get(8, 0))
        sep.append(months_data.get(9, 0))
        oct.append(months_data.get(10, 0))
        nov.append(months_data.get(11, 0))
        dec.append(months_data.get(12, 0))
    table.extend([jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec])
    return table


def get_orders_per_month(month, year):
    return models.Order.objects.filter(Q(created_date__month=month) & Q(created_date__year=year))


def get_orders_per_year(year):
    return models.Order.objects.filter(created_date__year=year)


def get_orders_per_quarter(quarter, year):
    quarter_dic = {1: ('01', '03'), 2: ('04', '06'), 3: ('07', '09'), 4: ('10', '12')}

    if quarter == 1:
        val = quarter_dic[1]
    elif quarter == 2:
        val = quarter_dic[2]
    elif quarter == 3:
        val = quarter_dic[3]
    else:
        val = quarter_dic[4]

    return models.Order.objects.filter(Q(created_date__month__gte=val[0]) & Q(created_date__month__lte=val[1]) & Q(created_date__year=year))


def distribution_by_directions(period):
    orders = ''
    if YEAR in period:
        year = period[YEAR]
        orders = get_orders_per_year(year)

    elif MONTH in period:
        month, year = period[MONTH][0], period[MONTH][1]
        orders = get_orders_per_month(month, year)

    elif QUARTER in period:
        quarter, year = period[QUARTER][0], period[QUARTER][1]
        orders = get_orders_per_quarter(quarter, year)

    data = {}
    for oder in orders:
        if f'{oder.load_place}-{oder.unload_place}' in data.keys():
            data[f'{oder.load_place}-{oder.unload_place}'] += 1
        else:
            data[f'{oder.load_place}-{oder.unload_place}'] = 1

    data = [[key, val] for key, val in data.items()]

    return data
