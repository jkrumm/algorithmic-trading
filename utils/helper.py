def transform_cursor(obj):
    data = list(obj)
    for x in data:
        if '_id' in x: del x['_id']
    return data


def transform_cursor_dict(obj):
    if '_id' in obj: del obj['_id']
    return obj
