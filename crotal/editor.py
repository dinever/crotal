import os

from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash


DEBUG = True
FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = '.md'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))

@app.route('/')
def index():
    path = os.path.join('publish', 'index.html')
    page = open(path, 'r').read()
    return page

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('admin'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('index'))

@app.route('/admin/')
def admin():
    if not session.get('logged_in'):
        abort(401)
    return render_template('admin.html')

@app.route('/edit/<string:slug>/')
def edit(slug):
    return "Hello" + slug

@app.route('/<path:path>')
def page(path):
    path = os.path.join('publish', path)
    if os.path.isdir(path):
        path = os.path.join(path, 'index.html')
    page = open(path, 'r').read()
    return page

def server_start():
    app.run(port=5000)
