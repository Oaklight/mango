## read in game.map.human and game.map.machine
# go over each line in game.map.machine, grab nodeCode and find the corresponding node name in game.map.human
import argparse
import json


# helper function to get such dict
def get_dict(lines):
    d = {}
    for line in lines:
        line = line.strip()
        if len(line) == 0:
            continue
        path_str, step_str = line.split(", step ")
        step = int(step_str)
        elements = path_str.split(" --> ")
        src = elements[0]
        act = elements[1]
        dst = elements[2]
        d[step] = {"src": src, "dst": dst, "act": act}
    return d


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--machine_code",
        "-c",
        type=str,
        default="../data/zork1.map.machine",
        help="path to game.map.machine file",
    )
    parser.add_argument(
        "--human_anno",
        "-a",
        type=str,
        default="../data/zork1.map.human",
        help="path to game.map.human file",
    )
    args = parser.parse_args()
    args.game_name = args.machine_code.split("/")[-1].split(".")[0]
    # output_path the same as machine path, but with .code2anno.json and .anno2code.json
    args.output_path = args.machine_code.replace(".map.machine", "")

    # read in game.map.human and game.map.machine
    # go over each line in game.map.machine, grab nodeCode and find the corresponding node name in game.map.human
    with open(args.machine_code, "r") as f:
        machine_lines = f.readlines()
    with open(args.human_anno, "r") as f:
        human_lines = f.readlines()

    # example of machine and human lines
    # machine: west house (obj180) --> north --> north house (obj81), step 1
    # human: west of house --> north --> north of house, step 1
    # matching lines must have the same step number

    # create a dict of machine line number to {src, dst, action}
    machine_dict = get_dict(machine_lines)
    # create a dict of human line number to {src, dst, action}
    human_dict = get_dict(human_lines)

    code2anno = {}
    anno2code = {}
    # iter over machine dict, find the corresponding human line
    for step_num in machine_dict.keys():
        src_code = machine_dict[step_num]["src"]
        dst_code = machine_dict[step_num]["dst"]
        src_anno = human_dict[step_num]["src"]
        dst_anno = human_dict[step_num]["dst"]

        code2anno[src_code] = src_anno
        code2anno[dst_code] = dst_anno

        if src_anno not in anno2code:
            anno2code[src_anno] = set([src_code])
        else:
            anno2code[src_anno].add(src_code)
        if dst_anno not in anno2code:
            anno2code[dst_anno] = set([dst_code])
        else:
            anno2code[dst_anno].add(dst_code)

    # cast anno2code entry from set to list
    for anno in anno2code.keys():
        anno2code[anno] = list(anno2code[anno])

    # write to json file
    with open(args.output_path + ".code2anno.json", "w") as f:
        json.dump(code2anno, f, indent=4)
    with open(args.output_path + ".anno2code.json", "w") as f:
        json.dump(anno2code, f, indent=4)
