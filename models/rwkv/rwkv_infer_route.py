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
from utils import read_json, read_txt, cutoff_walkthrough, process, check_pair_exist, save_json

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
    print(f'Current rank {rank}')
    world_size = dist.get_world_size()

    time_s = time.time()
    model, tokenizer = init_model(rwkv_dir, ckpt_dir)
    model = model.to(device_id)
    tokenizer = tokenizer.to(device_id)

    data_folder = '{}/data'.format(mango_folder)
    game_name_list = sorted(os.listdir(data_folder))
    print ("==> game name list: ", game_name_list)
    if end_game_idx == 10000:
        end_game_idx = len(game_name_list)
    
    game_num = end_game_idx - start_game_idx
    tmp_start_game_idx = start_game_idx + (rank/world_size) * game_num
    tmp_end_game_idx = start_game_idx + (rank/world_size) * game_num

    for game_name in game_name_list[tmp_start_game_idx:tmp_end_game_idx]:
        print ("gpu {} processing game {} ...".format(rank, game_name))

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

        # all_pairs
        all_pairs_path = '{}/{}/{}.all_pairs.json'.format(data_folder, game_name, game_name)
        all_pairs_dict = read_json(all_pairs_path)

        for pair in tqdm(all_pairs_dict):
            src_node = pair['src_node']
            dst_node = pair['dst_node']
            sample_id = pair['id']

            question_path_gen = """!!! Can you find a path from '{}' to '{}'?\nFormat the output as a python list of python dictionary with keys 'location_before', 'action' and 'location_after'.\n{}\n{}\n""".format(src_node, dst_node, action_space_prompt, place_name_prompt)
            question_path_gen += "\nAnswer: [{{'location_before': '{}', 'action': ".format(src_node)
            prefix_path_gen = ''.join((prefix_walkthrough, question_path_gen))

            save_path = '{}/{}/results/path_gen_rwkv'.format(save_folder, game_name)
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
                "task": "pathgen",
                'src_node': src_node,
                'dst_node': dst_node,
                "sample_id": sample_id,
                "pretext": prefix_walkthrough,
                'step_num': step_num,
                'question': question_path_gen,
                'query': prefix_path_gen,
                'save_file': save_file,
                "time": now_str
            }

            old_folder = mango_folder + '/mango-inhouse-llms/rwkv_results_processed/{}/results/path_gen_llama'.format(task_info['game_name'])
            exist, task_info = check_pair_exist(task_info, old_folder=old_folder, mango_folder=mango_folder)
            if exist:
                save_json(task_info['save_file'], task_info)
                print ('{} exist in pre experiments!!! update and continue ...'.format(save_file))
                continue

            response = rwkv_infer(model, tokenizer, task_info['query'], stop_token=']', chunk_len= chunk_len)
            process([task_info], [response], 0, time_s)
            time_s = time.time()

        print ("Good Job!")
    destory()

if __name__ == "__main__":
    fire.Fire(main)