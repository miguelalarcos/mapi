from schema import Schema, public, current_user, read_only, default, \
     required, is_owner, now, current_user_is, never
from api import has_role

plain_schema = {
    "__get_default": public,
    "__set_default": never,
    "__ownership": False,
    "tag": {
        "type": str,
        "required": True
    },
    "total": {
        "type": float,
        "required": True
    }
}

TagSchema = Schema(plain_schema)

