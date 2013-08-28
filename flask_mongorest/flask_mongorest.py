from flask import current_app, Blueprint, jsonify, Flask, make_response, request, Response, stream_with_context
from views import APIView, HomeView, AboutView
from utils import *
import json, datetime, pymongo

try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack

class MongoAPI(object):
    
    METHODS_SUPPORTED = ('GET', 'POST', 'DELETE', 'PUT')
    BLUEPRINT_NAME_SUFFIX = "%s%s"
    API_PREFIX = '/api'
    ABOUT = '/api/about'

    def __init__(self, app=None, db=None, api_prefix=API_PREFIX):
        
        if db:
            self.db = db
        if app:
            self.app = app

        if self.app is not None and self.db is not None:
            self.init_app(app, db)

    def init_app(self, app=None, db=None):
        """
        Initalise the `app` with the database, makes sure that `app` and `db` are of the right type.
        If the `app` or `db` parameters where previously set ie during `__init__`, then the attributes are replaced with the new,
        only if they are truthy objects, and of the right `Flask` and `Database` types.
        So passing `None` is safe if the attributes where set already.
        Returns `self` to allow method chaining.

        """

        self.db = db or self.db 
        self.app = app or self.app

        if not isinstance(self.app, Flask):
            raise TypeError('`app` must be a `Flask` object')

        if not isinstance(self.db, pymongo.database.Database):
            raise TypeError('`db` must be a `Database` object') 

        if hasattr(self.app, 'teardown_appcontext'):
            self.app.teardown_appcontext(self.teardown)
        else:
            self.app.teardown_request(self.teardown)

        self._register_defaults()
        
        return self
    
    def create_api_blueprint(self, collection_name, api_name=None, api_prefix=API_PREFIX, methods_allowed=['GET', ], pk_type='str', pk='_id'):
        """
        
        """
        collection = self.get_collection(collection_name)
        
        view_name, endpoint, blueprint_name = self.format_names(collection, api_name, api_prefix) # format_names returns a tuple with the names used to register the views and blueprints.
        
        try:
            collection_view = APIView.as_view(view_name, collection) # Flask pluggable view
        except TypeError:
            # This exception occurs because flask views don't support unicode 
            # And pymongo collections.name returns a unicode value
            collection_view = APIView.as_view(str(view_name), collection, pk)

        methods_allowed = self.format_methods(methods_allowed)
        
        self.validate_methods(MongoAPI.METHODS_SUPPORTED, methods_allowed)

        blueprint = Blueprint(str(blueprint_name), __name__, api_prefix)

        blueprint.add_url_rule(endpoint, view_func=collection_view, methods=self.root_methods(methods_allowed[:])) #/api/collection_name/

        endpoint = create_url_placeholder(endpoint, pk_type, pk)

        blueprint.add_url_rule(endpoint, view_func=collection_view, methods=self.document_methods(methods_allowed[:])) #/api/collection_name/primary_key

        blueprint.mongo_rest_api = True
        return blueprint


    def create_api(self, *args, **kw):
        """
        Following Flask-Restless example, calls the `create_api_blueprint` and registers the `Blueprint` object to the application.
        If you want to create the API but register it later on, use `create_api_blueprint`.
        Returns self
        """
        blueprint = self.create_api_blueprint(*args, **kw)
        self.app.register_blueprint(blueprint)
        return self

    def teardown(self, exception):
        ctx = stack.top
        # TODO implement
        # stuff to close off here, stuff you add should be added to the stack ctx
        #if hasattr(ctx, '')
        pass
    
    def format_names(self, collection, api_name=None, api_prefix=API_PREFIX):
        """
        Returns the names used to register the api. This method will make sure there isn't any duplicates.

        `collection` Pymongo.collection.Collection object.

        `api_name` The name the collection should use in URI endpoints, defaults to the collection's name if not provided.

        `api_prefix` Prepended to the collection name. For example 'apiv1'.
        """
        
        name = api_name or collection.name.lower()  # used for the url route, if the user supplied an api_name use that, else use the collection's name

        name = self.unique_name(name)

        view_name = "%s_%s" % (api_prefix, name) # used for the view function
         
        endpoint = '%s/%s/' % (api_prefix, name)

        blueprint_name = name

        return (view_name, endpoint, blueprint_name)
        

    def format_methods(self, methods_list):
        """
        Returns all the items in the list but capitalized. Used to turn get, post, delete into GET, POST, DELETE

        `methods_list` a list of strings with HTTP actions.
        """
        if not check_list_or_tup(methods_list):
            raise TypeError('methods_allowed must be a list or tuple')

        return [method.upper() for method in methods_list] # Capitalize all methods

    def get_collection(self, collection_name):
        """
        Retreives a collection from the database. A handy method that accepts a str, unicode, or Collection object.
        If collection_name is a pymongo.collection.Collection object then the collection must already exist in the database.
        """
        
        if check_string(collection_name):
            # if the collection_name is a string or unicode, then ask the database for it.
            return self.db[collection_name]
        # if  the collection_name is Collection object from the database already and it already 
        # exists in the database, we use that
        elif isinstance(collection_name, pymongo.collection.Collection) and collection_name in self.db.collection_names():
            return collection_name
        else:
            # raised when collection_name is not string, unicode or a Collection object already in the database
            raise TypeError('collection_name must be a string, or a collection already in the database.')

    def root_methods(self, methods):
        return self.remove_items(methods, 'PUT', )
    
    def document_methods(self, methods):
        return self.remove_items(methods,'POST')

    def remove_item(self, list_object, item):
        """
        Removes an item from a list without raising an exception if the item isn't found.
        """
        # TODO type check on paramas, and move over to utils.py
        try:
            list_object.remove(item)
        except ValueError:
            pass
        return list_object

    def remove_items(self, list_object, *items):
        for item in items:
            list_object = self.remove_item(list_object, item)
        return list_object

    def validate_methods(self, methods_valid, methods):
        """
        Takes a list of methods that are valid and a list of methods. 
        If any of the methods isn't valid it raises an Exception.
        If all methods are in methods_valid it returns True.

        """
        for method in methods:
            if method not in methods_valid:
                raise BaseException('Invalid method: %s, methods supported are: %s' % (method, methods_valid)) # TODO Create a custom exception
        return True
    
    def unique_name(self, basename):
        """
        Directly taken from Flask-Restless, the inspiration for this extension.
        See https://github.com/jfinkels/flask-restless/

        Returns the next name for a blueprint with the specified base name.

        This method returns a string of the form ``'{0}{1}'.format(basename,
        number)``, where ``number`` is the next non-negative integer not
        already used in the name of an existing blueprint.

        For example, if `basename` is ``'personapi'`` and blueprints already
        exist with names ``'personapi0'``, ``'personapi1'``, and
        ``'personapi2'``, then this function would return ``'personapi3'``. We
        expect that code which calls this function will subsequently register a
        blueprint with that name, but that is not necessary.

        """
        # blueprints is a dict whose keys are the names of the blueprints
        blueprints = self.app.blueprints
        existing = [name for name in blueprints if name.startswith(basename)]
        # if this is the first one...
        if not existing:
            next_number = 1
        else:
            # for brevity
            b = basename
            existing_numbers = [int(n.partition(b)[-1]) for n in existing]
            next_number = max(existing_numbers) + 1
        return MongoAPI.BLUEPRINT_NAME_SUFFIX % (basename, next_number)

    def _register_defaults(self):
        """
        Registers some meta data about the Extension developers and gives the '/api' route a nice index of all
        registered blueprints.

        """
        self.app.add_url_rule("%s/" % MongoAPI.API_PREFIX, view_func=HomeView.as_view('home_page', app=self.app))
        self.app.add_url_rule("%s/" % MongoAPI.ABOUT, view_func=AboutView.as_view('about_page', app=self.app))
