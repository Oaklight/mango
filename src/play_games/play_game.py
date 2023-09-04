"""
# https://jericho-py.readthedocs.io/en/latest/index.html
"""

import os
import time
import argparse
import json
from tqdm import tqdm
from collections import defaultdict

from jericho import *
from src.play_games.api import api_complete


direction_list = ['east', 'west', 'north', 'south', 'northeast', 'northwest', 'southeast', 'up', 'down']
opposite_direction_dict = {
    'east': 'west',
    'west': 'east',
    'north': 'south',
    'south': 'north',
    'northeast': 'southwest',
    'southwest': 'northeast',
    'northwest': 'southeast',
    'southeast': 'northwest',
    'up': 'up',
    'down': 'down'
}


def play_game(args):
    model_name = args.model_name
    game_name = args.game_name
    max_steps = args.max_steps
    env = FrotzEnv("{}/{}".format(args.jericho_path, game_name))

    map_adjacent_dict = defaultdict(dict)
    system_prompt = "Your task is to play an interactive fiction game. Please try to get as many points as possible."
    history_steps = ""
    reward = 0
    observation, info = env.reset()
    act_info = {
        'valid_actions': ['Init'],
        'act': 'Init',
        'observation': observation,
        'reward': reward,
        'done': False,
        'info': info,
        'prompt': ''
    }
    walkthrough_list = []
    walkthrough_list.append(act_info)
    location_tmp = 'Init'

    for step_num in range(max_steps):
        print ("==> step num: ", step_num)
        valid_actions = env.get_valid_actions()
        current_map = ''
        if args.aug_map:
            if location_tmp in map_adjacent_dict:
                current_map = '\n- extra info: ' # '\n- hints: '
                current_map_dict = map_adjacent_dict[location_tmp]
                for direction in current_map_dict:
                    current_map += 'If you go {}, you will get to "{}";'.format(direction, current_map_dict[direction])

        prompt = '- history: {}\n- new observation: {}{}\n- valid actions: {}\nPlease select an action from the valid actions list. Please just tell me the selected action without any extra words.'.format(history_steps, observation, current_map, valid_actions)
        try:
            act = api_complete(system_prompt=system_prompt, prompt = prompt, model=model_name).strip().strip('"').strip("'")
        except Exception as e:
            print ("exception: ", e)
            break
        history_steps += '\nobservation: {}\nselected action: "{}"\nreward: {}\n'.format(observation, act, reward)
        observation, reward, done, info = env.step(act)
        if args.aug_map and act in set(direction_list):
            location_new = observation.strip().split('\n')[0].strip()  # ??
            map_adjacent_dict[location_tmp][act] = location_new
            map_adjacent_dict[location_new][opposite_direction_dict[act]] = location_tmp
            location_tmp = location_new

        sample_info = {
            'valid_actions': valid_actions,
            'act': act,
            'observation': observation,
            'reward': reward,
            'done': done,
            'info': info,
            'prompt': prompt
        }
        walkthrough_list.append(sample_info)
        print (sample_info)
        if done:
            break
    
    cache_dir = os.path.join(args.cache_dir, game_name.split('.')[0])
    if os.path.exists(cache_dir) == False:
        os.makedirs(cache_dir)

    aug_map = ''
    if args.aug_map:
        aug_map = 'aug_map'
    outfile = '{}/{}_{}_walkthrough.json'.format(cache_dir, model_name, aug_map)
    with open(outfile, 'w+', encoding='utf-8') as fout:
        fout.write(json.dumps(walkthrough_list, indent=4))
    print ('Well Done!')

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", '-m', type=str, default="gpt-3.5-turbo")
    parser.add_argument("--game_name", '-g', type=str, default="zork1")
    parser.add_argument("--jericho_path", '-j', type=str, default="./z-machine-games-master/jericho-game-suite")
    parser.add_argument("--aug_map", action='store_true')
    parser.add_argument("--cache_dir", '-cdir', type=str, default="./data/maps")
    parser.add_argument("--max_steps", type=int, default=120)
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    print ("Args: {}".format(args))
    play_game(args)