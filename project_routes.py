from api import api_get, api_put_v2, api_post, api_get_many, ArgumentError
from project_schema import ProjectSchema
from db import db
from pymongo import ASCENDING

@api_get('/api/project/<id>', db.project, ProjectSchema)
def get_project(id):
    pass

@api_put_v2('/api/project/<id>', db.project, ProjectSchema)
def put_project():
    pass

@api_get_many('/api/projects/<offset:int>/<limit:int>', db.project, ProjectSchema, max_limit=10)
def get_many_search_projects(params, filter):
    if 'tags' in params:
        filter['tags'] = {"$in": params['tags'].split(',')}
    else: 
        raise ArgumentError('tags not in params')
    return None, filter, [("created_at", ASCENDING)]

@api_post('/api/projects',db.project, ProjectSchema)
def offer_post():
    pass

