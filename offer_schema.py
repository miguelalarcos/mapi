from schema import Schema, public, current_user, read_only, default, required,\
                   is_owner, now
from api import has_role, current_user_id

def provinces():
    #access mongo or not
    return ['Murcia', 'Alicante']

plain_schema = {
    "__ownership": False,
    "__set_document": is_owner,
    "__create_document": has_role('offerer'),
    "__set_default": public,
    "__get": public,
    "__set": is_owner,
    "__owners": {
        "type": list,
        "set": read_only,
        "initial": lambda ctx: [current_user()]
    },
    "_id": {
        "type": str,
        "set": read_only
    },
    "offerer": {
        "type": str,
        "initial": current_user,
        "set": read_only
    },
    "title": {
        "type": str,
        "required": True,
        "validation": lambda v: 0 < len(v) <= 30
    },
    "description": {
        "type": str,
        "required": True,
        "validation": lambda v: 0 < len(v) <= 1000
    },
    "tags": {
        "type": list,
        "required": True
    },
    "province": {
        "type": str,
        "validation": lambda v: v in provinces()
    },
    "remote": {
        "type": bool,
        "required": True,
    },
    "questions": {
        "type": str,
        "get": is_owner,
        "required": False,
        "validation": lambda v: 0 < len(v) < 1000
    },
    "salary-min": {
        "type": float,
        "required": False
    },
    "salary-max": {
        "type": float,
        "required": False
    },
    "user_id": {
        "type": str,
        "initial": current_user_id,
        "set": read_only,
    },
    "status": {
        "type": str,
        "initial": default('open'),
        "required": True,
        "validation": lambda v: v in ['open', 'closed']
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

OfferSchema = Schema(plain_schema)
