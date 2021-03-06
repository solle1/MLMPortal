import json
import requests
import rollbar

from utils import get_user_token

__author__ = 'danolsen'

API_ENDPOINT = 'http://smartpayout-dev.elasticbeanstalk.com/api/'
# API_ENDPOINT = 'http://local.smartpayout.com:8123/api/'

def register(first_name, last_name, username, email, password, slug, *args, **kwargs):
    payload = {
        'first_name': first_name,
        'last_name': last_name,
        'username': username,
        'email': email,
        'password': password,
        'upline_slug': slug,
    }

    heard_from = kwargs.get('heard_from', None)
    if heard_from:
        payload['metadata'] = json.dumps({'heard_from': heard_from})

    resp = requests.post('{}users/'.format(API_ENDPOINT), data=payload)
    return resp

def valid_slug(slug):
    payload = {
        'slug': slug,
    }
    resp = requests.post('{}users/slugs/'.format(API_ENDPOINT), data=payload)
    data = json.loads(resp.content)
    return data


def add_user_slug(slug, ident, request, session, user_token=None):
    user_token = get_user_token(request, session)

    headers = {}
    if user_token:
        headers['Authorization'] = 'Token {}'.format(user_token)

    payload = {
        'ident': ident,
        'slug': slug,
    }

    resp = requests.post('{}users/add_slug/'.format(API_ENDPOINT), data=payload, headers=headers)

    return resp.status_code, resp.content

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
        # rollbar.report_message(resp.url, 'debug')
        # rollbar.report_message('Status Code: {}'.format(resp.status_code), 'info')
        # rollbar.report_message('Content: \n{}'.format(resp.content), 'info')
        cart = json.loads(resp.content)
        session['cart_id'] = cart['id']
        pass

    return resp.content

def get_products(include_specialist=False, ignore_non_specialist=False):
    url_params = '?'
    if include_specialist:
        url_params = '{}include_specialist=true&'.format(url_params)
    if ignore_non_specialist:
        url_params = '{}ignore_non_specialist=true&'.format(url_params)

    if len(url_params) > 1:
        response = requests.get('{}products/{}'.format(API_ENDPOINT, url_params))
    else:
        response = requests.get('{}products/'.format(API_ENDPOINT))
    return response.content

def get_product(slug=None):
    if slug:
        response = requests.get('{}products/details/{}/'.format(API_ENDPOINT, slug))
    else:
        response = None
    return response.content


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

def get_user_locker(user_token):
    info = get_user_info(user_token)
    user_id = info['id']



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

def process_order(user_token, order_id, card_id, sollesafe=False):
    headers = {}
    if user_token:
        headers = {'Authorization': 'Token {}'.format(user_token)}

    payload = {
        'card': card_id,
        'autoship': sollesafe,
    }

    resp = requests.post('{}orders/{}/process_order/'.format(API_ENDPOINT, order_id), data=payload, headers=headers)

    return resp

def create_autoship(user_token, order_id, card_id, day):
    headers = {}
    if user_token:
        headers = {'Authorization': 'Token {}'.format(user_token)}

    payload = {
        'card': card_id,
        'day': day,
    }

    resp = requests.post('{}orders/{}/create_autoship/'.format(API_ENDPOINT, order_id), data=payload, headers=headers)

    return resp

def get_orders(user_token):
    headers = {}
    if user_token:
        headers = {'Authorization': 'Token {}'.format(user_token)}

    resp = requests.get('{}users/orders/'.format(API_ENDPOINT), headers=headers)

    return json.loads(resp.content)

def get_order(user_token, order_id):
    headers = {}
    if user_token:
        headers = {'Authorization': 'Token {}'.format(user_token)}

    resp = requests.get('{}orders/{}/'.format(API_ENDPOINT, order_id), headers=headers)

    return resp.status_code, json.loads(resp.content)

def get_shipping_options(sub_total):
    payload = {
        'sub_total': sub_total,
    }

    resp = requests.post('{}shipping/options/from_subtotal/'.format(API_ENDPOINT), data=payload)

    return resp.status_code, json.loads(resp.content)

def login(username, password):
    payload = {
        'username': username,
        'password': password,
    }
    response = requests.post('{}login/'.format(API_ENDPOINT), data=payload)

    return response
    pass


def get_organization(user_token):
    headers = {}
    if user_token:
        headers = {'Authorization': 'Token {}'.format(user_token)}

    resp = requests.get('{}users/organization/'.format(API_ENDPOINT), headers=headers)

    return json.loads(resp.content)

def get_mentored(user_token):
    headers = {}
    if user_token:
        headers = {'Authorization': 'Token {}'.format(user_token)}

    resp = requests.get('{}users/mentored/'.format(API_ENDPOINT), headers=headers)

    return json.loads(resp.content)

def update_upline(user_token, mentored_id, new_upline_id):
    headers = {}
    if user_token:
        headers = {'Authorization': 'Token {}'.format(user_token)}

    payload = {
        'upline_id': new_upline_id,
    }

    resp = requests.post('{}users/{}/update_upline/'.format(API_ENDPOINT, mentored_id), data=payload, headers=headers)

    return json.loads(resp.content)

def get_monthly_qv(user_token):
    headers = {}
    if user_token:
        headers = {'Authorization': 'Token {}'.format(user_token)}

    resp = requests.get('{}users/monthly_qv/'.format(API_ENDPOINT), headers=headers)

    return json.loads(resp.content)


def get_monthly_ov(user_token):
    headers = {}
    if user_token:
        headers = {'Authorization': 'Token {}'.format(user_token)}

    resp = requests.get('{}users/monthly_ov/'.format(API_ENDPOINT), headers=headers)

    return json.loads(resp.content)


def get_monthly_enrollments(user_token):
    headers = {}
    if user_token:
        headers = {'Authorization': 'Token {}'.format(user_token)}

    resp = requests.get('{}users/monthly_enrollments/'.format(API_ENDPOINT), headers=headers)

    return json.loads(resp.content)


def get_monthly_enrollment_orders(user_token):
    headers = {}
    if user_token:
        headers = {'Authorization': 'Token {}'.format(user_token)}

    resp = requests.get('{}orders/monthly_enrollments_for_user/'.format(API_ENDPOINT), headers=headers)
    return json.loads(resp.content)

def get_monthly_ranking(user_token):
    headers = {}
    if user_token:
        headers = {'Authorization': 'Token {}'.format(user_token)}

    resp = requests.get('{}users/monthly_rank/'.format(API_ENDPOINT), headers=headers)
    return json.loads(resp.content)

def get_solle_rewards(user_token):
    headers = {}
    if user_token:
        headers = {'Authorization': 'Token {}'.format(user_token)}

    resp = requests.get('{}users/get_rewards/'.format(API_ENDPOINT), headers=headers)
    return json.loads(resp.content)

def apply_discount(user_token, order_id, discount_code):
    headers = {}
    if user_token:
        headers = {'Authorization': 'Token {}'.format(user_token)}

    payload = {
        'code': discount_code,
    }

    resp = requests.post('{}orders/{}/apply_discount/'.format(API_ENDPOINT, order_id), data=payload, headers=headers)
    return json.loads(resp.content)

def apply_rewards(user_token, order_id, reward_amt):
    headers = {}
    if user_token:
        headers = {'Authorization': 'Token {}'.format(user_token)}

    payload = {
        'amt': reward_amt,
    }

    resp = requests.post('{}orders/{}/apply_rewards/'.format(API_ENDPOINT, order_id), data=payload, headers=headers)
    return json.loads(resp.content)

def update_user_profile(user_token, user_id, profile):
    headers = {}
    if user_token:
        headers = {'Authorization': 'Token {}'.format(user_token)}

    payload = {
        'profile': json.dumps(profile),
    }

    resp = requests.post('{}users/{}/update_profile/'.format(API_ENDPOINT, user_id), data=payload, headers=headers)

    return json.loads(resp.content)

def add_payer_id(user_token, user_id, payer_id):
    headers = {}
    if user_token:
        headers = {'Authorization': 'Token {}'.format(user_token)}

    payload = {
        'payer_id': payer_id,
    }

    resp = requests.post('{}users/{}/update_payer_id/'.format(API_ENDPOINT, user_id), data=payload, headers=headers)

    return json.loads(resp.content)
