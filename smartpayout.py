import json
import requests

__author__ = 'danolsen'

API_ENDPOINT = 'http://smartpayout-dev.elasticbeanstalk.com/api/'

def get_cart(cart_id, user_token=None):
    pass

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

def login(username, password):
    pass
