"""
# https://jericho-py.readthedocs.io/en/latest/index.html
"""

import os
import argparse
import json
from tqdm import tqdm

from jericho import *
from src.play_games.api import api_complete

def play_game(args):
    model_name = args.model_name
    game_name = args.game_name
    max_steps = args.max_steps
    env = FrotzEnv("{}/{}".format(args.jericho_path, game_name))

    system_prompt = "Your task is to play an interactive fiction game. Please try to get as many points as possible."
    history_steps = ""
    reward = 0
    observation, info = env.reset()
    act_info = {
        'act': 'Init',
        'observation': observation,
        'reward': reward,
        'done': False,
        'info': info
    }
    walkthrough_list = []
    walkthrough_list.append(act_info)

    for step_num in range(max_steps):
        valid_actions = env.get_valid_actions()
        prompt = '- history: {}\n- new observation: {}\n- valid actions: {}\nPlease select an action from the valid actions list. Please just tell me the selected action without any extra words.'.format(history_steps, observation,valid_actions)
        try:
            act = api_complete(system_prompt=system_prompt, prompt = prompt, model=model_name).strip()
        except:
            print ("This model's maximum context length is 4097 tokens.")
            break
        history_steps += '\nobservation: {}\nselected action: "{}"\nreward: {}\n'.format(observation, act, reward)
        observation, reward, done, info = env.step(act)
        sample_info = {
            'act': act,
            'observation': observation,
            'reward': reward,
            'done': done,
            'info': info,
        }
        walkthrough_list.append(sample_info)
        print (sample_info)
        if done:
            break
    
    cache_dir = os.path.join(args.cache_dir, game_name.split('.')[0])
    if os.path.exists(cache_dir) == False:
        os.makedirs(cache_dir)
    outfile = '{}/{}_walkthrough.json'.format(cache_dir, model_name)
    with open(outfile, 'w+', encoding='utf-8') as fout:
        fout.write(json.dumps(walkthrough_list, indent=4))
    print ('Well Done!')

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", '-m', type=str, default="gpt-3.5-turbo")
    parser.add_argument("--game_name", '-g', type=str, default="zork1")
    parser.add_argument("--jericho_path", '-j', type=str, default="./z-machine-games-master/jericho-game-suite")
    parser.add_argument("--cache_dir", '-cdir', type=str, default="./data/maps")
    parser.add_argument("--max_steps", type=int, default=120)
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    print ("Args: {}".format(args))
    play_game(args)