#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
from flask import Flask, render_template, request, redirect, abort, g, session, Response
from flask.ext.babel import Babel
from flask.ext.bootstrap import Bootstrap
import requests

from utils import datetimeformat, stringtodate, remove_spaces

app = Flask(__name__)
Bootstrap(app)
app.config['API_ENDPOINT'] = 'http://demo.smartpayout.com/api/'
# app.config['API_ENDPOINT'] = 'http://local.smartpayout.com:8123/api/'
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
    return render_template('index.html')

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
    return render_template('home.html')


@app.route('/register/')
def register():
    return render_template('register.html')


@app.route('/profile/')
def profile():
    return render_template('profile.html')


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

    return render_template('products.html', products=products, groups=groups)


@app.context_processor
def inject_user():
    context = {'loggedin': False}

    token = request.cookies.get('token', None)
    if token and request.path != '/login/':
        response = requests.get('%s%s' % (app.config['API_ENDPOINT'], 'users'),
                                headers={'Authorization': 'Token %s' % token})
        if response.status_code == 401:
            context['redirect'] = '/login/?next=%s' % request.path
        response = json.loads(response.content)

        context['user'] = response
        context['loggedin'] = True

    return context

@app.context_processor
def inject_language():
    context = {'language': session.get('current_lang', 'en')}

    return context


if __name__ == '__main__':
    # app.config['API_ENDPOINT'] = 'http://catchmycommission.com/api/v1/'

    app.run(debug=True)
