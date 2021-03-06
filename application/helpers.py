from flask import redirect, session, url_for
from functools import wraps

def login_required(f):
    '''
    Decorate routes to require login.
    http://flask.pocoo.org/docs/0.11/patterns/viewdecorators/
    '''
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('charityId') is None:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function