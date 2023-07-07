# Copyright (c) Meta Platforms, Inc. and affiliates.
# This software may be used and distributed according to the terms of the GNU General Public License version 3.

from typing import Tuple
import os
import sys
import torch
import time
import json
import re
import argparse
from tqdm import tqdm
import fire
import datetime
import random

sys.path.append(os.getcwd())
from utils_rwkv import init_model, rwkv_infer
from utils import read_json, read_txt, cutoff_walkthrough, process, check_path_exist, save_json

import torch.distributed as dist
def setup():
    dist.init_process_group('nccl')

def destroy():
    dist.destroy_process_group()


def main(
    rwkv_dir: str,
    ckpt_dir: str,
    mango_folder: str,
    save_folder: str,
    chunk_len: int,
    start_game_idx: int = 0,
    end_game_idx: int = 10000
):
    setup()
    rank = dist.get_rank()
    device_id = rank % torch.cuda.device_count()
    world_size = dist.get_world_size()
    print(f'Current rank {rank}')
    print(f'World size {world_size}')

    time_s = time.time()
    model, tokenizer = init_model(rwkv_dir, ckpt_dir, device_id)

    data_folder = '{}/data'.format(mango_folder)
    game_name_list = sorted(os.listdir(data_folder))
    print ("==> game name list: ", game_name_list)

    for game_name in game_name_list[start_game_idx:end_game_idx]:
        print ("processing game {} ...".format(game_name))

        # action_space
        action_space_file = '{}/{}/{}.actions.json'.format(data_folder, game_name, game_name)
        action_space_list = read_json(action_space_file)
        action_space_prompt = "The allowed actions are: {}.".format(action_space_list)

        # place_name
        places_name_file = '{}/{}/{}.locations.json'.format(data_folder, game_name, game_name)
        place_name_list = read_json(places_name_file)
        place_name_prompt = "The list of locations are: {}.".format(place_name_list)

        # walkthrough_line
        walkthrough_file = '{}/{}/{}.walkthrough'.format(data_folder, game_name, game_name)
        walkthrough_line = read_txt(walkthrough_file).strip().replace('===========','')
        prefix_walkthrough, step_num = cutoff_walkthrough(walkthrough_line, max_step = 70)
        prefix_walkthrough = '!!! Here is a walkthrough of a text game:\n' + prefix_walkthrough

        # all2all
        all2all_path = '{}/{}/{}.all2all.json'.format(data_folder, game_name, game_name)
        all2all_dict = read_json(all2all_path)

        task_num = len(all2all_dict)
        tmp_start_idx = int((rank/world_size) * task_num)
        tmp_end_idx = int(((rank+1)/world_size) * task_num)
        for traj in tqdm(all2all_dict[tmp_start_idx:tmp_end_idx]):
            src_node = traj['src_node']
            dst_node = traj['dst_node']
            path_gt = traj['path_details']
            action_list = [step['action'] for step in path_gt]
            sample_id = traj['id']

            question_step_navi = """!!! Starting from location '{}', perform a list of action {}, where are you now?\nDescribe the trajectory in a python list of python dictionary with keys 'location_before', 'action' and 'location_after'.\n{}\n{}\n""".format(src_node, action_list, action_space_prompt, place_name_prompt)
            question_step_navi += "\nAnswer: [{{'location_before': '{}', 'action': '{}', 'location_after': ".format(src_node, action_list[0])
            prefix_step_navi = ''.join((prefix_walkthrough, question_step_navi))

            save_path = '{}/{}/results/step_navi_rwkv'.format(save_folder, game_name)
            os.makedirs(save_path, exist_ok=True)

            save_file = '{}/results_sample_id_{}.json'.format(save_path,sample_id)
            if os.path.exists(save_file):
                print ('{} exist!!! continue ...'.format(save_file))
                continue

            now = datetime.datetime.now()
            now_str = now.strftime("%Y_%m_%d_%H_%M_%S")
            task_info = {
                "game_name": game_name,
                "model": "rwkv",
                "task": "stepnav",
                'src_node': src_node,
                'dst_node': dst_node,
                "path_gt": path_gt,
                "sample_id": sample_id,
                "pretext": prefix_walkthrough,
                'step_num': step_num,
                'question': question_step_navi,
                'query': prefix_step_navi,
                'save_file': save_file,
                "time": now_str
            }

            old_folder = mango_folder + '/mango-inhouse-llms/rwkv_results_processed/{}/results/stepnav_llama'.format(task_info['game_name'])
            exist, task_info = check_path_exist(task_info, old_folder=old_folder, mango_folder=mango_folder)
            if exist:
                save_json(task_info['save_file'], task_info)
                print ('{} exist in pre experiments!!! update and continue ...'.format(save_file))
                continue

            response = rwkv_infer(model, tokenizer, task_info['query'], stop_token=']', chunk_len= chunk_len)
            process([task_info], [response], 0, time_s)
            time_s = time.time()

        print ("Good Job!")
    destroy()
    

if __name__ == "__main__":
    fire.Fire(main)