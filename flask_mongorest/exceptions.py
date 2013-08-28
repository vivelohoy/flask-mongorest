class MongoExceptionBase(Exception):
    def __init__(self,e):
        self.e = e
        self.msg = 'This exception was raised due to an error with Flask-MongoREST/'
    def __str__(self):
        return repr("%s:%s" % self.msg, self.e)

NotFlaskObject = type('NotFlaskObject', (MongoExceptionBase,), {})


