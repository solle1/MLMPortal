import json
import logging
import os

import requests
import rollbar

import bank
import smartpayout

API_ENDPOINT = 'http://test.smartlockout.com/'
# API_ENDPOINT = 'http://127.0.0.1:9000/'
api_key = os.environ['LOCKER']

# def submit_banking(user_token, routing_number, account_number):
#     # TODO: Get the unique identifier.
#     user_info = smartpayout.get_user_info(user_token)
#
#     headers = {'Authorization': 'Token {}'.format(api_key)}
#
#     if 'locker' in user_info['profile']:
#         locker = user_info['profile']['locker']
#     else:
#         # TODO: Create a user by sending the information
#         locker = None
#
#     payload = {
#         'customer': locker,
#         'rtn': routing_number,
#         'atn': account_number,
#     }
#
#     resp = requests.post('{}customers/'.format(API_ENDPOINT), data=payload, headers=headers)
#     resp_content = json.loads(resp.content)
#
#     if locker != resp_content['id']:
#         user_info['profile']['locker'] = resp_content['id']
#         resp = smartpayout.update_user_profile(user_token, user_info['id'], user_info['profile'])
#
#     return True
#
# def submit_tin(user_token, tin):
#     user_info = smartpayout.get_user_info(user_token)
#
#     headers = {'Authorization': 'Token {}'.format(api_key)}
#
#     if 'locker' in user_info['profile']:
#         locker = user_info['profile']['locker']
#     else:
#         locker = None
#
#     payload = {
#         'customer': locker,
#         'tin': tin,
#     }
#
#     resp = requests.post('{}customers/'.format(API_ENDPOINT), data=payload, headers=headers)
#     resp_content = json.loads(resp.content)
#
#     if locker != resp_content['id']:
#         user_info['profile']['locker'] = resp_content['id']
#         resp = smartpayout.update_user_profile(user_token, user_info['id'], user_info['profile'])
#
#     return True

def submit_data(user_token, *args, **kwargs):
    user_info = smartpayout.get_user_info(user_token)

    headers = {'Authorization': 'Token {}'.format(api_key)}

    if 'locker' in user_info['profile']:
        locker = user_info['profile']['locker']
    else:
        locker = None

    payload = {'customer': locker}

    tin = kwargs.get('tin', None)
    rtn = kwargs.get('rtn', None)
    atn = kwargs.get('atn', None)

    if tin:
        payload['tin'] = tin
    if rtn:
        payload['rtn'] = rtn
    if atn:
        payload['atn'] = atn

    resp = requests.post('{}customers/'.format(API_ENDPOINT), data=payload, headers=headers)
    resp_content = json.loads(resp.content)

    if locker != resp_content['id']:
        user_info['profile']['locker'] = resp_content['id']
        resp = smartpayout.update_user_profile(user_token, user_info['id'], user_info['profile'])

    return True
