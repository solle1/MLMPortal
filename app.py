import json
from flask import Flask, render_template, request, redirect
from flask.ext.bootstrap import Bootstrap
import requests

app = Flask(__name__)
Bootstrap(app)
app.config['API_ENDPOINT'] = 'http://catchmycommission.com/api/v1/'

ADMINS = ['dan@straightbit.com']
import logging
from logging.handlers import SMTPHandler
mail_handler = SMTPHandler('127.0.0.1',
                           'server-error@straightbit.com',
                           ADMINS, 'Your Application Failed')
mail_handler.setLevel(logging.ERROR)
app.logger.addHandler(mail_handler)

@app.route('/')
def landing():
    return render_template('index.html')


@app.route('/login/')
def login():
    token = request.cookies.get('token')
    if token:
        return redirect('/home/')
    next = request.args.get('next', '/home/')
    unauth = request.args.get('unauth', None)

    redirected = False
    if unauth:
        redirected = True

    return render_template('login.html', next=next, redirected=redirected)


@app.route('/logout/')
def logout():
    return render_template('logout.html')


@app.route('/home/')
def home():
    return render_template('home.html')


@app.route('/register/')
def register():
    return render_template('register.html')


@app.context_processor
def inject_user():
    context = {'loggedin': False}

    token = request.cookies.get('token', None)
    if token:
        response = requests.get('%s%s' % (app.config['API_ENDPOINT'], 'users'),
                                headers={'Authorization': 'Token %s' % token})
        response = json.loads(response.content)
        context['user'] = response
        context['loggedin'] = True

    return context


if __name__ == '__main__':
    # app.config['API_ENDPOINT'] = 'http://catchmycommission.com/api/v1/'
    # app.config['API_ENDPOINT'] = 'http://127.0.0.1:8111/api/v1/'
    app.run()
