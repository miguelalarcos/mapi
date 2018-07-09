from bottle import get, response, put, post, request
import json
import jwt 
from bson.objectid import ObjectId

JWT_SECRET = 'secret'
JWT_ALGORITHM = 'HS256'

def current_user(*args): 
    jwt_token = request.headers.get('Authorization')
    jwt_payload = jwt.decode(jwt_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    return jwt_payload.get('user') 

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

def dumps(obj):
    return json.dumps(obj)

def returns_json(f):
    def helper(*args, **kwargs):
        response.content_type = 'application/json'
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
        ret = f(*args, **kwargs)
        return dumps(ret)
    return helper

def catching(f):
    def helper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except jwt.DecodeError:
            response.status = 500
            return {'error': 'jwt decode error'}
        except json.JSONDecodeError:
            response.status = 500
            return {'error': 'json decode error'}
        except ArgumentError:
            response.status = 500
            return {'error': 'argument error'}
    return helper

def api_get(route, collection, schema):
    @get(route)
    @returns_json
    @catching
    def helper(id):
        response.status = 200
        id = ObjectId(id)
        filter = {"_id": id}
        if schema['__ownership']:
            filter.update({'owner': current_user()})
        doc = collection.find_one(filter)
        doc['_id'] = str(id)
        return schema.get(doc)
    return helper

def api_put(route, collection, schema):
    @put(route)
    @returns_json
    @catching
    def helper(id):
        response.status = 201
        id = ObjectId(id)
        old_doc = collection.find_one({"_id": id})
        js = current_payload()
        t = '$set'
        if js['type'] == '$push':
            t = '$push'
        mod = {}
        for data in js['data']:
            doc = schema.put(data['path'], old_doc, data['value'])
            mod['path'] = doc       
        collection.update({"_id": id}, {t: mod})
        doc = collection.find_one({"_id": id})
        doc['_id'] = str(id)
        return schema.get(doc)
    return helper

def api_post(route, collection, schema):
    def decorator(f):
        @post(route)
        @returns_json
        @catching
        def helper():            
            response.status = 201
            payload = current_payload()
            ctx = f(payload)
            if ctx is None:
                ctx = {}
            payload = schema.post(payload, ctx)
            _id = collection.insert_one(payload).inserted_id
            payload['_id'] = str(_id)
            return payload
        return helper
    return decorator
