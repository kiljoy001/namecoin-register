
async def wrap_in_tuple(obj):
    return (obj,) if not isinstance(obj, tuple) else obj