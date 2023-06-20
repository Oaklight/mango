import os
import json
import datetime
import random
import traceback

def find_json(directory):
    json_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                json_files.append(os.path.join(root, file))
    return json_files

def read_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def save_json(save_path, save_object, prefix=''):
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    now = datetime.datetime.now()
    now_str = now.strftime("%Y-%m-%d-%H-%M-%S")
    json_path = os.path.join(save_path, prefix + now_str + '_' + str(random.randint(0,1e3)).zfill(3) + '.json')
    json_object = json.dumps(save_object, indent=4)
    with open(json_path, 'w') as f:
        f.write(json_object)
    return json_path

def replace_str_in_dict(obj, replace_dict):
    if isinstance(obj, dict):
        return {k: replace_str_in_dict(v, replace_dict) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_str_in_dict(i, replace_dict) for i in obj]
    elif isinstance(obj, str):
        if obj in replace_dict.keys():
            
            obj = replace_dict[obj]
        return obj
    else:
        return obj
    
def get_timetsamp_with_random():
    now = datetime.datetime.now()
    now_str = now.strftime("%Y-%m-%d-%H-%M-%S")
    return  now_str + '_' + str(random.randint(0,1e3)).zfill(3)