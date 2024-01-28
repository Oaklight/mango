## read in game.map.human and game.map.machine
# go over each line in game.map.machine, grab nodeCode and find the corresponding node name in game.map.human
import argparse
import json
import os
from collections import OrderedDict


# helper function to get such dict
def get_dict(lines, cutoff=None):
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
        if cutoff is not None and step > cutoff:
            continue
        elements = path_str.split("-->")
        src = elements[0].strip()
        act = elements[1].strip()
        dst = elements[2].strip()
        d[step] = {"src": src, "dst": dst, "act": act}
    return d


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--game_data_dir",
        "-d",
        type=str,
        help="path to game data dir containing game.map.machine and game.map.human",
        required=True,
    )
    parser.add_argument(
        "--max_step",
        "-s",
        type=int,
        default=70,
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


def sanity_check(machine_dict, human_dict):
    """
    compare machine_dict with human_dict
    - get common step numbers, appear in both machine and human
    - get diff step numbers, appear in machine but not human
    - get diff step numbers, appear in human but not machine
    - get diff in src, act, dst when step number is the same, namely on common steps
    """
    # sort step number list for stable order
    common_steps = sorted(
        list(set(machine_dict.keys()).intersection(set(human_dict.keys())))
    )
    machine_only_steps = sorted(
        list(set(machine_dict.keys()).difference(set(human_dict.keys())))
    )
    human_only_steps = sorted(
        list(set(human_dict.keys()).difference(set(machine_dict.keys())))
    )

    # further sanity check on common steps, to see if src, act, dst are the same
    conflict_anno_dict = node_conflict_check(machine_dict, human_dict, common_steps)

    # print to notify user
    print(
        "General Stats:",
        "- [num: {}] common steps".format(len(common_steps)),
        "- [num: {}] machine only steps: {}".format(
            len(machine_only_steps), machine_only_steps
        ),
        "- [num: {}] human only steps: {}".format(
            len(human_only_steps), human_only_steps
        ),
        "- [num: {}] conflict annotations on common steps: \n\t{}".format(
            len(conflict_anno_dict),
            "\n\t".join(
                [str(k) + ": " + str(v) for k, v in conflict_anno_dict.items()]
            ),
        ),
        sep="\n",
    )
    # wait for signal, Y/n, Y as default, check to see if user wants to continue
    # if not, exit
    # if yes, continue
    # return step sets for further processing
    if (
        len(machine_only_steps) == 0
        and len(human_only_steps) == 0
        and len(conflict_anno_dict) == 0
    ):
        print("No difference found, exiting...")
        return common_steps, machine_only_steps, human_only_steps
    else:
        while True:
            signal = input("Continue? [y/n] ").strip()
            if signal == "n":
                print("Please manually review difference\n")
                exit()
            elif signal == "y":
                return (
                    common_steps,
                    machine_only_steps,
                    human_only_steps,
                )
            else:
                print("Invalid input, please enter y or n")


def node_conflict_check(machine_dict, human_dict, common_steps):
    """
    In machine dict, nodes with same code ARE the same location. After conflict resolve, it must be able to achieve the same human annotation content for the same machine code in matching steps
    """

    def __conflict_counter(which: str):
        code = machine_dict[step][which]
        anno = human_dict[step][which]
        if code not in code2anno_tmp:
            code2anno_tmp[code] = set()
        code2anno_tmp[code].add(anno)
        if anno not in anno_step_map:
            anno_step_map[anno] = set()
        anno_step_map[anno].add((step, which))
        if code not in code_step_map:
            code_step_map[code] = set()
        code_step_map[code].add((step, which))

    # create mapping of human anno with machine code at each step. check if machine code exist already. If not, add it to the mapping. if exist but different, put into conflict list
    conflict_anno_dict = {}  # conflict list, from code (unique) to anno (list)
    code2anno_tmp = {}  # tmp mapping of code to anno, for tracking and debugging
    anno_step_map = {}  # where each anno appears
    code_step_map = {}  # where each code appears
    for step in common_steps:
        # check src & dst
        __conflict_counter("src")
        __conflict_counter("dst")

    for code in code2anno_tmp:
        if len(code2anno_tmp[code]) > 1:
            conflict_anno_dict[code] = list(code2anno_tmp[code])
            # collect where each conflicted anno appears, by replacing anno with tuple of (anno, [step_num])
            conflict_anno_dict[code] = [
                (
                    anno,
                    sorted(list(anno_step_map[anno].intersection(code_step_map[code]))),
                )
                for anno in conflict_anno_dict[code]
            ]

    return conflict_anno_dict


def load_both_maps(args):
    with open(args.machine_code, "r") as f:
        machine_lines = f.readlines()
    with open(args.human_anno, "r") as f:
        human_lines = f.readlines()

    if args.max_step == -1:
        _, step_str = human_lines[-1].split(", step ")
        args.max_step = int(step_str)
    # create a dict of machine/human line number to {src, dst, action}
    machine_dict = get_dict(machine_lines, cutoff=args.max_step)
    human_dict = get_dict(human_lines, cutoff=args.max_step)
    return machine_dict, human_dict


def add_anno2code(anno2code: dict, code: str, anno: str):
    # anno2code[anno] = {code, ...}
    if anno not in anno2code:
        anno2code[anno] = set([code])
    else:
        anno2code[anno].add(code)

    return anno2code


def add_code2anno(
    code2anno: OrderedDict, step_num: int, code: str, anno: str, position: str
):
    # code2anno[code] = {
    #   'anno': [(step_num, position), ...]
    # }
    # print(type(code2anno), type(code), type(code2anno[code]))
    entry = (step_num, position)
    if code not in code2anno:
        code2anno[code] = {anno: set([entry])}
    else:
        if anno not in code2anno[code]:
            code2anno[code][anno] = set([entry])
        else:
            code2anno[code][anno].add(entry)

    return code2anno


if __name__ == "__main__":
    args = parse_args()

    print("Processing {}...".format(args.game_name))
    # read in game.map.human and game.map.machine
    # go over each line in game.map.machine, grab nodeCode and find the corresponding node name in game.map.human
    machine_dict, human_dict = load_both_maps(args)

    (
        common_steps,
        machine_only_steps,
        human_only_steps,
    ) = sanity_check(machine_dict, human_dict)
    print("Reload both maps after resolution")
    machine_dict, human_dict = load_both_maps(args)

    code2anno = OrderedDict()
    anno2code = OrderedDict()

    """
    assumption: human annotation is a connected graph, each line is a edge. Thus, the end node of current line must be the start node of next line. I only need to check matching of end node of each line. and start node of the first line.
    """
    # first process the common_steps, which are the same in both machine and human
    print("processing common steps...")
    for step_num in common_steps:
        dst_code = machine_dict[step_num]["dst"]
        dst_anno = human_dict[step_num]["dst"]
        code2anno = add_code2anno(code2anno, step_num, dst_code, dst_anno, "dst")
        anno2code = add_anno2code(anno2code, dst_code, dst_anno)

        # src_code also needs to be checked in every time, in case of disconnection in machine code.
        src_code = machine_dict[step_num]["src"]
        src_anno = human_dict[step_num]["src"]
        code2anno = add_code2anno(code2anno, step_num, src_code, src_anno, "src")
        anno2code = add_anno2code(anno2code, src_code, src_anno)

    # then process the human_only_steps, which are annotated by human but not machine
    print("processing human only steps...")
    for step_num in human_only_steps:
        # since there is no matching machine code, we can only see if there was a previous step
        src_anno = human_dict[step_num]["src"]
        dst_anno = human_dict[step_num]["dst"]

        if src_anno not in anno2code:
            prompt = f"Please enter the code for {src_anno} (no previous step): "
            src_code = input(prompt).strip()
            code2anno = add_code2anno(code2anno, step_num, src_code, src_anno, "src")
            anno2code = add_anno2code(anno2code, src_code, src_anno)

        if dst_anno not in anno2code:
            prompt = f"Please enter the code for {dst_anno} (no previous step): "
            dst_code = input(prompt).strip()
            code2anno = add_code2anno(code2anno, step_num, dst_code, dst_anno, "dst")
            anno2code = add_anno2code(anno2code, dst_code, dst_anno)

    # cast anno2code entry from set to list and sort it
    for anno in anno2code.keys():
        anno2code[anno] = sorted(list(anno2code[anno]))

    # cast code2anno entry step number to list
    for code in code2anno.keys():
        codemap = code2anno[code]
        if len(codemap) == 1:  # meaning no human anno alias
            codemap = list(codemap.keys())[0]
        else:
            for anno in codemap.keys():
                codemap[anno] = sorted(list(codemap[anno]))
        code2anno[code] = codemap

    # prompt to alert unusual cases
    # multiple machine code map to the same human anno
    for anno in anno2code.keys():
        if len(anno2code[anno]) > 1:
            for code in anno2code[anno]:
                print(
                    f"Warning: human anno [{anno}] map to different machine code [{code}]"
                )

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
