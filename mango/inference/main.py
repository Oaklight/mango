"""
Paper: MANGO: A Benchmark for Evaluating Mapping and Navigation Abilities of Large Language Models

inference codebase
"""

import os
import argparse
from tqdm import tqdm

from utils import read_text, load_json, load_jsonl, save_json

def load_model(model_name, temperature, ckpt_dir, tokenizer_path, batch_size):
    if model_name in ['gpt-3.5', 'gpt4']:
        from models.gpt import GPTModel
        model = GPTModel(model_name, temperature)
    elif model_name in ['claude-instant-1', 'claude2']:
        from models.claude import ClaudeModel
        model = ClaudeModel(model_name, temperature)
    elif model_name in ['llama2']:
        from models.llama import LlamaModel
        model = LlamaModel(model_name, temperature, ckpt_dir, tokenizer_path, batch_size)
    elif model_name in ['rwkv']:
        from models.rwkv import RWKVModel
        model = RWKVModel(model_name, temperature, ckpt_dir, tokenizer_path, batch_size)
    else:
        raise NotImplementedError
    return model

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--exp_tag', type=str)
    parser.add_argument('--data_folder', type=str, default='./data')
    parser.add_argument('--save_folder', type=str, default='./results')
    parser.add_argument('--game_name', type=str, default='905')
    parser.add_argument('--task_type', type=str, choices=['route_finding', 'desti_finding'])
    parser.add_argument('--model_name', type=str, choices=['gpt-3.5', 'gpt4', 'claude-instant-1', 'claude2', 'llama2', 'rwkv'])
    parser.add_argument('--batch_size', type=int, default=1)
    parser.add_argument('--max_token_num', type=int, default=3600)
    parser.add_argument('--max_step_num', type=int, default=70)
    parser.add_argument('--temperature', type=float, default=0.0)
    parser.add_argument('--ckpt_dir', type=str, default=None)
    parser.add_argument('--tokenizer_path', type=str, default=None)
    return parser.parse_args()

if __name__=='__main__':
    local_rank = int(os.environ.get("LOCAL_RANK", 0))

    args = parse_args()

    exp_tag = args.exp_tag
    data_folder = args.data_folder
    save_folder = args.save_folder
    game_name = args.game_name
    task_type = args.task_type

    model_name = args.model_name
    batch_size = args.batch_size
    max_token_num = args.max_token_num
    max_step_num = args.max_step_num
    temperature = args.temperature
    ckpt_dir = args.ckpt_dir
    tokenizer_path = args.tokenizer_path

    if model_name in ["llama2", "rwkv"]:
        assert ckpt_dir is not None and tokenizer_path is not None, "Please specify the ckpt_dir and tokenizer path"

    model = load_model(model_name, temperature, ckpt_dir, tokenizer_path, batch_size)

    save_path = os.path.join(save_folder, f'{model_name}_{task_type}_{exp_tag}', game_name)
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    config_save_file = os.path.join(save_path, 'exp_config.json')
    save_json(vars(args), config_save_file)

    # walkthrough
    walkthrough_file = os.path.join(data_folder, game_name, f'{game_name}.walkthrough')
    walkthrough_text = read_text(walkthrough_file).strip().replace('===========','')
    walkthrough_text, cutoff_step_num = model.cutoff_input(walkthrough_text, max_token_num, max_step_num)

    # action_space
    action_space_path = os.path.join(data_folder, game_name, f'{game_name}.actions.json')
    action_space_list = load_json(action_space_path)

    # location_space
    location_space_path = os.path.join(data_folder, game_name, f'{game_name}.locations.json')
    location_space_list = load_json(location_space_path)

    # all sample list
    all_sample_list = []
    if task_type == "route_finding":
        # all_pairs
        all_pairs_path = os.path.join(data_folder, game_name, f'{game_name}.all_pairs.jsonl')
        all_pairs_list = load_jsonl(all_pairs_path)

        for pair in all_pairs_list:
            src_node = pair['src_node']
            dst_node = pair['dst_node']
            sample_id = pair['id']

            save_file = os.path.join(save_path, f'result_sample_id_{sample_id}.json')
            if os.path.exists(save_file):
                print ('{} exist!!! continue ...'.format(save_file))
                continue
            
            min_step_total_answerable = pair['min_step_total_answerable']
            sample_info = {
                "sample_id": sample_id,
                "game_name": game_name,
                "task": task_type,
                'src_node': src_node,
                'dst_node': dst_node,
                "walkthrough_text": walkthrough_text,
                "action_space_list": action_space_list,
                "location_space_list": location_space_list,
                "model_cutoff_num": cutoff_step_num,
                "min_step_total_answerable": min_step_total_answerable,
                "answerable": True,
                "answer": "",
                "save_file": save_file
            }

            if cutoff_step_num < min_step_total_answerable:
                print ("unanswerable sample, skipped.")
                sample_info['answerable'] = False
                save_json(sample_info, sample_info["save_file"])
                continue

            all_sample_list.append(sample_info)

    elif task_type == "desti_finding":
        # all2all
        all2all_path = os.path.join(data_folder, game_name, f'{game_name}.all2all.jsonl')
        all2all_list = load_jsonl(all2all_path)

        for traj in all2all_list:
            src_node = traj['src_node']
            dst_node = traj['dst_node']
            sample_id = traj['id']
            path_details = traj['path_details']
            action_list = [step['action'] for step in path_details]

            save_file = os.path.join(save_path, f'result_sample_id_{sample_id}.json')
            if os.path.exists(save_file):
                print (f'{save_file} exist!!! continue ...')
                continue

            min_step_total_answerable = traj['min_step_total_answerable']
            sample_info = {
                "sample_id": sample_id,
                "game_name": game_name,
                "task": task_type,
                'src_node': src_node,
                'dst_node': dst_node,
                "action_list": action_list,
                "walkthrough_text": walkthrough_text,
                "action_space_list": action_space_list,
                "location_space_list": location_space_list,
                "model_cutoff_num": cutoff_step_num,
                "min_step_total_answerable": min_step_total_answerable,
                "answerable": True,
                "answer": "",
                "save_file": save_file
            }

            if cutoff_step_num < min_step_total_answerable:
                print (f"unanswerable sample ({sample_id}), skipped.")
                sample_info['answerable'] = False
                save_json(sample_info, sample_info["save_file"])
                continue
        
            all_sample_list.append(sample_info)

    else:
        raise NotImplementedError
    
    batched_sample_list = [all_sample_list[i:i+batch_size] for i in range(0, len(all_sample_list), batch_size)]
    for batch in tqdm(batched_sample_list):
        samples, answers = model.process(batch, task_type=task_type)
        for idx, answer in enumerate(answers):
            if answer.startswith('Error'):
                print (f"sample {samples[idx]['sample_id']}: {answer}")
                exit(0)

            samples[idx]['answer'] = answer
            save_json(samples[idx], samples[idx]['save_file'])