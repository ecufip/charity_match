# CSR match India #

An app to match companies with charities in India.

## To create database ##
From command line - deletes existing db:

        $ flask initdb

## To install ##
Within virtualenv

        $ python setup.py install
        
## To activate virtualenv ##
In root:
        $ source ENV/bin/activate

To deactivate:
        $ deactivate

## To run ##
After activating virtualenv:

        $ export FLASK_APP=application; export FLASK_DEBUG=true
        $ flask run

## Requirements ##
Flask
passlib
