from schema import Schema, public, current_user, read_only, default, required, is_owner, now
from api import has_role

def provinces():
    #access mongo or not
    return ['Murcia', 'Alicante']

plain_schema = {
    "__ownership": False,
    "__create_document": has_role('offerer'),
    "__set_default": public,
    "__get": public,
    "__set": is_owner,
    "__owners": {
        "type": list,
        "set": read_only,
        "initial": lambda *args: [current_user()]
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
        "validation": lambda v: required(v) and type(v) is str and 0 < len(v) <= 30
    },
    "description": {
        "type": str,
        "validation": lambda v: required(v) and type(v) is str and 0 < len(v) <= 250
    },
    "tags": {
        "type": list,
        "validation": lambda v: required(v) and type(v) is list
    },
    "province": {
        "type": str,
        "validation": lambda v: v in provinces()
    },
    "remote": {
        "type": bool,
        "validation": lambda v: required(v) and type(v) is bool
    },
    "questions": {
        "type": str,
        "get": is_owner,
        "validation": lambda v: not v or type(v) is str and 0 < len(v) < 1000
    },
    "salary": {
        "type": str,
        "validation": lambda v: not v or type(v) is str and 0 <= len(v) <= 20
    },
    "status": {
        "type": str,
        "initial": default('open'),
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
