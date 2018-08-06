from api import api_post, api_get_many, ArgumentError

from message_schema import MessageSchema
from db import db
from pymongo import DESCENDING

@api_post('/api/messages', db.messages, MessageSchema)
def post_message():
    pass

@api_get_many('/api/messages/<offset:int>/<limit:int>', db.messages, MessageSchema, max_limit=100)
def get_many_messages(params, filter):
    if 'id' in params:
        filter['id'] = params['id']
    else:
        raise ArgumentError('id not in params')
    return None, filter, [("date", DESCENDING)]