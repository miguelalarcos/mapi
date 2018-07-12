from api import api_get, api_put, api_post, api_get_many, current_user, api_aggregation
from bottle import run, debug, default_app, request, hook, response, route, get
from pymongo import MongoClient
from offer_schema import OfferSchema
from candidature_schema import CandidatureSchema
import jwt 
import json

client = MongoClient()
db = client.test_database

JWT_SECRET = 'secret'
JWT_ALGORITHM = 'HS256'
print(jwt.encode({'user': 'miguel', 'roles': ['user', 'offerer']}, JWT_SECRET, algorithm=JWT_ALGORITHM))

@route('/<:re:.*>', method='OPTIONS')
def getRoot(*args, **kwargs):
    print('Route handler')
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Authorization, Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'


@api_get('/offer/<id>', db.offer, OfferSchema)
def get_offer():
    pass

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
    title = params['title']
    filter['title'] = {'$regex':'^.*' + title + '.*$'}
    return {'tags': 0}, filter

###
@api_get('/candidature/<id>', db.candidature, CandidatureSchema)
def get_candidature():
    return {'messages': 0}


@api_get('/candidature-with-messages/<id>', db.candidature, CandidatureSchema)
def get_candidature():
    pass

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

application = default_app()
if __name__ == '__main__':
    debug(True)
    run(reloader=True, port=8081)