"""
route finding
"""

import os
import sys
import fire
import time
import re
import datetime
from tqdm import tqdm


sys.path.append('/home-nfs/pengli/workspace/projects/codellama')
from llama import Llama
from utils import read_json, read_txt, cutoff_walkthrough, process


def main(
    ckpt_dir: str,
    tokenizer_path: str,
    mango_folder: str,
    save_folder: str,
    max_batch_size: int = 48,
    temperature: float = 0.0,
    top_p: float = 0.95,
    max_seq_len: int = 4096,
    start_game_idx: int = 0,
    end_game_idx: int = 10000
):
    time_s = time.time()
    local_rank = int(os.environ.get("LOCAL_RANK", 0))

    generator = Llama.build(
        ckpt_dir=ckpt_dir,
        tokenizer_path=tokenizer_path,
        max_seq_len=max_seq_len,
        max_batch_size=max_batch_size,
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
        prefix_walkthrough, step_num = cutoff_walkthrough(walkthrough_line, tokenizer, max_step = 70, prompt_length = 3600)
        prefix_walkthrough = '!!! Here is a walkthrough of a text game:\n' + prefix_walkthrough

        # all_pairs
        all_pairs_path = '{}/{}/{}.all_pairs.json'.format(data_folder, game_name, game_name)
        all_pairs_dict = read_json(all_pairs_path)

        task_info_list = [] 
        for pair in tqdm(all_pairs_dict):
            src_node = pair['src_node']
            dst_node = pair['dst_node']
            sample_id = pair['id']

            question_path_gen = """!!! Can you find a path from '{}' to '{}'?\nFormat the output as a python list of python dictionary with keys 'location_before', 'action' and 'location_after'.\n{}\n{}\n""".format(src_node, dst_node, action_space_prompt, place_name_prompt)
            question_path_gen += "\nAnswer: [{{'location_before': '{}', 'action': ".format(src_node)
            prefix_path_gen = ''.join((prefix_walkthrough, question_path_gen))

            save_path = '{}/{}/results/path_gen_llama'.format(save_folder, game_name)
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
                "model": ckpt_dir,
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

            task_info_list.append(task_info)
            if len(task_info_list) == int(max_batch_size):
                llama_query_list = [task['query'] for task in task_info_list]
                responses = generator.text_completion(
                    llama_query_list, max_gen_len=512, temperature=temperature, top_p=top_p
                )  
                process(task_info_list, responses, local_rank, time_s)
                time_s = time.time()
                task_info_list = []
                
        if len(task_info_list) > 0:
            llama_query_list = [task['query'] for task in task_info_list]
            responses = generator.text_completion(
                llama_query_list, max_gen_len=512, temperature=temperature, top_p=top_p
            )  
            process(task_info_list,responses, local_rank, time_s)
            time_s = time.time()
            task_info_list = [] 

        print ("Good Job!")


if __name__ == "__main__":
    fire.Fire(main)