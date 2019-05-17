import datetime
from dateutil.relativedelta import relativedelta

def initial_date(request, months=3):
    #gets the initial last three months or the session date
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


def date_range_filter(request):
    date_start, date_end = datetime.datetime.now().replace(day=1, month=1),\
                           datetime.datetime.now().replace(day=31, month=12)
    date_pick = request.GET.get('date_pick', None)
    date_range = None
    try:
        date_range = date_pick.split('-')
        date_range[0] = date_range[0].replace(' ', '')
        date_range[1] = date_range[1].replace(' ', '')
        date_start = datetime.datetime.strptime(date_range[0], '%m/%d/%Y')
        date_end = datetime.datetime.strptime(date_range[1], '%m/%d/%Y')
    except:
        date_start, date_end, date_range = [date_start, date_end, date_range] if date_start and date_end else \
            initial_date(request)
    if date_start > date_end:
        date_start, date_end = datetime.datetime.now().replace(day=1, month=1), datetime.datetime.now().replace(day=31,
                                                                                                                month=12
                                                                                                                )
    return date_start, date_end