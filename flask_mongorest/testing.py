from utils import *

def audit_fields(obj_dict, current_level=0):
    
    print "Audit object: %s:%s" % (obj_dict, type(obj_dict))

    if check_list_or_tup(obj_dict):
        current_obj = obj_dict.pop(0)
        audit_fields(current_obj)
    else:
        current_obj = obj_dict
        print "Iterating object %s:%s" % (obj_dict, type(obj_dict))
        for key in current_obj.iterkeys():
            if key.startswith('$'):
                return (False, bsonify({'Error field names cannot start with': '$'}))
            if key.startswith('.'):
                return (False ,bsonify({'Error field names cannot start with': '.'}))

        return (True, None)

x = [{'Data': 'A lot', 'Muchmore': 'to come'}, {'Xlist': ['muajaja', 'muahaha']}]

print audit_fields(x)
