from flask.views import MethodView, View
from flask import request
from utils import *
from ast import literal_eval
import pymongo, bson

class HomeView(View):
    """
    Useful view to list all of the apis registered.
    """
    methods = ['Get',]
    def __init__(self, app):
        self.app = app
    def dispatch_request(self):
        return bsonify({"All_API": [{"API_name": api_name } for api_name, blueprint_obj in self.app.blueprints.iteritems()
                                        if hasattr(blueprint_obj, 'mongo_rest_api')]})
class AboutView(View):
    """
    Simple view to show some meta data about the core authors and organizations.
    """
    methods = ['Get',] # Only allow get methods because this is only intended to be viewed.
    def __init__(self, app):
        self.app = app
    
    def dispatch_request(self):
        return bsonify({
            "About": "This Flask extension is developed by Hoy Publications LLC and some hackers.",
            "Hack": "Feel free to hack on the source code and send a Pull Request. We are very open about changes that imporve the API",
            "Free Geek": "Free Geek’s mission is to recycle technology and provide access to computers, the Internet, education, and job skills in exchange for community service.",
            "Free Geek Chicago": "Free Geek Chicago is a branch of Free Geek. Join us every Saturday for open hack and get to work with projects like this one. All skill levels are welcomed!"
            })
class APIView(MethodView):
    def __init__(self, collection, pk=None):
        self.collection = collection
        self.pk = pk
    
    def get(self, **kwargs):
        
        args = request.args
        
        uri_query = literal_eval(args.get('q', default='{}'))
        
        limit = int(args.get('limit', default=20))

        pk = kwargs.get(self.pk)
        
        if pk is None:
            data = self.collection.find(spec=uri_query)
            return self._output_results(data, limit=limit)
        else:
            # expose one document
            if self.pk == '_id':
                query = bson.objectid.ObjectId(oid=pk)
            
            else:
                query = pk
            results = self.collection.find_one(spec_or_id=pk)

            return bsonify({"results": results})

    def post(self, **kwargs):
        # create a document
        """
        Receive atleast the primary key.
        Insert the data into the database.
        """
        
        data = literal_eval(request.form['data'])
            
        passed, response = self.audit_fields(data)
        
        if not passed:
            return response
        
        return bsonify({'results': self.collection.insert(data)})


    def delete(self, **kwargs):
         # delete a single document
         """
         receive the string, 
         convert the string into an ObjectID
         delete from the database
         """
         # !!!If the query is empty, the db will delete all data!!!
         data = literal_eval(request.form['data'])
         results = self.collection.remove(data)
         return bsonify({'results': results})         

    def put(self, **kwargs):
        # update a single document
        args = request.args

        pk = kwargs.get(self.pk)
        if pk:
            'Do single item stuff here.'
            print pk
        else:
            print 'No pk'
        return bsonify({})

    def _output_results(self, cursor, limit):
        """
        Loop through the next batch.
        """
        batch = []
        try:
            while len(batch) < limit:
                batch.append(cursor.next())
        except pymongo.errors.AutoReconnect:
            return bsonify({"error message" : "Reconnecting, please try again"})

        except pymongo.errors.OperationFailure, e:
            return bsonify({"error message" : "%s" % e})

        except StopIteration: pass
        
        return bsonify({"results":batch})

    def audit_fields(self, obj_dict, current_level=0):
        """
        Finish me.
        """
        return (True, None)
        if check_list_or_tup(obj_dict):

            self.audit_fields(obj_dict[current_level], current_level + 1)

        for key in obj_dict.iterkeys():
            if key.startswith('$'):
                return (False, bsonify({'Error field names cannot start with': '$'}))
            if key.startswith('.'):
                return (False ,bsonify({'Error field names cannot start with': '.'}))
        return (True, None)
