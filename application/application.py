# all the imports
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template
from passlib.apps import custom_app_context as pwd_context

from .helpers import *

app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'application.db'),
    SECRET_KEY='csrmatch',
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
    projects = db.execute('''
                          SELECT * , charities.name AS charity
                          FROM projects 
                          INNER JOIN charities ON projects.charityId = charities.id
                          ORDER BY name DESC
                          ''').fetchall()
    db.close()
    return render_template('index.html', projects=projects)

@app.route('/register', methods=['POST', 'GET'])
def register():
    '''Inserts new charity into database'''
    if request.method == 'POST':
        
        # encrypt the password
        hash = pwd_context.hash(request.form.get('password'))

        # open db connection
        db = get_db()

        # add validation to check if email already exists
        
        # insert form information into database
        db.execute('''
                   INSERT INTO charities (name, email, description, password)
                   VALUES (?, ?, ?, ?)
                   ''', 
                    [request.form['name'], request.form['email'],
                    request.form['description'], hash]
                   )

        # carry out query to select data that matches email
        rows = db.execute('SELECT * FROM charities WHERE email = ?', [request.form.get('email')]).fetchall()
        
        # update session information
        session['charityId'] = rows[0]['id']
        session['charityName'] = rows[0]['name']
        
        # commit changes
        db.commit()

        db.close()

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
        
        # query database for username - use request.form.get() not request.form[] as won't throw error
        rows = db.execute('SELECT * FROM charities WHERE email = ?', [request.form.get('email')]).fetchall()

        # ensure email exists and password is correct - pwd_context de-hashes password and compares
        if len(rows) != 1 or not pwd_context.verify(request.form.get('password'), rows[0]['password']):
            return 'invalid email or password'
        
        # update session information
        session['charityId'] = rows[0]['id']
        session['charityName'] = rows[0]['name']
        
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
    ''' render account homepage with charity and projects'''
    # open db connection
    db = get_db()

    # return all project where the charity id is the same as the logged in project
    projects = db.execute('SELECT * FROM projects WHERE charityId = ? ORDER BY name DESC', 
                            [session['charityId']]).fetchall()
    
    # close db connection
    db.close()

    return render_template('account.html', name = session['charityName'], projects=projects)

@app.route('/add-project', methods=['GET', 'POST'])
@login_required
def add_project():
    ''' Adding a project '''
    if request.method == 'POST':
        # open db connection
        db = get_db()
        
        # insert form information into database
        db.execute('''
                   INSERT INTO projects (name, charityId, description, short, picUrl)
                   VALUES (?, ?, ?, ?, ?)
                   ''', 
                    [request.form['name'], session['charityId'], request.form['description'], 
                    request.form['short'], request.form['picUrl']]
                   )
        
        # commit changes
        db.commit()

        db.close()

        # direct to account homepage
        return redirect(url_for('account'))

    else:
        return render_template('add_project.html')


@app.route('/project/<projectId>')
def project_page(projectId):

    # open db connection
    db = get_db()

    # return all project where the charity id is the same as the logged in project
    project = db.execute('''
                         SELECT * , charities.email AS email
                         FROM projects 
                         INNER JOIN charities ON projects.charityId =charities.id
                         WHERE projects.id = ? ORDER BY name DESC
                         ''', 
                         projectId).fetchall()[0]

    # close db connection
    db.close()

    print(project)

    return render_template('project.html', project = project)

@app.route('/delete-project/<projectId>', methods=['GET', 'POST'])
def project_delete(projectId):
    
    if request.method == 'POST':

        db = get_db()

        db.execute('DELETE FROM projects WHERE id =?', projectId)
        
        db.commit()

        db.close()

        return redirect(url_for('account'))