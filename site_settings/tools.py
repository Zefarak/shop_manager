import datetime
from dateutil.relativedelta import relativedelta
from django_tables2 import RequestConfig


def initial_date(request, months=3):
    date_now = datetime.datetime.today()
    try:
        date_range = request.session['date_range']
        date_range = date_range.split('-')
        date_range[0] = date_range[0].replace(' ','')
        date_range[1] = date_range[1].replace(' ','')
        date_start = datetime.datetime.strptime(date_range[0], '%m/%d/%Y')
        date_end = datetime.datetime.strptime(date_range[1],'%m/%d/%Y')
    except:
        date_three_months_ago = date_now - relativedelta(months=months)
        date_start = date_three_months_ago
        date_end = date_now
        date_range = '%s - %s' % (str(date_three_months_ago).split(' ')[0].replace('-','/'),str(date_now).split(' ')[0].replace('-','/'))
        request.session['date_range'] = '%s - %s'%(str(date_three_months_ago).split(' ')[0].replace('-','/'),str(date_now).split(' ')[0].replace('-','/'))
    return [date_start, date_end, date_range]


def clean_date_filter(request, date_pick, date_start=None, date_end=None, date_range=None):
    try:
        date_range = date_pick.split('-')
        date_range[0] = date_range[0].replace(' ', '')
        date_range[1] = date_range[1].replace(' ', '')
        date_start = datetime.datetime.strptime(date_range[0], '%m/%d/%Y')
        date_end = datetime.datetime.strptime(date_range[1], '%m/%d/%Y')
        date_range = '%s - %s' % (date_range[0], date_range[1])
    except:
        date_start, date_end, date_range = [date_start, date_end, date_range] if date_start and date_end else \
            initial_date(request)
    return [date_start, date_end, date_range]


def estimate_date_start_end_and_months(request):
    day_now, start_year = datetime.datetime.now(), datetime.datetime(datetime.datetime.now().year, 1, 1)
    date_pick = request.GET.get('daterange', None)
    start_year, day_now, date_range = clean_date_filter(request, date_pick, date_start=start_year, date_end=day_now)
    months_list = 12
    return [start_year, day_now, date_range, months_list]


def list_view_table(request, context, table, filters, data):
    queryset_table = table
    RequestConfig(request).configure(queryset_table)
    for filter in filters:
        filter = True
    for key, value in data.items():
        key = value
    context.update(locals())