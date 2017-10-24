from setuptools import setup

setup(
    name='application',
    packages=['application'],
    include_package_data=True,
    py_modules=['flask_passlib'],
    install_requires=[
        'flask==0.12.1'
    ]
)