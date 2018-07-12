from schema import Schema, public, current_user, read_only, default, required, is_owner, now
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
    }
}

Message = Schema(plain_schema)

plain_schema = {
    "__ownership": False,
    #"__create_document": has_role('offerer'),
    "__set_document": is_owner,
    "__set_default": is_owner,
    "__get_default": is_owner,
    "__owners": {
        "type": list,
        "set": read_only,
        "initial": lambda ctx: [current_user()]
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
        "get": is_owner,
        "set": is_owner
    },
    "messages": {
        "type": [Message],
        "get": is_owner,
        "set": is_owner
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
