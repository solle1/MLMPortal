from datetime import datetime
from functools import wraps
from flask import request, redirect, session, Response
import requests

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

def qv(order):
    total_qv = 0
    for item in order['items']:
        total_qv += float(item['qualification_volume'])
    return total_qv

# REGULAR UTILITY FUNCTIONS
def get_user_token(request, session):
    return request.cookies.get('token', None)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_token = get_user_token(request, session)
        if not user_token:
            return redirect('/login/')
        return f(*args, **kwargs)
    return decorated_function


def ajax_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_token = get_user_token(request, session)
        if not user_token:
            response = Response({'detail': 'You are not authorized.'})
            response.status_code = 403
            return response
        return f(*args, **kwargs)
    return decorated_function
