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
