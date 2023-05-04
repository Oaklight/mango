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

#
# from jericho import * # https://jericho-py.readthedocs.io/en/latest/index.html
# import os
# import argparse
# from tqdm import tqdm
# from jericho import *
#
# direction_abbrv_dict = {'e': 'east', 'w': 'west', 'n': 'north', 's': 'south',
#                         'ne': 'northeast', 'nw': 'northwest', 'se': 'southeast', 'sw': 'southwest',
#                         'u': 'up', 'd': 'down'} # jericho.defines.ABBRV_DICT
# direction_vocab_abbrv = direction_abbrv_dict.keys()
# direction_vocab = direction_abbrv_dict.values()
# opposite_direction_dict = {
#     'east': 'west',
#     'west': 'east',
#     'north': 'south',
#     'south': 'north',
#     'northeast': 'southwest',
#     'southwest': 'northeast',
#     'northwest': 'southeast',
#     'southeast': 'northwest',
#     'up': 'up',
#     'down': 'down'
# }
#
# def gen_move_machine(args):
#     game_name = args.game_name
#     max_steps = args.max_steps
#     print ('Game: {}, Max steps: {}'.format(game_name, max_steps))
#
#     # env
#     env = FrotzEnv("{}/{}".format(args.jericho_path, game_name))
#     env.reset()
#     location_before = env.get_player_location().name.strip().lower()
#     location_before_id = env.get_player_location().num
#
#     # walkthrough
#     walkthrough_raw = env.get_walkthrough()
#     abbrv_dict = jericho.defines.ABBRV_DICT
#     walkthrough = [abbrv_dict[item.lower()] if item.lower() in abbrv_dict else item.lower() for item in walkthrough_raw]
#
#     map_list = []
#     # map_reversed_list = []
#     move_list = []
#     for step_idx, act in enumerate(walkthrough[:max_steps]):
#         observation, reward, done, info = env.step(act)
#         location_after = env.get_player_location().name.strip().lower()
#         location_after_id = env.get_player_location().num
#         if location_after_id != location_before_id:
#             map_list.append({
#                 'location_before': location_before,
#                 'location_before_id': location_before_id,
#                 'act': act,
#                 'location_after': location_after,
#                 'location_after_id': location_after_id,
#                 'step_num': step_idx + 1
#             })
#             move_list.append(act)
#             # # reverse
#             # valid_actions = env.get_valid_actions()
#             # if act in direction_vocab:
#             #     if opposite_direction_dict[act] in valid_actions:
#             #         desc = 'None'
#             #     else:
#             #         obsrv_splitted = observation.split('\n')
#             #         if len(obsrv_splitted) == 1:
#             #             desc = obsrv_splitted[0]
#             #         else:
#             #             desc = '{} || {}'.format(obsrv_splitted[0], "".join(obsrv_splitted[1:]))
#             #
#             #     map_reversed_list.append({
#             #         'location_before': location_after,
#             #         'location_before_id': location_after_id,
#             #         'act': opposite_direction_dict[act],
#             #         'location_after': location_before,
#             #         'location_after_id': location_before_id,
#             #         'step_num': step_idx + 1,
#             #         'desc': desc
#             #     }
#             #     )
#             # else:
#             #     map_reversed_list.append({
#             #         'location_before': None,
#             #         'location_before_id': None,
#             #         'act': None,
#             #         'location_after': None,
#             #         'location_after_id': None,
#             #         'step_num': None,
#             #         'desc': None
#             #     }
#             #     )
#
#             location_before = location_after
#             location_before_id = location_after_id
#
#     output_dir = args.output_dir + '/' + game_name.split('.')[0]
#     if os.path.exists(output_dir) == False:
#         os.makedirs(output_dir)
#
#     output_file = '{}/{}.map.machine'.format(output_dir,game_name.split('.')[0])
#     with open(output_file,'w', encoding='utf-8') as fout:
#         for item in map_list:
#             fout.write('{} (obj{}) --> {} --> {} (obj{}), step {}\n'.format(item['location_before'],
#                                                                             item['location_before_id'],
#                                                                             item['act'],
#                                                                             item['location_after'],
#                                                                             item['location_after_id'],
#                                                                             item['step_num']))
#     print ("Saved to {}".format(output_file))
#
#     outfile = '{}/{}.walkthrough.moves.{}'.format(output_dir, game_name.split('.')[0], max_steps)
#     with open(outfile, 'w', encoding='utf-8') as fout:
#         for sample in set(move_list).union(set(direction_vocab)) :
#             fout.write('{}\n'.format(sample))
#
#     # output_file = '{}/{}.map.machine.reversed'.format(args.output_dir, game_name.split('.')[0])
#     # with open(output_file,'w', encoding='utf-8') as fout:
#     #     for item in map_reversed_list:
#     #         if item['act'] != None:
#     #             fout.write('{} (obj{}) --> {} --> {} (obj{}), step {}, desc: {}\n'.format(item['location_before'],
#     #                                                                                       item['location_before_id'],
#     #                                                                                       item['act'],
#     #                                                                                       item['location_after'],
#     #                                                                                       item['location_after_id'],
#     #                                                                                       item['step_num'],
#     #                                                                                       item['desc']))
#     #         else:
#     #             fout.write('\n')
#
#     print ("Saved to {}".format(output_file))
#     print ("Good Job!")
#
#
# def parse_args():
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--game_name", '-g', type=str)
#     parser.add_argument("--jericho_path", '-j', type=str, default="./data/z-machine-games-master/jericho-game-suite")
#     parser.add_argument("--max_steps", type=int, default=70)
#     parser.add_argument("--output_dir", '-odir', type=str, default="./data/maps")
#     parser.add_argument("--walk_md", '-md', action='store_true', help='toggle to output walkthrough.md, otherwise output walkthrough.txt')
#     return parser.parse_args()
#
# if __name__ == '__main__':
#     args = parse_args()
#     print ("Args: {}".format(args))
#     gen_move_machine(args)
