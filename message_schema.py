from schema import Schema, read_only, required, is_owner, now, current_user

plain_schema = {
    "__get_default": is_owner,
    "__set_default": read_only,
    "__ownership": True,
    "__owners": { 
        "type": list,
        "set": read_only,
        "initial": lambda ctx: [current_user()]
    },
    "author": {
        "type": str,
        "initial": current_user,
        "validation": lambda v: 0 <= len(v) <= 300
    },
    "message": {
        "type": str,
        "required": True,
        "validation": lambda v: 0 <= len(v) <= 300
    },
    "date": {
        "type": float,
        "initial": now
    },
    "id": {
        "type": str
    }
}

MessageSchema = Schema(plain_schema)