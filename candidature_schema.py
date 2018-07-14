from schema import Schema, public, current_user, read_only, default, \
     required, is_owner, now, current_user_is
from api import has_role

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
        "validation": lambda v: 0 <= len(v) <= 300
    },
    "date": {
        "type": float,
        "initial": now,
        "set": read_only
    },
    "unread": {
        "type": bool,
        "initial": lambda *args: True,
        "get": is_owner,
        "set": is_owner
    }
}

Message = Schema(plain_schema)

plain_schema = {
    "__ownership": True,
    #"__create_document": has_role('offerer'),
    "__set_document": is_owner,
    "__set_default": is_owner,
    "__get_default": is_owner,
    "__owners": {
        "type": list,
        "set": read_only,
        "initial": lambda payload: [current_user(), payload['offerer']]
    },
    "_id": {
        "type": str,
        "set": read_only
    },
    "company": {
        "type": str,
        "set": read_only
    },
    "title": {
        "type": str,
        "required": True,
        "validation": lambda v: 0 <= len(v) <= 30
    },
    "description": {
        "type": str,
        "required": True,
        "validation": lambda v: 0 <= len(v) <= 300
    },
    "status": {
        "type": str,
        "required": True,
        "set": current_user_is('offerer'),
        "validation": lambda v: v in ['open', 'discarded']
    },
    "tags": {
        "type": list
    },
    "candidate": {
        "type": str,
        "initial": current_user
    },
    "mark": {
        "type": float
    },
    "offerer": {
        "type": str,
        "required": True,
        "validation": lambda v: 0 <= len(v) <= 30
    },
    "offer": {
        "type": str,
        "required": True
    },
    #"status": {
    #    "type": str,
    #    "initial": default('open'),
    #    "required": True,
    #    "validation": lambda v: v in ['open', 'closed']
    #},
    "candidateObservations": {
        "type": str,
        "get": current_user_is('candidate'),
        "set": current_user_is('candidate')
    },
    "offererObservations": {
        "type": str,
        "get": current_user_is('offerer'),
        "set": current_user_is('offerer')
    },
    "messages": {
        "type": [Message],
        "get": is_owner,
        "set": is_owner
    },
    "date":{
        'type': float,
        'set': read_only
    },
    "province":{
        'type': str,
        'set': read_only
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

CandidatureSchema = Schema(plain_schema)
