import json
import os

# find out all subfolders in given dir
data_path = "./data-intermediate"
subfolders = [
    f.name for f in os.scandir(data_path) if f.is_dir()
]  # enlist only the last level of folder name
games = [f for f in subfolders if os.path.exists(f"{data_path}/{f}/{f}.code2anno.json")]

# keep the subfolder if there is *.code2anno.json
# subfolders = [f for f in subfolders if os.path.exists(f + ".code2anno.json")]
print(len(games))
print(games)

code2anno_aliased = {g: [] for g in games}
anno2code_aliased = {g: [] for g in games}
obj_not_exist = {g: [] for g in games}

for g in games:
    code2anno_path = f"{data_path}/{g}/{g}.code2anno.json"
    anno2code_path = f"{data_path}/{g}/{g}.anno2code.json"
    # edit_anno2code_path = f"{data_path}/{g}/{g}.anno2code_edit.json"

    with open(code2anno_path, "r") as f:
        code2anno = json.load(f)
    with open(anno2code_path, "r") as f:
        anno2code = json.load(f)
    # with open(edit_anno2code_path, "w") as f:
    #     json.dump(anno2code, f, indent=4)

    # no alias means:
    # every entry in anno2code has a len 1 list
    # every entry in code2anno is a str

    for k in code2anno.keys():
        if not isinstance(code2anno[k], str):
            code2anno_aliased[g].append(k)
        if "(obj" not in k:
            obj_not_exist[g].append(k)

    for k in anno2code.keys():

        if len(anno2code[k]) > 1:
            anno2code_aliased[g].append(k)


# drop all non-aliased games from both dicts
# code2anno_aliased = {k: v for k, v in code2anno_aliased.items() if len(v) > 0}
# obj_not_exist = {k: v for k, v in obj_not_exist.items() if len(v) > 0}
# anno2code_aliased = {k: v for k, v in anno2code_aliased.items() if len(v) > 0}

# save the result to jsons
# with open("code2anno_aliased.json", "w") as f: # save to the folder containing this code
output_path = os.path.dirname(__file__)

with open(f"{output_path}/obj_not_exist.json", "w") as f:
    json.dump(obj_not_exist, f, indent=2)

with open(f"{output_path}/code2anno_aliased.json", "w") as f:
    json.dump(code2anno_aliased, f, indent=2)

with open(f"{output_path}/anno2code_aliased.json", "w") as f:
    json.dump(anno2code_aliased, f, indent=2)
