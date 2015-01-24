from flask import Flask, render_template, request
from flask.ext.bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)


@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/login/')
def login():
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
def hello():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
