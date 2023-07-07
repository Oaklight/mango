"""
destination finding
"""

import os
import sys
import fire
import time
import datetime
from tqdm import tqdm

from utils_llama import setup_model_parallel, load
from utils import read_json, read_txt, cutoff_walkthrough, process, check_path_exist, save_json


def main(
    ckpt_dir: str,
    tokenizer_path: str,
    mango_folder: str,
    save_folder: str,
    max_batch_size: int = 48,
    temperature: float = 0.0,
    top_p: float = 0.95,
    max_seq_len: int = 2048,
    start_game_idx: int = 0,
    end_game_idx: int = 10000
):
    time_s = time.time()
    local_rank, world_size = setup_model_parallel()
    if local_rank > 0:
        sys.stdout = open(os.devnull, "w")

    generator = load(
        ckpt_dir, tokenizer_path, local_rank, world_size, max_seq_len, max_batch_size
    )
    tokenizer = generator.tokenizer

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
        prefix_walkthrough, step_num = cutoff_walkthrough(walkthrough_line, tokenizer, max_step = 70, prompt_length = 1500)
        prefix_walkthrough = '!!! Here is a walkthrough of a text game:\n' + prefix_walkthrough
        
        # all2all
        all2all_path = '{}/{}/{}.all2all.json'.format(data_folder, game_name, game_name)
        all2all_dict = read_json(all2all_path)

        task_info_list = [] 
        for traj in tqdm(all2all_dict):
            src_node = traj['src_node']
            dst_node = traj['dst_node']
            path_gt = traj['path_details']
            action_list = [step['action'] for step in path_gt]
            sample_id = traj['id']

            question_step_navi = """!!! Starting from location '{}', perform a list of action {}, where are you now?\nDescribe the trajectory in a python list of python dictionary with keys 'location_before', 'action' and 'location_after'.\n{}\n{}\n""".format(src_node, action_list, action_space_prompt, place_name_prompt)
            question_step_navi += "\nAnswer: [{{'location_before': '{}', 'action': '{}', 'location_after': ".format(src_node, action_list[0])
        
            prefix_step_navi = ''.join((prefix_walkthrough, question_step_navi))

            save_path = '{}/{}/results/step_navi_llama'.format(save_folder, game_name)
            os.makedirs(save_path, exist_ok=True)

            save_file = '{}/results_sample_id_{}.json'.format(save_path,sample_id)
            if os.path.exists(save_file):
                if local_rank == 0:
                    print ('{} exist!!! continue ...'.format(save_file))
                continue

            now = datetime.datetime.now()
            now_str = now.strftime("%Y_%m_%d_%H_%M_%S")
            task_info = {
                "game_name": game_name,
                "model": "llama",
                "task": "pathgen",
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

            old_folder = '/remote-home/pli/mango/data_backup_pli/llama_results_processed/{}/results/stepnav_llama'.format(task_info['game_name'])
            exist, task_info = check_path_exist(task_info, old_folder=old_folder)
            if exist:
                if local_rank == 0:
                    save_json(task_info['save_file'], task_info)
                    print ('{} exist in pre experiments!!! update and continue ...'.format(save_file))
                continue

            task_info_list.append(task_info)
            if len(task_info_list) == int(max_batch_size):
                llama_query_list = [task['query'] for task in task_info_list]
                responses = generator.generate(
                    llama_query_list, max_gen_len=512, temperature=temperature, top_p=top_p
                )  
                process(task_info_list, responses, local_rank, time_s)
                time_s = time.time()
                task_info_list = []
                
        if len(task_info_list) > 0:
            llama_query_list = [task['query'] for task in task_info_list]
            responses = generator.generate(
                llama_query_list, max_gen_len=512, temperature=temperature, top_p=top_p
            )  
            process(task_info_list,responses, local_rank, time_s)
            time_s = time.time()
            task_info_list = [] 

        print ("Good Job!")


if __name__ == "__main__":
    fire.Fire(main)