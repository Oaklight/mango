import glob
from jericho import * # https://jericho-py.readthedocs.io/en/latest/index.html
import os
import argparse
from tqdm import tqdm
from jericho import *
from jericho.util import unabbreviate

direction_abbrv_dict = {'e': 'east', 'w': 'west', 'n': 'north', 's': 'south',
                        'ne': 'northeast', 'nw': 'northwest', 'se': 'southeast', 'sw': 'southwest',
                        'u': 'up', 'd': 'down'} # jericho.defines.ABBRV_DICT
direction_vocab_abbrv = direction_abbrv_dict.keys()
direction_vocab = direction_abbrv_dict.values()

def gen_move_machine(args):
    game_name = args.game_name
    max_steps = args.max_steps
    print ('Game: {}, Max steps: {}'.format(game_name, max_steps))

    # env
    # env = FrotzEnv("{}/{}".format(args.jericho_path, game_name))
    game_file_path = None
    for game_file in glob.glob(f"{args.jericho_path}/*"):
        if game_name == os.path.splitext(os.path.basename(game_file))[0]:
            game_file_path = game_file
            break
    if game_file_path is None:
        print(f"Game file {game_name} not found in {args.jericho_path}")
        return -1
    env = FrotzEnv(game_file_path)
    
    env.reset()
    location_before = env.get_player_location().name.strip().lower()
    location_before_id = env.get_player_location().num

    # walkthrough
    walkthrough_acts = env.get_walkthrough()

    map_list = []
    move_list = []
    for step_idx, act in enumerate(walkthrough_acts[:max_steps]):
        observation, reward, done, info = env.step(act)
        print(step_idx, env.get_player_location())
        try:
            location_after = env.get_player_location().name.strip().lower()
        except:
            print ('{}||{}||{}||{}||{}||{}'.format(step_idx, act, observation, reward, done, info))
            location_after = None
            # exit(0)

        location_after_id = env.get_player_location().num
        if location_after_id != location_before_id:
            map_list.append({
                'location_before': location_before,
                'location_before_id': location_before_id,
                'act': unabbreviate(act),
                'location_after': location_after,
                'location_after_id': location_after_id,
                'step_num': step_idx + 1
            })
            move_list.append(unabbreviate(act))

            location_before = location_after
            location_before_id = location_after_id

            # print(step_idx, unabbreviate(act), act)

    output_dir = args.output_dir + '/' + game_name.split('.')[0]
    if os.path.exists(output_dir) == False:
        os.makedirs(output_dir)

    if len(map_list) == 0:
        print ("No map generated!")
        return -1
    
    output_file = '{}/{}.map.machine'.format(output_dir,game_name.split('.')[0])
    with open(output_file,'w', encoding='utf-8') as fout:
        for item in map_list:
            fout.write('{} (obj{}) --> {} --> {} (obj{}), step {}\n'.format(item['location_before'],
                                                                            item['location_before_id'],
                                                                            item['act'],
                                                                            item['location_after'],
                                                                            item['location_after_id'],
                                                                            item['step_num']))
    print ("Saved to {}".format(output_file))

    output_file = '{}/{}.moves'.format(output_dir, game_name.split('.')[0])
    valid_moves = list(set(move_list).union(set(direction_vocab)))
    # sort valid_moves by str content
    valid_moves = sorted(valid_moves, key=lambda x: str(x))
    with open(output_file, 'w', encoding='utf-8') as fout:
        for sample in valid_moves :
            fout.write('{}\n'.format(sample))
    print ("Saved to {}".format(output_file))
    print ("Good Job!")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--game_name", '-g', type=str)
    parser.add_argument("--jericho_path", '-j', type=str, default="./data/z-machine-games-master/jericho-game-suite")
    parser.add_argument("--max_steps", type=int, default=70)
    parser.add_argument("--output_dir", '-odir', type=str, default="./data/maps")
    parser.add_argument("--walk_md", '-md', action='store_true', help='toggle to output walkthrough.md, otherwise output walkthrough.txt')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    print ("Args: {}".format(args))
    gen_move_machine(args)