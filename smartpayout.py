import json
import requests

__author__ = 'danolsen'

api_endpoint = 'http://local.smartpayout.com:8123/api/'

def get_cart(cart_id, user_token=None):
    pass

def add_product(cart_id, product_id, quantity, user_token=None):
    url = '{}carts/{}/add_product/'.format(api_endpoint, cart_id)
    headers = {}
    if user_token:
        headers['Authorization'] = 'Token {}'.format(user_token)

    payload = {'product': product_id, 'quantity': quantity}
    resp = requests.post(url, data=payload, headers=headers)

    return resp

def remove_product(cart_id, product_id, user_token=None):
    pass

def login(username, password):
    pass

