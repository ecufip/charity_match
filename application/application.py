# all the imports
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
render_template, flash

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
    """Connects to database"""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """
    Opens a new database connection if there is none yet for the
    current application context
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    """Initializes the database"""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Command line prompt to call init_db function"""
    init_db()
    print('Initialized the database.')

@app.route('/')
def index():
    db = get_db()
    charities = db.execute('select * from charities order by id desc').fetchall()
    return render_template('index.html', charity='name', charities=charities)

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        db = get_db()
        db.execute('insert into charities (name, regNo, postCode, address, description) values (?, ?, ?, ?, ?)',
                    [request.form['name'], request.form['regNo'],
                    request.form['postCode'], request.form['address'],
                    request.form['description']])
        db.commit()
        flash('New charity was successfully registered')
        return redirect(url_for('index'))
    else:
        return render_template('register.html')

@app.route('/login')
def login():
    return 'TODO'