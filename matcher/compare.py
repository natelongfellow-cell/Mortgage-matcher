import json
from .scoring import score_fields

def compare_json_files(data1: bytes, data2: bytes):
    obj1 = json.loads(data1)
    obj2 = json.loads(data2)

    results = {}
    for key in obj1:
        if key in obj2:
            results[key] = score_fields(obj1[key], obj2[key])
        else:
            results[key] = {"match": False, "score": 0}

    return {"results": results}
