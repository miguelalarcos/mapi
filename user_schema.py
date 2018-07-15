from schema import Schema, public, current_user, read_only, default, \
     required, is_owner, now, current_user_is, never
from api import has_role

plain_schema = {
    "__get_default": public,
    "__set_default": is_owner,
    "tags": {
        "type": str,
        "required": True
    },
    "description": {
        "type": str,
        "required": True,
        "validation": lambda v: 0 <= len(v) <= 500
    }
}

Experience = Schema(plain_schema)

def tags(doc):
    s = set()
    for exp in doc['experience']:
        exps = exp['tags'].split(',')
        exps = [e.strip() for e in exps if e != '']
        for e in exps:
            s.add(e)
    return list(s)

plain_schema = {
    "__ownership": False,
    #"__create_document": has_role('offerer'),
    "__set_document": is_owner,
    "__set_default": is_owner,
    "__get_default": public,
    "__ownership": True,
    "__owners": {
        "type": list,
        "set": read_only,
        "initial": lambda payload: [payload['name']]
    },
    "_id": {
        "type": str,
        "set": read_only
    },
    "name": {
        "type": str,
        "required": True,
        "set": is_owner,
        "validation": lambda v: 0 <= len(v) <= 30
    },
    "email": {
        "type": str,
        "required": True,
        "set": is_owner,
        "validation": lambda v: 0 <= len(v) <= 30
    },
    "password": {
        "type": str,
        "get": never,
        "set": never
    },
    "tags": {
        "type": list,
        "computed": lambda doc: tags(doc)
    },
    "phone": {
        "type": str,
        "required": True,
        "set": is_owner,
        "validation": lambda v: 0 <= len(v) <= 30
    },
    "experience": {
        "type": [Experience],
        "set": is_owner
    },
    "province":{
        'type': str,
        'set': is_owner,
        "validation": lambda v: 0 <= len(v) <= 30
    },
    "created_at": {
        "type": float,
        "initial": now,
        "set": read_only
    },
    "updated_at": {
        "type": float,
        "initial": now,
        "computed": now
    }
}

UserSchema = Schema(plain_schema)
