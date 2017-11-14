# all the imports
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
render_template, flash
from passlib.apps import custom_app_context as pwd_context

from .helpers import *

app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'application.db'),
    SECRET_KEY='csrm1tch3nd31',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('APPLICATION_SETTINGS', silent=True)

def connect_db():
    '''Connects to database'''
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    '''
    Opens a new database connection if there is none yet for the
    current application context
    '''
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    '''Closes the database again at the end of the request.'''
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    '''Initializes the database'''
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    '''Command line prompt to call init_db function'''
    init_db()
    print('Initialized the database.')

@app.route('/')
def index():
    '''Accesses database and returns all charities to index template'''
    db = get_db()
    charities = db.execute('SELECT * FROM charities ORDER BY id DESC').fetchall()
    return render_template('index.html', charities=charities)

@app.route('/register', methods=['POST', 'GET'])
def register():
    '''Inserts new charity into database'''
    if request.method == 'POST':
        
        # encrypt the password
        hash = pwd_context.hash(request.form.get('password'))
        
        # open db connection
        db = get_db()
        
        # insert form information into database
        db.execute('''
                   INSERT INTO charities (name, email, regNo, postCode, address, description, password)
                   VALUES (?, ?, ?, ?, ?, ?, ?)
                   ''', 
                    [request.form['name'], request.form['email'], request.form['regNo'], request.form['postCode'], 
                    request.form['address'],request.form['description'], hash]
                   )
        
        # commit changes
        db.commit()

        db.close()

        flash('New charity was successfully registered')

        # update session information
        session['email'] = request.form.get('email')

        # direct to account homepage
        return redirect(url_for('account'))
    
    # shows registration form
    else:
        return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    '''Log user in.'''
    if request.method == 'POST':

        # forget any user_id
        session.clear()
        
        # ensure username was submitted
        if not request.form.get('email'):
            return 'must provide email'

        # ensure password was submitted
        elif not request.form.get('password'):
            return 'must provide password'
        
        # open db connection
        db = get_db()

        # open cursor - required for fetching results
        cur = db.cursor()
        
        # query database for username - use request.form.get() not request.form[] as won't throw error
        cur.execute('SELECT * FROM charities WHERE email = ?', [request.form.get('email')])
        rows = cur.fetchall()

        # ensure email exists and password is correct - pwd_context de-hashes password and compares
        if len(rows) != 1 or not pwd_context.verify(request.form.get('password'), rows[0]['password']):
            return 'invalid email or password'
        
        # update session information
        session['email'] = request.form.get('email')
        
        # close db
        db.close()

        # direct to account homepage
        return redirect(url_for('account')) 
    
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for('login'))

@app.route('/account')
@login_required
def account():
    return render_template('account.html', email = session['email'])