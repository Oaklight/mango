import json
import os, sys
import subprocess

from tqdm import tqdm

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from gen_moves.gen_move_human import read_csv

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


def anno2code(anno, map_dict):
    anno = anno.lower()
    if anno in map_dict:
        return map_dict[anno][0]
    else:
        raise ValueError(f"Annotation {anno} not found")


class StreamEditor:
    def __init__(self, in_path, out_path):
        self.path_in = in_path
        self.path_out = out_path
        self.file_in = open(in_path, "r")
        self.file_out = open(out_path, "w")

    def edit(self, process_fn):
        # read file_in one line at a time,
        # apply process_fn to line
        # write the processed line to file_out
        for line in tqdm(self.file_in, total=self.count_lines_with_wc(self.path_in)):
            line_processed = process_fn(line)
            self.file_out.write(line_processed)
            self.file_out.write("\n")  # add newline
            self.file_out.flush()

    def count_lines_with_wc(self, file_path):
        result = subprocess.run(["wc", "-l", file_path], stdout=subprocess.PIPE)
        return int(result.stdout.decode("utf-8").split()[0])

    def close(self):
        self.file_in.close()
        self.file_out.close()


for g in games:

    all2all_path = f"{data_path}/{g}/{g}.all2all.json"
    all_pairs_path = f"{data_path}/{g}/{g}.all_pairs.json"
    walkthrough_path = f"{data_path}/{g}/{g}.walkthrough"
    edges_path = f"{data_path}/{g}/{g}.edges.json"
    nodes_path = f"{data_path}/{g}/{g}.nodes.json"

    valid_move_path = f"{data_path}/{g}/{g}.valid_moves.csv"
    anno2code_path = (
        f"{data_path}/{g}/{g}.anno2code_edit.json"  # use the manually cleaned version
    )

    with open(anno2code_path, "r") as f:
        anno2code_dict = json.load(f)
    # lower all keys in map_dict, via a copy
    anno2code_dict = {k.lower(): v for k, v in anno2code_dict.items()}

    valid_moves = read_csv(valid_move_path, -1)
    # find first valid_move
    for k, v in valid_moves.items():
        if v["valid_move"] == True:
            break
    start_whereabout_anno = v["src_node"]
    print(g, len(valid_moves), start_whereabout_anno)

    # ============== insert codename into walkthrough ==============
    print(f"Writing to {walkthrough_path}......")

    with open(walkthrough_path, "r") as f:
        walkthrough_lines = f.readlines()

    edit_walkthrough_lines = []
    for line in walkthrough_lines:
        # print(line)
        if line.startswith("==>STEP NUM:"):
            step_num = line.split(":")[1].strip()
            # print(step_num)
        if line.startswith("==>OBSERVATION:"):
            if step_num == "0":
                whereabout_anno = start_whereabout_anno
                whereabout_code = anno2code(whereabout_anno, anno2code_dict)
                line = line.replace(
                    "==>OBSERVATION:", f"==>OBSERVATION: [{whereabout_code}] "
                )
            elif valid_moves[step_num]["valid_move"] == True:
                whereabout_anno = valid_moves[step_num]["dst_node"]
                whereabout_code = anno2code(whereabout_anno, anno2code_dict)
                line = line.replace(
                    "==>OBSERVATION:", f"==>OBSERVATION: [{whereabout_code}] "
                )
        edit_walkthrough_lines.append(line)

    edit_walkthrough_path = f"{data_path}/{g}/{g}.walkthrough_edit"
    with open(edit_walkthrough_path, "w") as f:
        f.writelines(edit_walkthrough_lines)
        print(f"Wrote to {edit_walkthrough_path}")

    # ============== replace name in nodes ==============
    print(f"Writing to {nodes_path}......")

    with open(nodes_path, "r") as f:
        nodes = json.load(f)
    edit_node = []
    for n_anno in nodes:
        n_code = anno2code(n_anno, anno2code_dict)
        edit_node.append(n_code)
    edit_node_path = f"{data_path}/{g}/{g}.nodes_edit.json"
    with open(edit_node_path, "w") as f:
        json.dump(edit_node, f, indent=4)
        print(f"Wrote to {edit_node_path}")

    # ============== replace name in edges ==============
    print(f"Writing to {edges_path}......")

    with open(edges_path, "r") as f:
        edges = json.load(f)
    edit_edges = []
    for each in edges:
        each_copy = each.copy()

        src_code = anno2code(each["src_node"], anno2code_dict)
        dst_code = anno2code(each["dst_node"], anno2code_dict)
        each_copy["src_node"] = src_code
        each_copy["dst_node"] = dst_code

        edit_edges.append(each_copy)
    edit_edge_path = f"{data_path}/{g}/{g}.edges_edit.json"
    with open(edit_edge_path, "w") as f:
        json.dump(edit_edges, f, indent=4)
        print(f"Wrote to {edit_edge_path}")

    # ============== replace name in all2all ==============
    print(f"Writing to {all2all_path}......")

    def process_all2all_line(line):
        entry = json.loads(line)

        entry_copy = entry.copy()

        src_code = anno2code(entry["src_node"], anno2code_dict)
        dst_code = anno2code(entry["dst_node"], anno2code_dict)
        entry_copy["src_node"] = src_code
        entry_copy["dst_node"] = dst_code

        path_detail_copy = []
        for edge in entry["path_details"]:
            edge_src_code = anno2code(edge["prev_node"], anno2code_dict)
            edge_dst_code = anno2code(edge["node"], anno2code_dict)
            edge["prev_node"] = edge_src_code
            edge["node"] = edge_dst_code
            path_detail_copy.append(edge)
        entry_copy["path_details"] = path_detail_copy

        return json.dumps(entry_copy)

    all2all_editor = StreamEditor(
        all2all_path, f"{data_path}/{g}/{g}.all2all_edit.json"
    )
    all2all_editor.edit(process_all2all_line)
    all2all_editor.close()

    # ============== replace name in all_pairs ==============
    print(f"Writing to {all_pairs_path}......")

    def process_all_pairs_line(line):
        entry = json.loads(line)

        entry_copy = entry.copy()

        src_code = anno2code(entry["src_node"], anno2code_dict)
        dst_code = anno2code(entry["dst_node"], anno2code_dict)
        entry_copy["src_node"] = src_code
        entry_copy["dst_node"] = dst_code

        return json.dumps(entry_copy)

    all_pairs_editor = StreamEditor(
        all_pairs_path, f"{data_path}/{g}/{g}.all_pairs_edit.json"
    )
    all_pairs_editor.edit(process_all_pairs_line)
    all_pairs_editor.close()

    # break
