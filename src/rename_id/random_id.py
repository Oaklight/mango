import json
import os, sys

import random

# find out all subfolders in given dir
data_path = "./data-intermediate-id"
subfolders = [
    f.name for f in os.scandir(data_path) if f.is_dir()
]  # enlist only the last level of folder name
games = [f for f in subfolders if os.path.exists(f"{data_path}/{f}/{f}.code2anno.json")]

# keep the subfolder if there is *.code2anno.json
# subfolders = [f fouse_alternative_r f in subfolders if os.path.exists(f + ".code2anno.json")]
print(len(games))
print(games)

for g in games:
    anno2code_edit_path = f"{data_path}/{g}/{g}.anno2code_edit.json"

    with open(anno2code_edit_path, "r") as f:
        anno2code_dict = json.load(f)
    
    rand_used = set()

    for k, v in anno2code_dict.items():
        if len(v) > 0:
            rand_id = random.randint(0, 999)
            while rand_id in rand_used:
                rand_id = random.randint(0, 999)
            rand_used.add(rand_id)

            code = v[0]
            root_str, id_str = code.split('(id')
            code_new = f"{root_str}(id{rand_id})"
            anno2code_dict[k] = [code_new]
    
    with open(anno2code_edit_path, 'w') as f:
        json.dump(anno2code_dict, f, indent=4)