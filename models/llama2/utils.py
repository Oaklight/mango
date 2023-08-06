import json
import re
import time
import os
import sys
sys.path.append('/remote-home/pli/mango/kangrui/code/utils')
from clean_utils import compute_hash_for_pair, compute_hash_for_path
"""
def compute_hash_for_path(path:list,feature_list=["prev_node","node","action"]):
    # compute hash for a path:
#     path = [
#             {
#                 "prev_node": "bathroom (obj44)",
#                 "node": "bedroom (obj25)",
#                 "action": "north",
#                 "seen_in_forward": True,
#                 "step_min_cutoff": 3
#             }
#         ]

    new_path=extract_path_with_feature(path,feature_list)
    hash_code=compute_hash(new_path)
    return hash_code
"""

def check_path_exist(task_info, old_folder):
    # task_id = task_info['sample_id']

    task_path_gt = task_info['path_gt']
    task_path_gt_new = []
    for item in task_path_gt:
        tmp = item
        tmp['prev_node'] = item['prev_node'].lower()
        tmp['node'] = item['node'].lower()
        task_path_gt_new.append(tmp)
    task_id = compute_hash_for_path(task_path_gt_new)

    json_file_names = os.listdir(old_folder)
    json_file_list = [read_json('{}/{}'.format(old_folder, name)) for name in json_file_names] # old

    path_gt_list = [item["path_gt"] for item in json_file_list]
    path_gt_list_new = []
    for path_gt in path_gt_list:
        new_path = []
        for item in path_gt:
            tmp = item
            tmp['prev_node'] = re.sub(r'\(obj\d+\)', '', item['prev_node']).strip()
            tmp['node'] = re.sub(r'\(obj\d+\)', '', item['node']).strip()
            new_path.append(tmp)
        path_gt_list_new.append(new_path)

    hash_ids= [compute_hash_for_path(item) for item in path_gt_list_new]

    exist = False
    if task_id in hash_ids:
        hash_idx = hash_ids.index(task_id)
        json_old = json_file_list[hash_idx]
        if json_old['pretext'] == task_info['pretext'] and json_old['question'] == task_info['question']:
            task_info['path'] = json_old['path']
            task_info['raw_response'] = json_old['raw_response']
            exist = True
        else:
            print ("context not equal, continue.")
    else:
        print ("task not in hash ids.")
    return exist, task_info

def check_pair_exist(task_info, old_folder):
    task_id = task_info['sample_id']
    json_file_names = os.listdir(old_folder)
    json_file_list = [read_json('{}/{}'.format(old_folder, name)) for name in json_file_names] # old
    hash_ids= [compute_hash_for_pair(item) for item in json_file_list]

    exist = False
    if task_id in hash_ids:
        hash_idx = hash_ids.index(task_id)
        json_old = json_file_list[hash_idx]
        if json_old['pretext'] == task_info['pretext'] and json_old['question'] == task_info['question']:
            task_info['path'] = json_old['path']
            task_info['raw_response'] = json_old['raw_response']
            exist = True
        else:
            print ("context not equal, continue.")
    else:
        print ("task not in hash ids.")
    return exist, task_info


def read_txt(txt_path):
    with open(txt_path, 'r') as fin:
        text = fin.read()
    return text


def read_json(json_path):
    with open(json_path, 'r') as f:
        json_object = json.load(f)
    return json_object

def save_json(save_path, save_object):
    json_object = json.dumps(save_object, indent=4)
    with open(save_path, 'w+') as f:
        f.write(json_object)
    print ("file saved to {}".format(save_path))
    return None

def convert_moves2walkthrough_anno(csv_file_in, action_list):
    with open(csv_file_in, 'r', encoding='utf-8') as fin:
        lines = fin.readlines()
        lines = [line.strip() for line in lines][1:]

    walkthrough_line = '==>STEP NUM: 0\n==>ACT: Init\n'
    action_list = action_list[1:] # ignore init
    location_after = 'placeholder'
    pattern = r',(?=(?:(?:[^"]*"){2})*[^"]*$)'
    placeholder = ''

    for idx, line in enumerate(lines[:len(action_list)]):
        step_num, tmp_location_before, tmp_location_after = re.split(pattern, line)[:3]
        tmp_location_before = tmp_location_before.strip().strip('"')
        tmp_location_after = tmp_location_after.strip().strip('"')

        if idx == 0:
            if tmp_location_before == '':
                tmp_location_before = 'placeholder'
                tmp_location_after = 'placeholder'
            walkthrough_line += '==>OBSERVATION: {}\n\n'.format(tmp_location_before)

        if tmp_location_before == '':
            location_before = location_after
        else:
            if idx!=0 and location_before == 'placeholder':
                placeholder = tmp_location_before
            location_before = location_after
            location_after = tmp_location_after

        action = action_list[idx].strip()
        walkthrough_line += '==>STEP NUM: {}\n==>ACT: {}\n==>OBSERVATION: {}\n\n'.format(step_num, action, location_after)

    assert placeholder != 'placeholder'
    if 'placeholder' in walkthrough_line:
        walkthrough_line = walkthrough_line.replace('placeholder', placeholder)
    return walkthrough_line

def find_max_step_num(string):
    pattern = r'\n==>STEP NUM: (\d+)'
    matches = re.findall(pattern, string)
    if matches:
        max_step_num = max(int(match) for match in matches)
        return max_step_num
    else:
        return None

def cutoff_walkthrough(input_line, tokenizer, max_step = 70, prompt_length = 1500):
    for step_num in range(max_step + 1, 0, -1):
        prefix_walkthrough = input_line.split("\n==>STEP NUM: {}".format(step_num))[0] + '\n'
        tokens_num = len(tokenizer.encode(prefix_walkthrough, bos=True, eos=False))
        if tokens_num < prompt_length: # <=
            break
    step_num = find_max_step_num(prefix_walkthrough)
    return prefix_walkthrough, step_num


def process(task_info_list, responses, local_rank, time_s):
    structure_acc = 0
    structure_all = 0
    for idx, task_info in enumerate(task_info_list):
        query = task_info['query']
        response = responses[idx]['generation']
        response = query + response
        task_info['raw_response'] = response.strip()

        tmp_text = re.search(r"Answer: \[(.*?)\]", response.strip(), re.DOTALL)
        if tmp_text:
            task_info['path'] = tmp_text.group(0).strip().lstrip('Answer: ')
            structure_acc += 1
        else:
            task_info['path'] = ''
        structure_all += 1

        if local_rank == 0:
            # print ("output ===> ", task_info['raw_response'])
            save_json(task_info['save_file'], task_info)
    time_e = time.time()
    print ("#Structure acc: {}/{}".format(structure_acc, structure_all))
    print ("#Time used: {} min".format((time_e - time_s)/60))