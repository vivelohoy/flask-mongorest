from flask import current_app, request
import json, bson, datetime
from utils import *

def check_string(var):
    """
    Returns 'True' if 'var' is an instance of 'str' or 'unicode'
    """
    return isinstance(var, str) or isinstance(var, unicode)

def check_list_or_tup(var):
    """
    Returns 'True' if 'var' is an instance of 'list' or 'tuple'
    """
    return isinstance(var, list) or isinstance(var, tuple)

def create_url_placeholder(endpoint, pk_type, pk_name):
    
    if pk_type == 'str' or pk_type == 'unicode':
        return "%s<%s>/" % (endpoint, pk_name)
    
    return "%s<%s:%s>/" % (endpoint, pk_type, pk_name)

def bsonify(*args, **kwargs):
    """

    """
    indent = 0
    
    if current_app.config['JSONIFY_PRETTYPRINT_REGULAR'] and not request.is_xhr: indent = 2

    return current_app.response_class(tobson(MongoEncoder, indent, *args, **kwargs), mimetype='application/json')
    
    
def tobson(encode_clss, indent, *args, **kwargs):
    return json.dumps(dict(*args, **kwargs), cls=MongoEncoder, indent=indent).replace('\n', '')

class MongoEncoder(json.JSONEncoder):
    """
    Custom encoder for dumping MongoDB documents.
    Mostly because MongoDB uses 'ObjectId' objects which aren't natively supported in Python. 
    Also if the object is an instance of 'datetime.datetime' then it returns it's iso format representation.
    """
    def default(self, obj):
        if isinstance(obj, bson.ObjectId):
            return str(obj)
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return super(MongoEncoder, self).default(obj)
