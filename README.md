Flask-MongoReST
================

A ReSTful API for Flask and MongoDB.

Installation
============

This project is really young and it isn't up at PYPI yet.

`git clone https://github.com/vivelohoy/flask-mongorest.git`
`cd /path/to/flask-mongorest`
`python setup.py install`

Usage
=====

Make sure to have ran `python setup.py install`. In your Flask project import [pymongo](http://api.mongodb.org/python/current/) and the `MongoAPI` object. Also the `mongod` daemon must be running.

```
from flask import Flask
from flask.ext.mongorest import MongoAPI
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient()
db = client['my_db_name']
manager = MongoAPI(app=app, db=db)

manager.create_api('my_collection_name')


if __name__ == '__main__':
    app.run(debug=True)
```


