from api import api_get, api_put, api_post, api_get_many, current_user, api_aggregation, returns_json
from bottle import run, debug, default_app, request, hook, response, route, get
from pymongo import MongoClient
from offer_schema import OfferSchema
from candidature_schema import CandidatureSchema
from user_schema import UserSchema
import jwt 
import json
from bson.objectid import ObjectId

client = MongoClient()
db = client.test_database

JWT_SECRET = 'secret'
JWT_ALGORITHM = 'HS256'
#print(jwt.encode({'user': 'miguel.alarcos@gmail.com', 'roles': ['user', 'offerer']}, JWT_SECRET, algorithm=JWT_ALGORITHM))

@route('/<:re:.*>', method='OPTIONS')
def getRoot(*args, **kwargs):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Authorization, Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'


#@api_get('/offer/<id>', db.offer, OfferSchema)
#def get_offer():
#    pass

#@api_put('/offer/<id>', db.offer, OfferSchema)

@api_put('/candidature-message/<id>', db.candidature, CandidatureSchema)
def put_candidature():
    return {'messages': 1, 'offerer': 1, '__owners': 1}

@api_put('/candidature/<id>', db.candidature, CandidatureSchema)
def put_candidature_prop():
    return {'messages': 0}

@api_post('/offers',db.offer, OfferSchema)
def offer_post():
    pass
    
@api_get_many('/offers/<offset:int>/<limit:int>',db.offer, OfferSchema, max_limit=10)
def offer_get_many(params, filter):
    offerer = params['offerer']
    filter['offerer'] = offerer
    print(filter)
    return None, filter

###

@api_get_many('/candidatures/<offset:int>/<limit:int>', db.candidature, CandidatureSchema, max_limit=10)
def get_many_candidatures(params, filter):
    if 'offer' in params:
        filter['offer'] = params['offer']
    #if 'my' in params:
    #    filter['candidate'] = current_user()
    #else: raise
    return {'messages': 0}, filter

@api_get_many('/search-offers/<offset:int>/<limit:int>', db.offer, OfferSchema, max_limit=10)
def get_many_candidatures(params, filter): # get_many_offers
    if 'tags' in params:
        filter['tags'] = {"$in": params['tags'].split(',')}
    #else: raise
    return None, filter

@api_get('/candidature/<id>', db.candidature, CandidatureSchema)
def get_candidature(id):
    return {'messages': 0}

@api_put('/add-experience/<id>', db.user, UserSchema)
def append_experience():
    pass

@api_get('/candidature-with-messages/<id>', db.candidature, CandidatureSchema)
def get_candidature(id):
    pass

@api_get('/candidate/<id>', db.user, UserSchema)
def get_candidate(id):
    return {"password": 0}

@api_post('/candidatures', db.candidature, CandidatureSchema)
def post_candidature():
    pass


@get('/login')
@returns_json
def get_user():
    print('get_user')
    name = request.params['name']
    doc = db.user.find_one({'email': name}, {'password': 0})
    print('fetched')
    doc['jwt'] = (jwt.encode({'user': name, 'user_id': str(doc['_id'])}, JWT_SECRET, algorithm=JWT_ALGORITHM)).decode()
    doc['_id'] = str(doc['_id'])
    return doc


@api_aggregation('/message-aggregation', db.candidature)
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

@api_aggregation('/message-aggregation-candidates/<candidatures>', db.candidature)
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

@api_aggregation('/message-aggregation-offerer', db.candidature)
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

@api_aggregation('/new-candidates/<offer>', db.candidature)
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

@api_aggregation('/total-actives-aggregation/<offer>', db.candidature)
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

@api_aggregation('/already-subscribed-aggregation/<offer>', db.candidature)
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
    #debug(True)
    run(reloader=True, port=8081)