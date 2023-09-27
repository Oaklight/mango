"""
# https://jericho-py.readthedocs.io/en/latest/index.html
"""

import os
import datetime
import argparse
import json

import openai
# https://github.com/openai/openai-cookbook/blob/main/examples/How_to_handle_rate_limits.ipynb
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff

from jericho import *

# openai api
openai.api_key = os.environ.get('OPENAI_API_KEY')
openai.organization = os.environ.get('OPENAI_API_ORG')

@retry(wait=wait_random_exponential(min=5, max=60), stop=stop_after_attempt(6))
def api_complete(system_prompt, prompt, model="gpt-3.5-turbo", temperature=0.0):
    try:
        completion = openai.ChatCompletion.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
        )
        return completion.choices[0].message['content']
    except openai.error.InvalidRequestError as e:
        return 'Exceeded context length limitation.'
    except Exception as e:
        raise e

system_prompt = "Your task is to play an interactive fiction game."
prompt_base = """history: {}\nConsider where you should do next, and choose one appropriate action from the valid actions list: {}\nPlease just tell me the selected action without any extra words."""

def format_action_history(action_list):
    history = ''
    for action_info in action_list:
        history += '- selected action: {}\n- observation: {}\n- reward: {}\n'.format(action_info['act'], action_info['observation'], action_info['reward'])
    return history

def play_game(args):
    model_name = args.model_name
    jericho_path = args.jericho_path
    game_name = args.game_name
    max_steps = args.max_steps

    # cache_dir
    cache_dir = os.path.join(args.cache_dir, game_name.split('.')[0])
    if os.path.exists(cache_dir) == False:
        os.makedirs(cache_dir)
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    outfile = '{}/{}_cache_{}.json'.format(cache_dir, model_name, formatted_datetime)

    # env
    env = FrotzEnv("{}/{}".format(jericho_path, game_name))
    
    # init
    initial_observation, info = env.reset()
    valid_actions = env.get_valid_actions()
    action_info = {
        'step': 0,
        'act': 'Init',
        'valid_actions': valid_actions,
        'observation': initial_observation,
        'reward': 0,
        'score': 0,
        'info': info,
        'done': False
    }
    action_list = [action_info]
    score = 0

    # loop
    for step_num in range(1, max_steps+1):
        history = format_action_history(action_list)
        valid_actions = env.get_valid_actions()

        prompt = prompt_base.format(history, valid_actions)
        response = api_complete(system_prompt=system_prompt, prompt = prompt, model=model_name)
        if response == 'Exceeded context length limitation.':
            print (response)
            break
        act = response.strip().strip('"').strip("'")
        observation, reward, done, info = env.step(act)
        score += reward
        print ("step: {} ; score: {}".format(step_num, score))
        action_info = {
            'step': step_num,
            'act': act,
            'valid_actions': valid_actions,
            'observation': observation,
            'reward': reward,
            'score': score,
            'info': info,
            'done': done,
            'prompt': prompt,
            'response': response
        }
        with open(outfile, 'a+', encoding='utf-8') as fout:
            fout.write(json.dumps(action_info, indent=4))
            fout.write('\n')

    print ('Well Done!')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", '-m', type=str, default="gpt-3.5-turbo")
    parser.add_argument("--game_name", '-g', type=str, default="zork1.z5")
    parser.add_argument("--jericho_path", '-j', type=str, default="./z-machine-games-master/jericho-game-suite")
    parser.add_argument("--cache_dir", '-cdir', type=str, default="./data/maps")
    parser.add_argument("--max_steps", type=int, default=70)
    parser.add_argument("--aug_map", action='store_true')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    print ("Args: {}".format(args))
    play_game(args)