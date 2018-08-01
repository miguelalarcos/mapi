from api import after_put, returns_json, api_get, api_put, api_post, api_get_unique, api_get_many, current_user, api_aggregation, returns_json
from bottle import run, debug, default_app, request, hook, response, route, get, put
#from pymongo import MongoClient
from offer_schema import OfferSchema
from candidature_schema import CandidatureSchema
#from project_schema import ProjectSchema
from tag_schema import TagSchema
from user_schema import UserSchema
import jwt 
import json
from bson.objectid import ObjectId
import re
import os
from api import ArgumentError
import requests
from db import db
from pymongo import ASCENDING


from dotenv import load_dotenv
load_dotenv()

#MONGO_URL = os.getenv("MONGO_URL")
#DATA_BASE= os.getenv("DATA_BASE")
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
CLIENT_ID_GITHUB = os.getenv("CLIENT_ID_GITHUB")
CLIENT_SECRET_GITHUB = os.getenv("CLIENT_SECRET_GITHUB")

#client = MongoClient(MONGO_URL)
#db = client[DATA_BASE]

import project_routes

@route('/api/<:re:.*>', method='OPTIONS')
def getRoot(*args, **kwargs):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Authorization, Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

@route('/api/v2/<:re:.*>', method='OPTIONS')
def getRoot(*args, **kwargs):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Authorization, Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

@api_get_unique('/api/user/<unique>/<value>', db.user, UserSchema)
def get_user_by_unique():
    return {'password': 0}

@api_put('/api/offer/<id>', db.offer, OfferSchema)
def put_offer():
    pass

@api_put('/api/candidature-message/<id>', db.candidature, CandidatureSchema)
def put_candidature():
    return {'messages': 1, 'offerer': 1, '__owners': 1}

@after_put('/api/candidature-message/<id>')
def after_put_message(doc):
    print(doc)

@api_put('/api/candidature/<id>', db.candidature, CandidatureSchema)
def put_candidature_prop():
    return {'messages': 0}

@api_post('/api/offers',db.offer, OfferSchema)
def offer_post():
    pass
    
@api_get_many('/api/offers/<offset:int>/<limit:int>',db.offer, OfferSchema, max_limit=10)
def offer_get_many(params, filter):
    offerer = params['offerer']
    filter['offerer'] = offerer
    return None, filter, [("created_at", ASCENDING)]

###

@api_get_many('/api/candidatures/<offset:int>/<limit:int>', db.candidature, CandidatureSchema, max_limit=10)
def get_many_candidatures(params, filter):
    if 'offer' in params:
        filter['offer'] = params['offer']
    if 'my' in params:
        filter['candidate'] = current_user()
    #else: raise
    return {'messages': 0}, filter, [("created_at", ASCENDING)]

@api_get_many('/api/search-offers/<offset:int>/<limit:int>', db.offer, OfferSchema, max_limit=10)
def get_many_search_offers(params, filter):
    if 'tags' in params:
        filter['tags'] = {"$in": params['tags'].split(',')}
    #else: raise
    return None, filter, [("created_at", ASCENDING)]

#@api_get_many('/api/tags/<offset:int>/<limit:int>', db.tags, TagSchema, max_limit=10)
#def get_many_tags(params, filter): # get_many_offers
#    if 'value' in params:
#        filter['tag'] = re.compile('^' + params['value'] + '.*', re.IGNORECASE)
#    else:
#        raise ArgumentError('name not in keywords')
#    return None, filter

#@put('/api/tags/<tag>')
#@returns_json
#def upsert_tag(tag):
#    db.tags.update({"tag": tag}, {"$inc": {"total": 1}}, True)
#    return {"upsert tag": tag}

@api_get('/api/candidature/<id>', db.candidature, CandidatureSchema)
def get_candidature(id):
    return {'messages': 0}

@api_put('/api/add-experience/<id>', db.user, UserSchema)
def append_experience():
    pass

@api_get('/api/candidature-with-messages/<id>', db.candidature, CandidatureSchema)
def get_candidature(id):
    pass

@api_get('/api/candidate/<id>', db.user, UserSchema)
def get_candidate(id):
    return {"password": 0}

@api_post('/api/candidatures', db.candidature, CandidatureSchema)
def post_candidature():
    pass

@get('/api/login')
@returns_json
def get_user():
    code = request.params['code']
    data = {"client_id": CLIENT_ID_GITHUB, "client_secret": CLIENT_SECRET_GITHUB, "code": code}
    res = requests.post("https://github.com/login/oauth/access_token", data=data)
    patt = re.compile("access_token=(?P<token>.+)&")
    token = patt.match(res.text).group('token')
    res = requests.get("https://api.github.com/user?scope=user:email&access_token=" + token)
    data = json.loads(res.text)
    login = data['login']
    doc = db.user.find_one({'login': login}, {'password': 0})  
    if doc:  
        doc['jwt'] = (jwt.encode({'user': login, 'user_id': str(doc['_id'])}, JWT_SECRET, algorithm=JWT_ALGORITHM)).decode()
        doc['_id'] = str(doc['_id'])
        return doc
    else:
        #habria que crear al usuario con la info recibida de github
        return {'msg': 'user not found'}


@api_aggregation('/api/message-aggregation', db.candidature)
def message_aggregation():
    return [
        { "$match": {"candidate": current_user()} }, 
        { "$unwind": "$messages" },
        { "$match": {"messages.unread": True, "messages.owner": {"$ne": current_user()} }},
        {"$group": {
            "_id": "$_id", 
            "total": {
                "$sum": 1
                }
            }
        }
        ] 

@api_aggregation('/api/message-aggregation-candidates/<candidatures>', db.candidature)
def message_aggregation_candidates(candidatures):
    candidatures = candidatures.split(',')
    candidatures = [ObjectId(x) for x in  candidatures]
    return [
        { "$match": {"_id": {"$in": candidatures} } }, 
        { "$unwind": "$messages" },
        { "$match": {"messages.unread": True, "messages.owner": {"$ne": current_user()} }},
        {"$group": {
            "_id": "$_id", 
            "total": {
                "$sum": 1
                }
            }
        }
        ]

@api_aggregation('/api/message-aggregation-offerer', db.candidature)
def message_aggregation_offerer():
    return [
        { "$match": {"offerer": current_user()} }, 
        { "$unwind": "$messages" },
        { "$match": {"messages.unread": True, "messages.owner": {"$ne": current_user()} }},
        {"$group": {
            "_id": "$offer", 
            "total": {
                "$sum": 1
                }
            }
        }
        ] 

@api_aggregation('/api/new-candidates/<offer>', db.candidature)
def new_candidates(offer):
    return [
        { "$match": {"offer": {"$in": offer.split(',')}, "unread": True, "status": "open"}}, 
        {"$group": {
            "_id": "$offer", 
            "total": {
                "$sum": 1
                }
            }
        }
    ]

@api_aggregation('/api/total-actives-aggregation/<offer>', db.candidature)
def total_actives(offer):
    return [
        { "$match": {"offer": {"$in": offer.split(',')}, "status": "open"}}, 
        {"$group": {
            "_id": "$offer", 
            "total": {
                "$sum": 1
                }
            }
        }
        ] 

@api_aggregation('/api/already-subscribed-aggregation/<offer>', db.candidature)
def already_subscribed(offer):
    return [
        { "$match": {"offer": {"$in": offer.split(',')}, "status": "open", "candidate": current_user()}}, 
        {"$group": {
            "_id": "$offer", 
            "total": {
                "$sum": 1
                }
            }
        }
        ] 

application = default_app()
if __name__ == '__main__':
    debug(True)
    PORT = os.getenv("PORT")
    run(reloader=True, port=PORT)