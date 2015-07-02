from datetime import datetime

__author__ = 'danolsen'

def datetimeformat(value, format='%Y-%m-%d %H:%M'):
    return value.strftime(format)

def stringtodate(value, format='%Y-%m-%dT%H:%M:%S.%fZ'):
    return datetime.strptime(value, format)

def remove_spaces(value):
    return value.replace(' ', '')

def item_retail_total(item):
    return '{0:.2f}'.format(item['quantity'] * float(item['product']['retail_price']))

def format_currency(value):
    return '${0:,.2f}'.format(float(value))


# REGULAR UTILITY FUNCTIONS
def get_user_token(request, session):
    return request.cookies.get('token', None)

