#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import datetime
import os

import rollbar
import rollbar.contrib.flask
from flask import Flask, render_template, request, redirect, abort, g, session, jsonify, Response, make_response, \
    got_request_exception
from flask.ext.babel import Babel
from flask.ext.bootstrap import Bootstrap
import requests
import sys
from werkzeug.contrib.cache import SimpleCache

import smartpayout
from utils import datetimeformat, stringtodate, remove_spaces, item_retail_total, format_currency, get_user_token, \
    login_required, qv, format_two_decimals

app = Flask(__name__)
Bootstrap(app)
# app.config['API_ENDPOINT'] = 'http://demo.smartpayout.com/api/'
# app.config['API_ENDPOINT'] = 'http://smartpayout-dev.elasticbeanstalk.com/api/'
# app.config['API_ENDPOINT'] = 'http://local.smartpayout.com:8123/api/'
app.config['API_ENDPOINT'] = smartpayout.API_ENDPOINT

app.config['LANGUAGES'] = {'en': u'English', 'es': u'Español'}
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
babel = Babel(app)

ADMINS = ['dan@straightbit.com']
DEFAULT_SLUG = 'solle'
INVALID_SLUGS = ['products', 'login', 'logout', 'ajax', 'home', 'register', 'profile', 'language', 'cart', 'checkout',
                 'specialist', 'favicon.ico', 'about', 'reports']
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
app.jinja_env.filters['item_retail_total'] = item_retail_total
app.jinja_env.filters['format_currency'] = format_currency
app.jinja_env.filters['format_two_decimals'] = format_two_decimals
app.jinja_env.filters['qv'] = qv


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


@app.route('/<slug>/')
def landing(slug):
    session['slug'] = slug
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
    if 'cart_id' in session:
        del session['cart_id']
    return render_template('logout.html')


@app.route('/<slug>/home/')
def home(slug):
    return render_template('index.html', showcart=True)

@app.route('/<slug>/register/about/')
def register_about(slug):
    return render_template('register_about.html')

@app.route('/<slug>/register/<type>/')
def register(slug, type):
    response = smartpayout.valid_slug(slug)
    if type.lower() == 'specialist':
        specialist = True
    else:
        specialist = False

    if response['identifier']:
        identity = response['identifier']
    else:
        identity = response['name']

    response = make_response(render_template('register.html', slug=slug, identity=identity, specialist=specialist, type=type.lower()))
    response.set_cookie('slug', value=slug)
    return response

@app.route('/<slug>/about/')
def about(slug):
    return render_template('about.html', showcart=False)

@app.route('/<slug>/comp_plan/')
def comp_plan(slug):
    return render_template('comp_plan.html', showcart=False)

@app.route('/<slug>/contact/')
def contact(slug):
    return render_template('contact.html', showcart=False)

@app.route('/profile/')
@login_required
def profile():
    states_response = requests.get('%s%s' % (app.config['API_ENDPOINT'], 'states'))
    states = json.loads(states_response.content)
    return render_template('profile.html', showcart=True, states=states)


@app.route('/<slug>/products')
def products(slug):
    session['slug'] = slug
    response = smartpayout.get_products() #requests.get('%s%s' % (app.config['API_ENDPOINT'], 'products'))
    products = json.loads(response)

    for product in products:
        group_list = []
        for group in product['groups']:
            group_list.append(group['name'].replace(' ', ''))
        product['group_list'] = " ".join(group_list)

    response = requests.get('%s%s' % (app.config['API_ENDPOINT'], 'products/groups/'))
    groups = json.loads(response.content)

    response = make_response(render_template('products.html', products=products, groups=groups, showcart=True, slug=slug))
    response.set_cookie('slug', value=slug)
    return response

@app.route('/<slug>/products/<product_slug>/')
def product_details(slug, product_slug):
    product = smartpayout.get_product(product_slug)
    return render_template('products/{}.html'.format(product_slug), product=product)


@app.route('/<slug>/cart/')
def cart(slug):
    cart = None

    user_token = get_user_token(request, session)

    if user_token:
        response = smartpayout.get_cart(request, session,
                                        user_token)  # requests.get('%s%s' % (app.config['API_ENDPOINT'], 'carts/get_cart/'),
        # headers={'Authorization': 'Token %s' % user_token})
        user = smartpayout.get_user_info(user_token)  # requests.get('%s%s' % (app.config['API_ENDPOINT'], 'users/'),
        # headers={'Authorization': 'Token %s' % user_token})
    else:
        response = smartpayout.get_cart(request, session,
                                        user_token)  # requests.get('%s%s' % (app.config['API_ENDPOINT'], 'carts/get_cart/'))
        user = None

    cart = json.loads(response)
    session['cart_id'] = cart['id']

    if user:
        addresses = json.dumps(user['addresses'])
    else:
        addresses = None

    state_response = requests.get('%s%s' % (app.config['API_ENDPOINT'], 'states/'))
    states = json.loads(state_response.content)
    status_code, shipping_options = smartpayout.get_shipping_options(cart['subtotal_price_field'])

    response = make_response(render_template('cart.html', cart=cart, user=user, states=states, addresses=addresses,
                                             shipping_options=shipping_options))
    response.set_cookie('slug', value=slug)
    return response


@app.route('/<slug>/checkout/', methods=['GET'])
@login_required
def checkout(slug):
    # Get the order!
    user_token = get_user_token(request, session)

    cart_id = session.get('cart_id', None)
    cart = json.loads(smartpayout.get_cart(request, session, user_token))


    if cart:
        response = requests.get('{}carts/{}/checkout/'.format(app.config['API_ENDPOINT'], cart['id']),
                                headers={'Authorization': 'Token {}'.format(user_token)})

        order = json.loads(response.content)

        return render_template('checkout.html', order=order)
    else:
        return redirect('/')


@app.route('/<slug>/specialist/signup/', methods=['GET'])
@login_required
def specialist_signup(slug):
    products = json.loads(smartpayout.get_products(include_specialist=True))

    specialist_products = []

    for product in products:
        if product['make_specialist']:
            specialist_products.append(product)

    return render_template('products.html', products=specialist_products, showcart=True, specialist_signup=True)


@app.route('/<slug>/specialist/setup/', methods=['GET'])
@login_required
def specialist_setup(slug):
    user_token = get_user_token(request, session)
    if not user_token:
        return redirect('/login/')
    response = make_response(render_template('specialist_setup.html'))
    response.set_cookie('slug', value=slug)
    return response

@app.route('/<slug>/specialist/dashboard/', methods=['GET'])
@login_required
def specialist_dashboard(slug):
    response = make_response(render_template('dashboard.html'))
    return response

@app.route('/<slug>/specialist/organization/', methods=['GET'])
@login_required
def organization(slug):
    user_token = get_user_token(request, session)
    if not user_token:
        return redirect('/login/')
    response = smartpayout.get_organization(user_token)
    org = response

    return render_template('organization.html', org=org, org_string=json.dumps(org))

@app.route('/<slug>/specialist/recent_enrollments/', methods=['GET'])
@login_required
def recent_enrollments(slug):
    user_token = get_user_token(request, session)
    if not user_token:
        return redirect('/login/')
    response = smartpayout.get_monthly_enrollment_orders(user_token)

    return render_template('recent_enrollments.html', orders=response)

@app.route('/<slug>/specialist/orders/', methods=['GET'])
@login_required
def specialist_orders(slug):
    return render_template('specialist_orders.html')

@app.route('/<slug>/specialist/wallet/', methods=['GET'])
@login_required
def wallet(slug):
    return render_template('wallet.html')

@app.route('/<slug>/specialist/wallet/settings/', methods=['GET'])
@login_required
def wallet_settings(slug):
    return render_template('wallet_settings.html')


@app.route('/<slug>/reports/growth/', methods=['GET'])
@login_required
def growth_report(slug):
    return render_template('reports/growth_report.html')

@app.route('/<slug>/reports/myspecialists/', methods=['GET'])
@login_required
def my_specialists_report(slug):
    return render_template('reports/my_specialists.html')

@app.route('/ajax/register/', methods=['post'])
def ajax_register():
    first_name = request.form.get('first_name', None)
    last_name = request.form.get('last_name', None)
    email = request.form.get('email', None)
    email_confirm = request.form.get('confirm-email', None)
    password = request.form.get('password', None)
    password_confirm = request.form.get('confirm-password', None)
    specialist = request.form.get('specialist', False) == 'true'
    slug = request.form.get('slug', None)

    result = {}

    errors = []

    if email != email_confirm:
        errors.append('Email fields do not match.')

    if password != password_confirm:
        errors.append('Password fields do not match.')

    if errors:
        result['success'] = False
        result['message'] = ' '.join(errors)
        result['fields'] = ' '.join(errors)
        resp = Response(json.dumps(result), mimetype='application/json')
        # resp.status_code = 400
    else:
        api_resp = smartpayout.register(first_name, last_name, email, password, slug)
        api_result = json.loads(api_resp.content)
        if api_resp.status_code == 201:
            api_result['specialist'] = specialist
            api_result['success'] = True
        else:
            api_result['success'] = False
            if 'email' in api_result:
                api_result['message'] = 'The email address is already in use.'

        resp = Response(json.dumps(api_result), mimetype='application/json')
        # resp.status_code = api_resp.status_code

    return resp


@app.route('/ajax/purchase/', methods=['post'])
def purchase():
    user_token = get_user_token(request, session)

    order_id = request.form.get('order-id', None)
    method = request.form.get('method', None)

    resp = smartpayout.process_order(user_token, order_id, method)

    if resp.status_code != 200:
        content = json.loads(resp.content)
        content['success'] = False
        del session['cart_id']
        response = Response(json.dumps(content), mimetype='application/json')
        # response.status_code = resp.status_code
        return response

        # return render_template('bad_order_process.html', content=json.loads(resp.content))
    else:
        del session['cart_id']
        resp_data = json.dumps({'success': True, 'order_id': order_id, 'detail': 'Order completed successfully.'})
        return Response(resp_data, mimetype='application/json')
        # return redirect('/receipt/{}/'.format(order_id))

    pass


@app.route('/<slug>/receipt/<int:order_id>/', methods=['get'])
def receipt(slug, order_id):
    user_token = get_user_token(request, session)
    status, order = smartpayout.get_order(user_token, order_id)
    return render_template('receipt.html', order=order)


@app.route('/ajax/login/', methods=['post'])
def ajax_login():
    email = request.form.get('email')
    password = request.form.get('password')

    response = smartpayout.login(email, password)
    resp = Response(response.content, mimetype='application/json')
    resp.status_code = response.status_code
    return resp


@app.route('/ajax/get_cart/')
def get_cart():
    # TODO: If we have a cart we need to fetch the latest for the cart. If they login we need to make sure the cart gets updated with the logged in user.
    user_token = get_user_token(request, session)
    headers = {}
    if user_token:
        headers['Authorization'] = 'Token {}'.format(user_token)

    resp = smartpayout.get_cart(request, session,
                                user_token)

    resp = Response(resp, mimetype='application/json')

    resp.status_code = 200
    return resp


@app.route('/ajax/cart/add_address/', methods=['POST'])
def add_address_to_cart():
    # This is where we collect the address as well as the shipping option.
    user_token = get_user_token(request, session)

    headers = {}
    if user_token:
        headers['Authorization'] = 'Token {}'.format(user_token)

    address_one = request.form.get('address-one')
    address_two = request.form.get('address-two')
    city = request.form.get('address-city')
    state = request.form.get('address-state')
    zip_code = request.form.get('address-zip')

    response = smartpayout.get_cart(request, session, user_token)

    cart = json.loads(response)

    address_payload = {'address': address_one, 'address_two': address_two, 'city': city, 'state': state,
                       'zip_code': zip_code}
    response = requests.post('{}carts/{}/add_address/'.format(app.config['API_ENDPOINT'], cart['id']),
                             headers=headers, data=address_payload)

    resp = Response(response.content, mimetype='application/json')
    resp.status_code = response.status_code

    return resp

@app.route('/ajax/cart/add_shipping/', methods=['POST'])
def add_shipping_to_cart():
    user_token = get_user_token(request, session)

    headers = {}
    if user_token:
        headers['Authorization'] = 'Token {}'.format(user_token)

    shipping_option = request.form.get('shipping_option')

    response = smartpayout.get_cart(request, session, user_token)

    cart = json.loads(response)

    shipping_option_payload = {'shipping_option': shipping_option}
    response = requests.post('{}carts/{}/add_shipping/'.format(app.config['API_ENDPOINT'], cart['id']), headers=headers,
                             data=shipping_option_payload)

    resp = Response(response.content, mimetype='application/json')
    resp.status_code = response.status_code

    return resp


@app.route('/ajax/add_product/', methods=['POST'])
def add_product():
    user_token = get_user_token(request, session)
    cart = json.loads(smartpayout.get_cart(request, session, user_token))

    product_id = request.form.get('product', type=int)
    quantity = request.form.get('quantity', type=int)

    response = smartpayout.add_product(cart['id'], product_id, quantity, user_token)

    # If we lost the session we need to fix the cart issue.
    # if response.status_code == 403:
    #     del session['cart_id']
    #     cart = smartpayout.get_cart(request, session, user_token)
    #     response = smartpayout.add_product(cart['id'], product_id, quantity, user_token)

    resp = jsonify(json.loads(response.content))
    resp.status_code = response.status_code
    return resp


@app.route('/ajax/update_cart/', methods=['POST'])
def update_cart():
    updates = request.form.get('changes', None)
    cart_id = session.get('cart_id', None)

    # TODO: Need to fix the issue with the response not being set if we have no updates.
    if updates:
        response = smartpayout.update_cart_quantities(cart_id, updates)
    resp = Response(response.content, mimetype='application/json')
    resp.status_code = 200
    return resp


@app.route('/ajax/get_cards/', methods=['get'])
def get_cards():
    user_token = get_user_token(request, session)
    status, cards = smartpayout.get_credit_cards(user_token)

    resp = Response(json.dumps(cards))
    resp.status_code = status
    return resp


@app.route('/ajax/add_card/', methods=['post'])
def add_card():
    user_token = get_user_token(request, session)
    card_number = request.form.get('number', None)
    expiry = request.form.get('expiry', None)
    name = request.form.get('name', None)
    cvc = request.form.get('cvc', None)

    if expiry:
        expiry = [x.strip() for x in expiry.split('/')]

    cards = smartpayout.add_credit_card(user_token, card_number=card_number, name=name, exp_month=expiry[0],
                                        exp_year=expiry[1], cvc=cvc)

    if cards.status_code != 200:
        return Response(json.dumps({'success': False, 'results': json.loads(cards.content)}))
        # return Response(cards.content)
    else:
        # TODO: Need to get the list of credit cards with the response.
        return Response(json.dumps({'success': True, 'results': json.loads(cards.content)}))
        # return Response(json.loads(cards.content))


@app.route('/ajax/createidentifier/', methods=['post'])
def create_identifier():
    user_token = get_user_token(request, session)

    ident = request.form.get('public-ident', None)
    slug = request.form.get('user-slug', None)

    status_code, resp = smartpayout.add_user_slug(slug, ident, request, session, user_token)

    # if status_code == 409:
    #     resp_data = json.loads(resp)
    #     return Response(resp, mimetype='application/json', status=409)

    return Response(resp, mimetype='application/json', status=status_code)


@app.route('/ajax/monthly_qv/', methods=['get'])
def monthly_qv():
    user_token = get_user_token(request, session)

    resp = smartpayout.get_monthly_qv(user_token)
    return Response(json.dumps({'monthly_qv': resp}), mimetype='application/json')

@app.route('/ajax/monthly_ov/', methods=['get'])
def monthly_ov():
    user_token = get_user_token(request, session)

    resp = smartpayout.get_monthly_ov(user_token)
    return Response(json.dumps({'monthly_ov': resp}), mimetype='application/json')


@app.route('/ajax/monthly_enrollments/', methods=['get'])
def monthly_enrollments():
    user_token = get_user_token(request, session)

    resp = smartpayout.get_monthly_enrollments(user_token)
    return Response(json.dumps({'monthly_enrollments': resp}), mimetype='application/json')

@app.route('/ajax/monthly_rank/', methods=['get'])
def monthly_rank():
    user_token = get_user_token(request, session)

    resp = smartpayout.get_monthly_ranking(user_token)
    return Response(json.dumps(resp), mimetype='application/json')

@app.context_processor
def inject_user():
    context = {'loggedin': False}

    token = request.cookies.get('token', None)
    if token and request.path != '/login/' and request.path != '/logout/':
        response = requests.get('%s%s' % (app.config['API_ENDPOINT'], 'users/me/'),
                                headers={'Authorization': 'Token %s' % token})
        if response.status_code == 401:
            context['redirect'] = '/login/?next=%s' % request.path
        response = json.loads(response.content)

        context['user'] = response[0]
        context['loggedin'] = True


    return context


@app.before_request
def catch_all():
    ignore_paths = ['/favicon.ico/', '/login/', '/logout/']
    if request.path in ignore_paths or request.path.startswith('/static/') or request.path.startswith(
            '/ajax/') or request.path.startswith('/language/') or request.path.startswith('/favicon.ico'):
        pass
    else:
        cache = SimpleCache()
        session.clear()
        known_slugs = cache.get('known_slugs')

        session_slug = request.cookies.get('slug', None)
        if session_slug in INVALID_SLUGS:
            session_slug = None
        if not session_slug:
            session_slug = session.get('slug', None)

        if session_slug:
            if known_slugs:
                if session_slug not in known_slugs:
                    known_slugs.append(session_slug)
                    cache.set('known_slugs', known_slugs)
            else:
                known_slugs = [session_slug]
                cache.set('known_slugs', known_slugs)

        # return 'You want path: %s' % path
        path = request.path.split('/')

        if path:
            try:
                if path[1] in INVALID_SLUGS or path[1] == '' or (
                                (path[1] != session_slug) and (known_slugs and not path[1] in known_slugs) and (
                                    path[1] != DEFAULT_SLUG)):
                    response = smartpayout.valid_slug(path[1])

                    if response['valid']:
                        session['slug'] = response['slug']
                    else:
                        if not session_slug:
                            session_slug = response['slug']
                            session['slug'] = session_slug
                        return redirect('/{}{}'.format(session_slug, request.path))
                else:
                    pass
            except TypeError as e:
                rollbar.report_exc_info(sys.exc_info())
                # raise TypeError('Error on path: {}'.format(request.path))
        else:
            if session_slug:
                return redirect('/{}/'.format(session_slug))


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


@app.before_first_request
def init_rollbar():
    """init rollbar module"""
    rollbar.init(
        # access token for the demo app: https://rollbar.com/demo
        'd3d3939c96634f5c8fbb585a97a4a031',
        # environment name
        'development',
        # server root directory, makes tracebacks prettier
        root=os.path.dirname(os.path.realpath(__file__)),
        # flask already sets up logging
        allow_logging_basic_config=False)

    # send exceptions from `app` to rollbar, using flask's signal system.
    got_request_exception.connect(rollbar.contrib.flask.report_exception, app)


if __name__ == '__main__':
    app.run(debug=True)
