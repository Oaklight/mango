# garbage code
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
