import time
from api import current_user

class SetError(Exception):
    pass

class ValidationError(Exception):
    pass

class PathError(Exception):
    pass

now = lambda *args: time.time()
identity = lambda x: x
public = lambda *args: True
never  = lambda *args: False
hidden = lambda *args: False
private = hidden

def required(v):
    return v is not None

def context(id):
    def helper(ctx, doc):
        return ctx[id]
    return helper

def read_only(*args):
    return False

def default(v):
    def helper(ctx):
        return v
    return helper

def now(*args):
    return time.time()

def hidden(*args):
    return False

def is_owner(doc):
    print(current_user(), doc['__owners'])
    return current_user() in doc['__owners']

class Schema:
    def __init__(self, schema):
        self.schema = schema
        self.kw = ['__get', '__set_document', '__get_document', \
                   '__create_document', '__ownership', '__set_default']

    def __getitem__(self, index):
        return self.schema[index]

    def get(self, document):
        schema = self.schema
        g = schema.get('__get', public)
        if not g(document):
            return None
        ret = {}
        set_document = set(document.keys())
        set_schema = set(schema.keys()) - set(self.kw)
        intersection =  set_document & set_schema

        owners = document.get('__owners', [])

        for key in intersection:
            g = schema[key].get('get', public)
            if '__owners' not in document:
                document['__owners'] = owners
            v = g(document)
            
            if schema[key]['type'].__class__ == Schema:
                if not v:
                    ret[key] = None
                else:
                    document[key]['__owners'] = owners
                    ret[key] = schema[key]['type'].get(document[key])
            elif schema[key]['type'].__class__ is list:
                if not v:
                    ret[key] = []
                else:
                    ret[key] = [schema[key]['type'][0].get(k) for k in document[key]] 
            elif v:
                ret[key] = document[key]
        return ret

    def post(self,document, context=None):
        if context is None:
            context = {}
        schema = self.schema

        c = schema.get('__create_document', lambda *args: True)
        if not c(document):
            raise Exception('can not create document')

        ret = {}
        set_document = set(document.keys())
        set_schema = set(schema.keys()) - set(self.kw)
        intersection =  set_document & set_schema 
        missing = set_schema - set_document
        if len(set_document - set_schema) > 0:
            raise Exception('keywords not in schema')

        for key in missing | intersection:
            if schema[key]['type'].__class__ == Schema:
                if document.get(key):
                    ret[key] = schema[key]['type'].post(document[key])
            elif type(schema[key]['type']) is list:
                schema = schema[key]['type'][0]
                ret[key] = [schema.post(k) for k in document[key]]
            elif 'computed' not in schema[key]:
                validation = schema[key].get('validation', public)
                mtype = schema[key]['type']
                initial = schema[key].get('initial')
                initial = initial and initial(context)
                v = document.get(key, initial)
                if not type(v) is mtype or not validation(v):
                    raise ValidationError('not valid prop or missing', key)
                if key in intersection or initial is not None: 
                    ret[key] = document.get(key, initial)
            else:
                create = schema[key].get('computed')
                val = create(document) 
                ret[key] = val
        return ret

    def put(self, path, root_doc, value):
        schema = self.schema
        s = schema.get('__set_document', never)
        if not s(root_doc):
            raise SetError('no se puede setear, __set')
        
        set_default = schema.get('__set_default', never)
        validation = public
        computed = None
        doc = root_doc
        paths = path.split('.')
        last = paths[-1]
        owners = root_doc.get('__owners', [])
        
        for key in paths:
            if key.isdigit():
                key = int(key)
                schema = schema[0]
                doc[key]['__owners'] = owners
                if schema.__class__ == Schema and not to_set(doc[key]): #schema.schema.get('set', set_default)():
                    raise SetError('no se puede setear, set')
            else:
                try:
                    schema[key]
                except KeyError:
                    raise PathError('path does not exist')
                validation = schema[key].get('validation', validation)
                computed = schema[key].get('computed')
                to_set = schema[key].get('set', set_default)
                schema = schema[key]['type']
            
            if (schema.__class__ == Schema or type(schema) is list) and key != last:
                try:                
                    doc = doc[key]
                except KeyError:
                    raise PathError('path does not exist')
                
                if type(schema) is not list:
                    doc['__owners'] = owners
                    if not to_set(doc):
                        raise SetError('no se puede setear, set')
        
        if type(schema) is list:
            schema = schema[0]
        if schema.__class__ == Schema:
            set_default = schema.schema.get('__set_default', never)
            keys = [k  for k in schema.schema.keys() if k not in self.kw] #  ['__set_document']]
            for k in keys:
                try:
                    schema[k]
                    value[k]
                except KeyError:
                    raise PathError('path does not exist')
                except TypeError:
                    raise PathError('path does not exist')
                
                if not schema[k].get('set', set_default)(doc):
                    raise SetError('no se puede setear, set')
                if 'computed' in schema[k]:
                    value[k] = schema[k]['computed'](value)   
                #value[k] = schema[k].get('computed', lambda v: v[k])(value)
                if not schema[k]['type'] == type(value[k]) and not schema[k].get('validation', public)(value[k]):
                    raise ValidationError('no se puede setear, validation')
            return value
        else:
            doc['__owners'] = owners
            if not to_set(doc):
                raise SetError('no se puede setear, set')
            if computed is not None:
                value = computed(value) 
            if schema == type(value) and validation(value):
                return value
            else:
                raise ValidationError('no se puede setear, validation')

if __name__ == '__main__':
    sch = {
        '__set_document': public,
        'a': {
            'type': int,
            'set': public,
            'validation': lambda v: v > 5
        },
        'date': {
            'type': float,
            'set': public,
            'computed': now
        }
    }
    A = Schema(sch)
    sch = {
        'b': {
            'get': hidden,
            'set': public,
            'type': [A]
        },
    }
    B = Schema(sch)

    doc = {
        'b': [{
            'a': 7
        }
        ]
    }

    #val = B.put('b.0', doc, {'a': 7})
    #print(val)

    #val = B.post(doc)
    #print(val)

    val = B.get(doc)
    print(val)