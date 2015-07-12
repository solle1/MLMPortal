import json
import requests
from utils import get_user_token

__author__ = 'danolsen'

API_ENDPOINT = 'http://smartpayout-dev.elasticbeanstalk.com/api/'
# API_ENDPOINT = 'http://local.smartpayout.com:8123/api/'

def register(first_name, last_name, email, password):
    payload = {
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'password': password,
    }

    resp = requests.post('{}users/'.format(API_ENDPOINT), data=payload)
    return resp


def get_cart(request, session, user_token=None):
    user_token = get_user_token(request, session)
    cart_id = session.get('cart_id', None)

    headers = {}
    if user_token:
        headers['Authorization'] = 'Token {}'.format(user_token)
    # if 'cart' not in session:
    # if user_token:
    #     headers = {'Authorization': 'Token {}'.format(user_token)}

    if cart_id:
        resp = requests.get('{}carts/{}/'.format(API_ENDPOINT, cart_id), headers=headers)
        cart = json.loads(resp.content)
        pass
    else:
        resp = requests.get('{}{}'.format(API_ENDPOINT, 'carts/get_cart/'), headers=headers)
        cart = json.loads(resp.content)
        session['cart_id'] = cart['id']
        pass

    return resp.content

def get_user_info(user_token):
    headers = {}
    if user_token:
        headers = {'Authorization': 'Token {}'.format(user_token)}

    resp = requests.get('{}{}'.format(API_ENDPOINT, 'users/me/'), headers=headers)
    return json.loads(resp.content)[0]


def add_product(cart_id, product_id, quantity, user_token=None):
    url = '{}carts/{}/add_product/'.format(API_ENDPOINT, cart_id)
    headers = {}
    if user_token:
        headers['Authorization'] = 'Token {}'.format(user_token)

    payload = {'product': product_id, 'quantity': quantity}
    resp = requests.post(url, data=payload, headers=headers)

    return resp

def remove_product(cart_id, product_id, user_token=None):
    pass

def update_cart_quantities(cart_id, updates, user_token=None):
    url = '{}carts/{}/update_quantities/'.format(API_ENDPOINT, cart_id)
    headers = {}
    if user_token:
        headers['Authorization'] = 'Token {}'.format(user_token)

    payload = {'updates': updates}
    resp = requests.post(url, data=payload, headers=headers)

    return resp

def get_credit_cards(user_token):
    info = get_user_info(user_token)

    headers = {}
    if user_token:
        headers = {'Authorization': 'Token {}'.format(user_token)}

    resp = requests.get('{}users/{}/list_cards/'.format(API_ENDPOINT, info['id']), headers=headers)
    # resp.content = json.loads(resp.content)

    return resp.status_code, json.loads(resp.content)

def add_credit_card(user_token, card_number=None, name=None, exp_month=None, exp_year=None, cvc=None):
    info = get_user_info(user_token)

    headers = {}
    if user_token:
        headers = {'Authorization': 'Token {}'.format(user_token)}

    payload = {
        'card_number': card_number,
        'exp_month': exp_month,
        'exp_year': exp_year,
        'cvc': cvc,
    }

    resp = requests.post('{}users/{}/create_card/'.format(API_ENDPOINT, info['id']), headers=headers, data=payload)

    return resp

def process_order(user_token, order_id, card_id):
    headers = {}
    if user_token:
        headers = {'Authorization': 'Token {}'.format(user_token)}

    payload = {
        'card': card_id,
    }

    resp = requests.post('{}orders/{}/process_order/'.format(API_ENDPOINT, order_id), data=payload, headers=headers)

    return resp

def get_order(user_token, order_id):
    headers = {}
    if user_token:
        headers = {'Authorization': 'Token {}'.format(user_token)}

    resp = requests.get('{}orders/{}/'.format(API_ENDPOINT, order_id), headers=headers)

    return resp.status_code, json.loads(resp.content)

def login(username, password):
    payload = {
        'email': username,
        'password': password,
    }
    response = requests.post('{}login/'.format(API_ENDPOINT), data=payload)

    return response
    pass


