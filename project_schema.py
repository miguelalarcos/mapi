from schema import Schema, read_only, default, required,\
                   is_owner, now
from api import has_role, current_user_id, current_user, is_logged

plain_schema = {
    "__get_default": is_owner,
    "__set_default": is_owner,
    "owner": {
        "type": str,
        "initial": current_user,
        "set": read_only
    },
    "msg": {
        "type": str,
        "required": True,
        "set": read_only,
        "validation": lambda v: 0 <= len(v) <= 300
    },
    "date": {
        "type": float,
        "initial": now,
        "set": read_only
    }
}

Message = Schema(plain_schema)

def provinces():
    #access mongo or not
    return ['Murcia', 'Alicante']

def is_participant(doc):
    if current_user() in doc['participants']:
        return True
    else:
        return False

plain_schema = {
    "__ownership": False,
    "__set_document": is_owner,
    "__set_default": is_owner,
    "__owners": { 
        "type": list,
        "set": read_only,
        "initial": lambda ctx: [current_user()]
    },
    "_id": {
        "type": str,
        "set": read_only
    },
    "title": {
        "type": str,
        "validation": lambda v: len(v) <= 100
    },
    "description": {
        "type": str,
        "validation": lambda v: len(v) <= 3000
    },
    "tags": {
        "type": list,
        "initial": lambda ctx: []
    },
    "province": {
        "type": str,
        "validation": lambda v: v in provinces()
    },
    "status": {
        "type": str,
        "initial": default('draft'),
        "validation": lambda v: v in ['draft', 'open', 'closed']
    },
    "participants": {
        "type": list,
        "initial": lambda ctx: [current_user()],
        "push": lambda v, doc: is_owner or current_user() in doc['invited'],
        "pull": lambda v, doc: current_user() in doc['participants']
    },
    "solicitations": {
        "type": list,
        "initial": lambda ctx: [],
        "push": is_logged,
        "pull": lambda v, doc: is_owner() or current_user() == v
    },
    "invited": {
        "type": list,
        "initial": lambda ctx: [],
        "push": is_owner,
        "pull": lambda v, doc: is_owner() or current_user() == v
    },
    "unread": {
        "type": list,
        "initial": lambda ctx: [],
        "push": is_participant,
        "pull": is_participant
    },
    "messages": {
        "type": [Message],
        "get": is_participant,
        "set": is_participant
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

ProjectSchema = Schema(plain_schema)
