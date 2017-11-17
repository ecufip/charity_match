from setuptools import setup

setup(
    name='application',
    packages=['application'],
    include_package_data=True,
    install_requires=[
        'flask==0.12.1', 
        'passlib==1.7.0'
    ]
)