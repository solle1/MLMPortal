#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import datetime
from flask import Flask, render_template, request, redirect, abort, g, session, Response, make_response, jsonify
from flask.ext.babel import Babel
from flask.ext.bootstrap import Bootstrap
import requests

from requests import Request, Session
import smartpayout
from utils import datetimeformat, stringtodate, remove_spaces, get_user_token

app = Flask(__name__)
Bootstrap(app)
# app.config['API_ENDPOINT'] = 'http://demo.smartpayout.com/api/'
app.config['API_ENDPOINT'] = 'http://smartpayout-dev.elasticbeanstalk.com/api/'
app.config['LANGUAGES'] = {'en': u'English', 'es': u'Español'}
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
babel = Babel(app)

ADMINS = ['dan@straightbit.com']
import logging
from logging.handlers import SMTPHandler

mail_handler = SMTPHandler('127.0.0.1',
                           'server-error@straightbit.com',
                           ADMINS, 'Your Application Failed')
mail_handler.setLevel(logging.ERROR)
app.logger.addHandler(mail_handler)

app.jinja_env.filters['datetimeformat'] = datetimeformat
app.jinja_env.filters['stringtodate'] = stringtodate
app.jinja_env.filters['remove_spaces'] = remove_spaces


@babel.localeselector
def get_locale():
    """Direct babel to use the language defined in the session."""
    return session.get('current_lang', 'en')


@app.before_request
def before():
    if request.view_args and 'lang_code' in request.view_args:
        if request.view_args['lang_code'] not in ('es', 'en'):
            return abort(404)
        g.current_lang = request.view_args['lang_code']
        session['current_lang'] = request.view_args['lang_code']
        request.view_args.pop('lang_code')


@app.route('/')
def landing():
    return render_template('index.html', showcart=True)


@app.route('/language/<lang_code>/')
def language():
    # session['lang'] = request.view_args['lang_code']
    next = request.args.get('next', '/home/')
    return redirect(next)


@app.route('/login/')
def login():
    token = request.cookies.get('token')
    if token:
        return redirect('/home/')
    next = request.args.get('next', '/home/')
    registered = request.args.get('registered', None)
    unauth = request.args.get('unauth', None)

    redirected = False
    if unauth:
        redirected = True

    return render_template('login.html', next=next, redirected=redirected, registered=registered)


@app.route('/logout/')
def logout():
    return render_template('logout.html')


@app.route('/home/')
def home():
    return render_template('index.html', showcart=True)


@app.route('/register/')
def register():
    return render_template('register.html')


@app.route('/profile/')
def profile():
    states_response = requests.get('%s%s' % (app.config['API_ENDPOINT'], 'states'))
    states = json.loads(states_response.content)
    return render_template('profile.html', showcart=True, states=states)


@app.route('/products/')
def products():
    response = requests.get('%s%s' % (app.config['API_ENDPOINT'], 'products'))
    products = json.loads(response.content)

    for product in products:
        group_list = []
        for group in product['groups']:
            group_list.append(group['name'].replace(' ', ''))
        product['group_list'] = " ".join(group_list)

    response = requests.get('%s%s' % (app.config['API_ENDPOINT'], 'products/groups/'))
    groups = json.loads(response.content)

    return render_template('products.html', products=products, groups=groups, showcart=True)


@app.route('/cart/')
def cart():
    cart = None

    user_token = get_user_token(request, session)

    if user_token:
        response = requests.get('%s%s' % (app.config['API_ENDPOINT'], 'carts/get_cart/'),
                                headers={'Authorization': 'Token %s' % user_token})
    else:
        response = requests.get('%s%s' % (app.config['API_ENDPOINT'], 'carts/get_cart/'))

    cart = json.loads(response.content)

    return render_template('cart.html', cart=cart)

@app.route('/ajax/login/')
def ajax_login():
    # response = requests.get('{}{}'.format(app.config['API_ENDPOINT'], '']))
    pass

@app.route('/ajax/get_cart/')
def get_cart():
    # TODO: If we have a cart we need to fetch the latest for the cart. If they login we need to make sure the cart gets updated with the logged in user.
    user_token = get_user_token(request, session)
    headers = {}
    if user_token:
        headers['Authorization'] = 'Token {}'.format(user_token)
    if 'cart' not in session:
        if user_token:
            headers = {'Authorization': 'Token {}'.format(user_token)}

        resp = requests.get('{}{}'.format(app.config['API_ENDPOINT'], 'carts/get_cart/'), headers=headers)
        session['cart'] = resp.content
    else:
        cart = json.loads(session['cart'])
        if user_token:
            headers = {'Authorization': 'Token {}'.format(user_token)}

        cart_url = '{}{}/{}/'.format(app.config['API_ENDPOINT'], 'carts', cart['id'])
        resp = requests.get(cart_url, headers=headers)
        session['cart'] = resp.content
    cart = json.loads(session['cart'])

    resp = jsonify(cart)
    resp.status_code = 200
    return resp

@app.route('/ajax/add_product/<int:cart_id>/', methods=['POST'])
def add_product(cart_id):
    user_token = get_user_token(request, session)

    product_id = request.form.get('product', type=int)
    quantity = request.form.get('quantity', type=int)

    response = smartpayout.add_product(cart_id, product_id, quantity, user_token)

    resp = jsonify(json.loads(response.content))
    resp.status_code = response.status_code
    return resp

@app.context_processor
def inject_user():
    context = {'loggedin': False}

    token = request.cookies.get('token', None)
    if token and request.path != '/login/':
        response = requests.get('%s%s' % (app.config['API_ENDPOINT'], 'users/me/'),
                                headers={'Authorization': 'Token %s' % token})
        if response.status_code == 401:
            context['redirect'] = '/login/?next=%s' % request.path
        response = json.loads(response.content)

        context['user'] = response[0]
        context['loggedin'] = True

    return context


@app.context_processor
def inject_language():
    context = {'language': session.get('current_lang', 'en')}

    return context


@app.context_processor
def inject_year():
    context = {'year': datetime.datetime.now().strftime('%Y')}

    return context


@app.context_processor
def inject_cart():
    # api_cookies = session.get('api_cookies', None)
    # user_token = get_user_token(request, session)
    # headers = {}
    # s = Session()
    # # if user_token:
    # #     headers['Authorization'] = 'Token %s' % user_token
    #
    # # req = Request('GET', '%s%s' % (app.config['API_ENDPOINT'], 'carts/get_cart/'),
    # #               headers=headers, cookies=api_cookies)
    # # prepped = s.prepare_request(req)
    # #
    # # resp = s.send(prepped)
    # #
    # # session['api_cookies'] = resp.cookies
    #
    # # cart_id = session.get('cart_id', None)
    # # if not cart_id:
    # # TODO: Need to check if the person is logged in. If they are, then we need to get their latest cart.
    # # TODO: We also need to grab the latest cart from the session. That way if they filled their cart before
    # # TODO: logging in they won't lose it. If the do login we need to make their new cart their cart and close
    # # TODO: out any existing carts.
    #
    # try:
    #     response = requests.get('%s%s' % (app.config['API_ENDPOINT'], 'carts/get_cart/'), cookies=api_cookies)
    #     session['api_cookies'] = response.cookies
    #     data = json.loads(response.content)
    #     cart_id = data['id']
    #     session['cart_id'] = cart_id
    #     if response.status_code != 200:
    #         raise Exception('Could not get a cart. Try creating an account.')
    # except requests.ConnectionError as e:
    #     cart_id = 0
    # #
    # context = {'cart_id': cart_id}
    context = {}
    return context


if __name__ == '__main__':
    # app.config['API_ENDPOINT'] = 'http://catchmycommission.com/api/v1/'

    app.run(debug=True)
