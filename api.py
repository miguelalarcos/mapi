from bottle import get, response, put, post, request
import json
import jwt 
from bson.objectid import ObjectId
from errors import SetError, ValidationError, PathError

JWT_SECRET = 'secret'
JWT_ALGORITHM = 'HS256'

after_put_hooks = {}

def after_put(route):
    def decorator(f):
        def helper(*args, **kwargs):
            f(*args, **kwargs)
        after_put_hooks[route] = helper
        return helper
    return decorator

def is_logged(*args):
    jwt_token = request.headers.get('Authorization')
    jwt_payload = jwt.decode(jwt_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    return True

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
        except SetError:
            response.status = 500
            print('set error')
            return {'error': 'set error'}
        except ValidationError:
            response.status = 500
            print('validation error')
            return {'error': 'validation error'}
        except PathError:
            response.status = 500
            print('path error')
            return {'error': 'path error'}
        except Exception:
            response.status = 500
            print('error')
            return {'error': 'error'}
        
    return helper

def api_get(route, collection, schema):
    def decorator(f):
        @get(route)
        @returns_json
        #@catching
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

def api_get_unique(route, collection, schema):
    def decorator(f):
        @get(route)
        @returns_json
        #@catching
        def helper(unique, value):
            response.status = 200
            id = ObjectId(id)
            filter = {}
            filter[unique] = value
            if schema['__ownership']:
                filter.update({'__owners': current_user()})
            proj = f()
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

def api_put_v2(route, collection, schema):
    def decorator(f):
        @put(route)
        @returns_json
        #@catching
        def helper(id):
            response.status = 201
            id = ObjectId(id)
            old_doc = collection.find_one({"_id": id})
            if old_doc is None:
                raise NoneDocError('no document found')
            js = current_payload()
            payload = {}
            for k in js:
                if k in ('$set', '$push', '$addToSet'):
                    payload[k] = {}
                    for path, value in js[k].items():
                        if k in ('$push', '$addToSet'):
                            doc = schema.put(path, old_doc, value, False, True)
                        else:
                            doc = schema.put(path, old_doc, value)
                        payload[k][path] = doc
                elif k == '$pull':
                    payload[k] = {}    
                    for path, value in js[k].items():
                        if schema.put(path, old_doc, "", True):
                            payload[k][path] = value
            collection.update_one({"_id": id}, payload)
            proj = f()
            if proj:
                doc = collection.find_one({"_id": id}, proj)
            else:
                doc = collection.find_one({"_id": id})
            doc['_id'] = str(id)
            doc = schema.get(doc)
            hook = after_put_hooks.get(route)
            if hook:
                hook(doc)
            return doc
        return helper
    return decorator

def api_put(route, collection, schema):
    def decorator(f):
        @put(route)
        @returns_json
        #@catching
        def helper(id):
            response.status = 201
            id = ObjectId(id)
            old_doc = collection.find_one({"_id": id})
            if old_doc is None:
                raise NoneDocError('no document found')
            js = current_payload()
            t = '$set'
            if js['type'] == '$push':
                t = '$push'
            elif js['type'] == '$addToSet':
                t = '$addToSet'
            elif js['type'] == '$pull':
                t = '$pull'
            mod = {}
            for data in js['data']:
                if t == '$pull':
                    if schema.put(data['path'], old_doc, "", True):
                        mod[data['path']] = data['value']    
                else:
                    doc = schema.put(data['path'], old_doc, data['value'])
                    mod[data['path']] = doc       
            
            collection.update_one({"_id": id}, {t: mod})
            proj = f()
            if proj:
                doc = collection.find_one({"_id": id}, proj)
            else:
                doc = collection.find_one({"_id": id})
            doc['_id'] = str(id)
            doc = schema.get(doc)
            hook = after_put_hooks.get(route)
            if hook:
                hook(doc)
            return doc
        return helper
    return decorator

def api_post(route, collection, schema):
    def decorator(f):
        @post(route)
        @returns_json
        #@catching
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
        #@catching
        def helper(offset, limit):
            response.status = 200
            filter = {}
            if schema['__ownership']:
                filter.update({'__owners': current_user()})
            limit = min(limit, max_limit)
            proj, filter, order = f(request.params, filter)
            if proj:
                docs = collection.find(filter, proj).sort(order).skip(offset).limit(limit)
            else:
                docs = collection.find(filter).sort(order).skip(offset).limit(limit)
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