from api import api_get, api_put, api_post
from bottle import run, debug, default_app
from pymongo import MongoClient
from offer_schema import OfferSchema
import jwt 

client = MongoClient()
db = client.test_database

JWT_SECRET = 'secret'
JWT_ALGORITHM = 'HS256'
print(jwt.encode({'user': 'miguel', 'roles': ['user', 'offerer']}, JWT_SECRET, algorithm=JWT_ALGORITHM))


api_get('/offer/<id>', db.offer, OfferSchema)
api_put('/offer/<id>', db.offer, OfferSchema)
@api_post('/offers',db.offer, OfferSchema)
def offer_post(payload):
    pass
    
application = default_app()
if __name__ == '__main__':
    debug(True)
    run(reloader=True)