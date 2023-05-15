## read in game.map.human and game.map.machine
# go over each line in game.map.machine, grab nodeCode and find the corresponding node name in game.map.human
import argparse
import json
import os


# helper function to get such dict
def get_dict(lines):
    """
    example of machine and human lines
    machine: west house (obj180) --> north --> north house (obj81), step 1
    human: west of house --> north --> north of house, step 1
    matching lines must have the same step number
    """
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


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--game_data_dir",
        "-d",
        type=str,
        help="path to game data dir containing game.map.machine and game.map.human",
        required=True,
    )

    args = parser.parse_args()
    args.output_path = args.game_data_dir
    print("game data dir: {}".format(args.game_data_dir))

    # game name in this case is the name of the last layer folder
    args.game_name = args.game_data_dir.split("/")[-1]
    # machine_code and human_anno are in the game data dir
    args.machine_code = os.path.join(
        args.game_data_dir, f"{args.game_name}.map.machine"
    )
    args.human_anno = os.path.join(args.game_data_dir, f"{args.game_name}.map.human")
    args.walkthrough = os.path.join(args.game_data_dir, f"{args.game_name}.walkthrough")

    # check if both machine_code and human_anno exist
    if not os.path.exists(args.machine_code):
        raise ValueError(f"{args.machine_code} does not exist")
    if not os.path.exists(args.human_anno):
        raise ValueError(f"{args.human_anno} does not exist")

    return args


def sanity_check(machine_dict, human_dict, walkthrough_file):
    """
    compare machine_dict with human_dict
    - get common step numbers, appear in both machine and human
    - get diff step numbers, appear in machine but not human
    - get diff step numbers, appear in human but not machine
    """
    common_steps = set(machine_dict.keys()).intersection(set(human_dict.keys()))
    machine_only_steps = set(machine_dict.keys()).difference(set(human_dict.keys()))
    human_only_steps = set(human_dict.keys()).difference(set(machine_dict.keys()))
    # print to notify user
    print(
        "common steps: {}, machine only steps: {}, human only steps: {}".format(
            len(common_steps), len(machine_only_steps), len(human_only_steps)
        )
    )
    print("machine only steps: {}".format(machine_only_steps))
    print("human only steps: {}".format(human_only_steps))
    # wait for signal, Y/n, Y as default, check to see if user wants to continue
    # if not, exit
    # if yes, continue
    while len(machine_only_steps) > 0 or len(human_only_steps) > 0:
        signal = input("Continue? [y/n] ").strip()
        if signal == "n":
            print("Please manually review difference\n")
            exit()
        if signal == "y":
            return


def load_both_maps(get_dict, args):
    with open(args.machine_code, "r") as f:
        machine_lines = f.readlines()
    with open(args.human_anno, "r") as f:
        human_lines = f.readlines()

    # create a dict of machine/human line number to {src, dst, action}
    machine_dict = get_dict(machine_lines)
    human_dict = get_dict(human_lines)
    return machine_dict, human_dict


if __name__ == "__main__":
    args = get_args()

    print("Processing {}...".format(args.game_name))
    # read in game.map.human and game.map.machine
    # go over each line in game.map.machine, grab nodeCode and find the corresponding node name in game.map.human
    machine_dict, human_dict = load_both_maps(get_dict, args)

    sanity_check(machine_dict, human_dict, args.walkthrough)
    print("Reload both maps after resolution")
    machine_dict, human_dict = load_both_maps(get_dict, args)

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
        # sort anno2code entry
        anno2code[anno].sort()
        
    # write to json file
    with open(
        os.path.join(args.output_path, f"{args.game_name}.code2anno.json"), "w"
    ) as f:
        json.dump(code2anno, f, indent=4)
    with open(
        os.path.join(args.output_path, f"{args.game_name}.anno2code.json"), "w"
    ) as f:
        json.dump(anno2code, f, indent=4)

    print("Done processing!\n")