import os

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

    all2all_path = f"{data_path}/{g}/{g}.all2all.json"
    all_pairs_path = f"{data_path}/{g}/{g}.all_pairs.json"
    walkthrough_path = f"{data_path}/{g}/{g}.walkthrough"
    edges_path = f"{data_path}/{g}/{g}.edges.json"
    nodes_path = f"{data_path}/{g}/{g}.nodes.json"

    edit_all2all_path = f"{data_path}/{g}/{g}.all2all_edit.json"
    edit_all_pairs_path = f"{data_path}/{g}/{g}.all_pairs_edit.json"
    edit_edges_path = f"{data_path}/{g}/{g}.edges_edit.json"
    edit_nodes_path = f"{data_path}/{g}/{g}.nodes_edit.json"
    edit_walkthrough_path = f"{data_path}/{g}/{g}.walkthrough_edit"

    # check all files above exist, both original and edit_*, skip g if edit is missing
    if (
        not os.path.exists(all2all_path)
        or not os.path.exists(all_pairs_path)
        or not os.path.exists(walkthrough_path)
        or not os.path.exists(edges_path)
        or not os.path.exists(nodes_path)
        or not os.path.exists(edit_all2all_path)
        or not os.path.exists(edit_all_pairs_path)
        or not os.path.exists(edit_edges_path)
        or not os.path.exists(edit_nodes_path)
        or not os.path.exists(edit_walkthrough_path)
    ):
        print(f"Missing edit version of {g}")
        continue

    # mv edit_ to original name
    os.rename(edit_all2all_path, all2all_path)
    os.rename(edit_all_pairs_path, all_pairs_path)
    os.rename(edit_walkthrough_path, walkthrough_path)
    os.rename(edit_edges_path, edges_path)
    os.rename(edit_nodes_path, nodes_path)
