"""
Flask-MongoReST

A MongoDB ReSTful interface for Flask.
"""
from setuptools import setup

setup(
    name='Flask-MongoReST',
    version='0.0.1',
    url='www.somem',
    license='MIT',
    author='Wilberto Morales',
    author_email='wilbertomorales777@gmail.com',
    description='A MongoDB ReSTFul interface for Flask applications',
    long_description=__doc__,
    packages=['flask_mongorest'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=['Flask', 'pymongo'],
    classifiers=[
        'Enviroment :: Web Development',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',

    ]

)
