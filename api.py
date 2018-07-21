from bottle import get, response, put, post, request
import json
import jwt 
from bson.objectid import ObjectId
from errors import SetError, ValidationError, PathError

JWT_SECRET = 'secret'
JWT_ALGORITHM = 'HS256'

def current_user(*args): 
    jwt_token = request.headers.get('Authorization')
    jwt_payload = jwt.decode(jwt_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    return jwt_payload.get('user') 

def current_user_id(*args): 
    jwt_token = request.headers.get('Authorization')
    jwt_payload = jwt.decode(jwt_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    return jwt_payload.get('user_id') 

def current_payload():
    return request.json

def has_role(role):
    def helper(*args):
        jwt_token = request.headers.get('Authorization')
        jwt_payload = jwt.decode(jwt_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return role in jwt_payload.get('roles')
    return helper

class ArgumentError(Exception):
    pass

class NoneDocError(Exception):
    pass

def dumps(obj):
    return json.dumps(obj)

def returns_json(f):
    def helper(*args, **kwargs):
        response.content_type = 'application/json'
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Authorization, Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
        ret = f(*args, **kwargs)
        return dumps(ret)
    return helper

def catching(f):
    def helper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except jwt.DecodeError:
            response.status = 500
            print('jwt decode error')
            return {'error': 'jwt decode error'}
        except json.JSONDecodeError:
            response.status = 500
            print('json decode error')
            return {'error': 'json decode error'}
        except ArgumentError:
            response.status = 500
            print('argument error')
            return {'error': 'argument error'}
        except NoneDocError:
            response.status = 500
            print('none doc error')
            return {'error': 'none doc error'}
        #except SetError:
        #    response.status = 500
        #    print('set error')
        #    return {'error': 'set error'}
        #except ValidationError:
        #    response.status = 500
        #    print('validation error')
        #    return {'error': 'validation error'}
        #except PathError:
        #    response.status = 500
        #    print('path error')
        #    return {'error': 'path error'}
        #except Exception:
        #    response.status = 500
        #    print('error')
        #    return {'error': 'error'}
        
    return helper

def api_get(route, collection, schema):
    def decorator(f):
        @get(route)
        @returns_json
        @catching
        def helper(id):
            response.status = 200
            id = ObjectId(id)
            filter = {"_id": id}
            if schema['__ownership']:
                filter.update({'__owners': current_user()})
            proj = f(id)
            if proj:
                doc = collection.find_one(filter, proj)
            else:
                doc = collection.find_one(filter)
            if doc is None:
                raise NoneDocError('no document found')
            doc['_id'] = str(id)
            return schema.get(doc)
        return helper
    return decorator

def api_put(route, collection, schema):
    def decorator(f):
        @put(route)
        @returns_json
        @catching
        def helper(id):
            #print('entro')
            response.status = 201
            id = ObjectId(id)
            old_doc = collection.find_one({"_id": id})
            #print('old doc', old_doc)
            if old_doc is None:
                raise NoneDocError('no document found')
            js = current_payload()
            #print('current payload', js)
            t = '$set'
            if js['type'] == '$push':
                t = '$push'
            elif js['type'] == '$pull':
                t = '$pull'
            mod = {}
            #print('t', t)
            for data in js['data']:
                if t == '$pull':
                    if schema.put(data['path'], old_doc, "", True):
                        mod[data['path']] = data['value']    
                else:
                    #print('else')
                    doc = schema.put(data['path'], old_doc, data['value'])
                    mod[data['path']] = doc       
            
            #print('previo update one', id, t, mod)
            collection.update_one({"_id": id}, {t: mod})
            proj = f()
            if proj:
                doc = collection.find_one({"_id": id}, proj)
                #print('doc al final', doc, proj)
            else:
                doc = collection.find_one({"_id": id})
                #print('doc al final, doc')
            doc['_id'] = str(id)
            return schema.get(doc)
        return helper
    return decorator

def api_post(route, collection, schema):
    def decorator(f):
        @post(route)
        @returns_json
        @catching
        def helper():            
            response.status = 201
            payload = current_payload()
            ctx = f() or {}
            payload = schema.post(payload, ctx)
            _id = collection.insert_one(payload).inserted_id
            payload['_id'] = str(_id)
            return payload
        return helper
    return decorator


def api_get_many(route, collection, schema, max_limit):
    def decorator(f):
        @get(route)
        @returns_json
        @catching
        def helper(offset, limit):
            response.status = 200
            filter = {}
            if schema['__ownership']:
                filter.update({'__owners': current_user()})
            limit = min(limit, max_limit)
            proj, filter = f(request.params, filter)
            if proj:
                docs = collection.find(filter, proj).limit(limit).skip(offset)
            else:
                docs = collection.find(filter).limit(limit).skip(offset)
            ret = []
            for doc in docs:
                doc['_id'] = str(doc['_id'])
                doc = schema.get(doc)
                ret.append(doc)
            return ret
        return helper
    return decorator

def api_aggregation(route, collection):
    def decorator(f):
        @get(route)
        @returns_json
        def helper(*args, **kwargs):
            pipeline = f(*args, **kwargs)
            ret_ = list(collection.aggregate(pipeline))
            ret = []
            for r in ret_:
                r['_id'] = str(r['_id'])
                ret.append(r)
            return ret
        return helper
    return decorator