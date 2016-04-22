import base64
import json
import os

import requests

PPTOKEN = os.environ['PPTOKEN']
PPBILLING = os.environ['PPBILLING']

API_ENDPOINT = 'https://api.propay.com/ProtectPay'
API_ENDPOINT = 'https://xmltestapi.propay.com/protectpay'


class ProPayException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class BadTempTokenException(ProPayException):
    def __init__(self, *args, **kwargs):
        ProPayException.__init__(self, *args, **kwargs)


class CreatePayerException(ProPayException):
    def __init__(self, *args, **kwargs):
        ProPayException.__init__(self, *args, **kwargs)


class PaymentMethodsException(ProPayException):
    def __init__(self, *args, **kwargs):
        ProPayException.__init__(self, *args, **kwargs)


def get_auth_token():
    token = base64.b64encode('{}:{}'.format(PPBILLING, PPTOKEN))
    return token


def get_url(uri):
    return '{}{}'.format(API_ENDPOINT, uri)


def get_temp_token(duration=600):
    """ Get a temp token for an API call. """
    url = '{}/TempTokens/?durationSeconds={}'.format(API_ENDPOINT, duration)
    token = base64.b64encode('{}:{}'.format(PPBILLING, PPTOKEN))

    headers = {'Authorization': 'Basic {}'.format(token)}
    resp = requests.get(url, headers=headers)

    resp_content = json.loads(resp.content)
    success = resp_content['RequestResult']['ResultValue'].lower() == 'success'
    if success is True:
        temp_token = {'credential_id': resp_content['CredentialId'], 'temp_token': resp_content['TempToken'], 'payer_id': resp_content['PayerId']}
    else:
        raise BadTempTokenException(
            'Request for Temp Token failed: {}'.format(resp_content['RequestResult']['ResultMessage']))
    return temp_token


def is_valid_response(content):
    if 'RequestResult' in content:
        success = content['RequestResult']['ResultValue'].lower() == 'success'
    else:
        success = content['ResultValue'].lower() == 'success'
    return success


def get_response_message(content):
    return content['RequestResult']['ResultMessage']


def create_a_payer(user_id, email, firstname, lastname):
    """ Create a new payer. """
    url = '{}/Payers/'.format(API_ENDPOINT)
    temp_token = get_temp_token()

    token = base64.b64encode('{}:{}'.format(PPBILLING, PPTOKEN))
    headers = {'Authorization': 'Basic {}'.format(token)}
    data = {
        'AuthenticationToken': temp_token,
        'BillerAccountId': PPBILLING,
        'EmailAddress': email,
        'Name': '{} {}'.format(firstname, lastname),
        'ExternalId1': user_id,
    }
    resp = requests.put(url, headers=headers, data=data)

    resp_content = json.loads(resp.content)
    success = resp_content['RequestResult']['ResultValue'].lower() == 'success'
    if success is True:
        account_id = resp_content['ExternalAccountID']
    else:
        raise CreatePayerException('Failed to create payer: {}'.format(resp_content['RequestResult']['ResultMessage']))

    return account_id


def edit_a_payer(payer_id, user_id, email, firstname, lastname):
    url = '{}/Payers/{}/'.format(API_ENDPOINT, payer_id)
    temp_token = get_temp_token()

    token = get_auth_token()
    headers = {'Authorization': 'Basic {}'.format(token)}

    data = {
        'PayerAccountId': payer_id,
        'EmailAddress': email,
        'Name': '{} {}'.format(firstname, lastname),
        'ExternalId1': user_id,
    }
    resp = requests.post(url, headers=headers, data=data)

    print resp


def get_payment_methods(payer_id):
    url = get_url('/Payers/{}/PaymentMethods/'.format(payer_id))
    token = get_auth_token()

    headers = {'Authorization': 'Basic {}'.format(token)}
    data = {
        'payerAccountId': payer_id,
    }

    resp = requests.get(url, headers=headers)
    resp_content = json.loads(resp.content)
    if is_valid_response(resp_content):
        methods = resp_content['PaymentMethods']
    else:
        raise PaymentMethodsException('Error retrieving payment methods: {}'.format(get_response_message(resp_content)))

    return methods



def create_payment_method(payer_id, card_number, exp_date):
    """ DO NOT RUN THIS ON SERVER! THIS IS FOR TESTS ONLY!"""
    url = get_url('/Payers/{}/PaymentMethods/'.format(payer_id))
    token = get_auth_token()

    headers = {'Authorization': 'Basic {}'.format(token)}
    data = {
        'PayerAccountId': payer_id,
        'AccountNumber': card_number,
        'PaymentMethodType': 'Visa',
        'ExpirationDate': exp_date,
    }

    resp = requests.put(url, headers=headers, data=data)
    resp_content = json.loads(resp.content)
    if is_valid_response(resp_content):
        method = resp_content['PaymentMethodId']
    else:
        raise PaymentMethodsException('Error creating a payment method: {}'.format(get_response_message(resp_content)))

    return method


def delete_payment_method(payer_id, method_id):
    url = get_url('/Payers/{}/PaymentMethods/{}/'.format(payer_id, method_id))
    token = get_auth_token()

    headers = {'Authorization': 'Basic {}'.format(token)}

    resp = requests.delete(url, headers=headers)
    resp_content = json.loads(resp.content)
    if is_valid_response(resp_content):
        success = True
    else:
        success = False

    return success
