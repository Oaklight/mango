import json 

def read_text(txt_path):
    with open(txt_path, 'r', encoding='utf-8') as fin:
        text = fin.read()
    return text

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        json_object = json.load(f)
    return json_object

def load_jsonl(file_path):
    json_object_list = []
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        json_object_list = [json.loads(line) for line in lines]
    return json_object_list

def save_json(json_object, file_path):
    with open(file_path, 'w+', encoding='utf-8') as fout:
        json.dump(json_object, fout, indent=4)