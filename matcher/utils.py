def normalize(value):
    if isinstance(value, str):
        return value.strip().lower()
    return value
