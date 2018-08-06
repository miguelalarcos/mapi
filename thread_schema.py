from schema import Schema, read_only, required, is_owner, now, current_user

plain_schema = {
    "__get_default": is_owner,
    "__set_default": read_only,
    "__ownership": True,
    "__owners": { 
        "type": list
    },
    "date": {
        "type": float,
        "initial": now
    },
    "participants": {
        "type": str # participant_a:participant_b
    }
}

Thread = Schema(plain_schema)