"""
# https://jericho-py.readthedocs.io/en/latest/index.html
"""

import re
import os
import time
import datetime
import argparse
import json
from tqdm import tqdm
from collections import defaultdict
from tqdm import tqdm


from jericho import *
from src.play_games.api import api_complete
from jericho.util import unabbreviate

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


def format_walkthrough(walkthrough_list):
    walkthrough = ''
    for wt in walkthrough_list:
        walkthrough += '- selected action: {}\n- observation: {}\n- reward: {}'.format(wt['act'], wt['observation'], wt['reward'])
    return walkthrough

def gen_eval_data(jericho_path, game_name, max_steps):
    eval_data = []
    env = FrotzEnv("{}/{}".format(jericho_path, game_name))

    walkthrough_acts = env.get_walkthrough()
    initial_observation, info = env.reset()
    valid_actions = env.get_valid_actions()

    step_num = 0
    act_info = {
        'step': step_num,
        'act': 'Init',
        'valid_actions': valid_actions,
        'observation': initial_observation.strip(),
        'reward': 0,
        'info': info,
        'done': False
    }

    walkthrough_list = []
    walkthrough_list.append(act_info)

    map = defaultdict(dict)
    last_location = 'Init'
    transition_steps = 0
    revisited_steps = 0
    for act in tqdm(walkthrough_acts[:max_steps]):
        step_num += 1
        observation, reward, done, info = env.step(act)
        valid_actions = env.get_valid_actions()

        action = unabbreviate(act)
        sample_info = {
            'step': step_num,
            'act': action,
            'valid_actions': valid_actions,
            'observation': observation.strip(),
            'reward': reward,
            'info': info,
            'done': done
        }

        if action in set(direction_list):
            location = observation.strip().split('\n')[0]
            if location != last_location:
                transition_steps += 1  
                if len(map) == 0:
                    map[last_location] = {
                        location: action
                    }
                    map[location] = {
                        last_location: opposite_direction_dict[action]
                    }
                elif location not in map:
                    map[last_location][location] = action
                    map[location] = {
                        last_location: opposite_direction_dict[action]
                    }
                elif location not in map[last_location] or map[last_location][location] != action:
                    map[last_location][location] = action
                    map[location][last_location] = opposite_direction_dict[action]
                elif map[last_location][location] == action: # revisit
                    revisited_steps += 1
                    eval_data.append({'history': format_walkthrough(walkthrough_list), 'valid actions': valid_actions, 'location': last_location, 'map': map[last_location], 'golden_action': action})
                last_location = location
        walkthrough_list.append(sample_info)
    return eval_data


def format_map(map_dict):
    current_map = '\n- extra info: '
    for key in map_dict:
        current_map += 'If you want to go to "{}", you should go {} ;'.format(key, map_dict[key])
    return current_map

prompt_base = """- history: {}\n{}\nConsider where you should go next, and choose one appropriate action from the valid actions list: {}\nPlease just tell me the selected action without any extra words."""

def play_game(args):
    model_name = args.model_name
    game_name = args.game_name
    max_steps = args.max_steps
    eval_data = gen_eval_data(args.jericho_path, game_name, max_steps)
    print ("loaded {} items.".format(len(eval_data)))

    cache_dir = os.path.join(args.cache_dir, game_name.split('.')[0])
    if os.path.exists(cache_dir) == False:
        os.makedirs(cache_dir)

    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    outfile = '{}/{}_cache_{}.json'.format(cache_dir, model_name, formatted_datetime)

    system_prompt = "Your task is to play an interactive fiction game."
    without_map_acc = 0
    with_map_acc = 0
    eval_num = 0
    for eval_item in eval_data:
        current_map = format_map(eval_item['map'])
        prompt_with_map = prompt_base.format(eval_item['history'], current_map, eval_item['valid actions'])
        response = api_complete(system_prompt=system_prompt, prompt = prompt_with_map, model=model_name)
        if response == 'Invalid Request.':
            print (response)
            break
        selected_act_with_map = response.strip().strip('"').strip("'")
        eval_item['prompt_with_map'] = prompt_with_map
        eval_item['selected_act_with_map'] = selected_act_with_map

        prompt_without_map = prompt_base.format(eval_item['history'], 'You should think about where you are now.', eval_item['valid actions'])
        response = api_complete(system_prompt=system_prompt, prompt = prompt_without_map, model=model_name)
        if response == 'Invalid Request.':
            print (response)
            break
        selected_act_without_map = response.strip().strip('"').strip("'")
        eval_item['prompt_without_map'] = prompt_without_map
        eval_item['selected_act_without_map'] = selected_act_without_map

        if selected_act_with_map == eval_item['golden_action']:
            eval_item['acc_with_map'] = True
            with_map_acc += 1
        else:
            eval_item['acc_with_map'] = False

        if selected_act_without_map == eval_item['golden_action']:
            eval_item['acc_without_map'] = True
            without_map_acc += 1
        else:
            eval_item['acc_without_map'] = False

        print ("acc without map: {}; acc with map: {}".format(eval_item['acc_without_map'], eval_item['acc_with_map']))
        print ("save to cache file: {}".format(outfile))
        with open(outfile, 'a+', encoding='utf-8') as fout:
            fout.write(json.dumps(eval_item, indent=4))
            fout.write('\n')
        eval_num +=1 

    print ("without map acc: {}/{}".format(without_map_acc, eval_num))
    print ("with map acc: {}/{}".format(with_map_acc, eval_num))
    print ('Well Done!')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", '-m', type=str, default="gpt-3.5-turbo")
    parser.add_argument("--game_name", '-g', type=str, default="zork1")
    parser.add_argument("--jericho_path", '-j', type=str, default="./z-machine-games-master/jericho-game-suite")
    parser.add_argument("--cache_dir", '-cdir', type=str, default="./data/maps")
    parser.add_argument("--max_steps", type=int, default=70)
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    print ("Args: {}".format(args))
    play_game(args)