import time
from api import current_user

class SetError(Exception):
    pass

now = lambda *args: time.time()
identity = lambda x: x
public = lambda *args: True
never  = lambda *args: False
hidden = lambda *args: False

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

        for key in intersection:
            g = schema[key].get('get', public)
            v = g(document)
            
            if schema[key]['type'].__class__ == Schema:
                if not v:
                    ret[key] = None
                else:
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
            print(schema, key)
            if schema[key]['type'].__class__ == Schema:
                if document.get(key):
                    ret[key] = schema[key].post(document[key])
            elif type(schema[key]['type']) is list:
                schema = schema[key]['type'][0]
                ret[key] = [schema.post(k) for k in document[key]]
            elif 'computed' not in schema[key]:
                validation = schema[key].get('validation', lambda v: True)
                initial = schema[key].get('initial')
                initial = initial and initial(context)
                if not validation(document.get(key, initial)):
                    raise Exception('not valid prop or missing', key)
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
        doc = root_doc
        paths = path.split('.')
        last = paths[-1]
        for key in paths:
            if key.isdigit():
                key = int(key)   
                if schema.__class__ == Schema and not schema.schema.get('set', set_default)():
                    raise SetError('no se puede setear, set')
            else:
                try:
                    validation = schema[key].get('validation', validation)
                except KeyError:
                    raise Exception('path does not exist')
                to_set = schema[key].get('set', set_default)
                schema = schema[key]['type']
                if type(schema) is list:
                    schema = schema[0]
            #doc = doc[key]            
            if schema.__class__ == Schema and key != last:
                doc = doc[key]
                #s = schema.schema.get('set', set_default) 
                #if s(doc):
                if to_set(doc):
                    continue
                else:
                    raise SetError('no se puede setear, set')
        
        if schema.__class__ == Schema:
            set_default = schema.schema.get('__set_default', never)
            keys = [k  for k in schema.schema.keys() if k not in self.kw] #  ['__set_document']]
            for k in keys:
                try:
                    schema[k]
                except KeyError:
                    raise Exception('path does not exist')
                if not schema[k].get('set', set_default)():
                    raise SetError('no se puede setear, set')
                value[k] = schema[k].get('computed', lambda v: v[k])(value)
                if not schema[k].get('validation', public)(value[k]):
                    raise SetError('no se puede setear, validation')
            return value

        if not to_set(doc):
            raise SetError('no se puede setear, set')
        if validation(value):
            return value
        else:
            raise Exception('no se puede setear, validation')

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