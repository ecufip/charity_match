from setuptools import setup

setup(
    name='application',
    packages=['application'],
    include_package_data=True,
    install_requires=[
        'flask==0.12.1', 
        'flask_passlib'
    ]
)