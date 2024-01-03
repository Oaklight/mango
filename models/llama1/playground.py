
import os
from utils import read_json
import re
import sys

sys.path.append('/remote-home/pli/mango/kangrui/code/utils')
from clean_utils import compute_hash_for_path

def check_path_exist(task_info):
    # task_id = task_info['sample_id']
    old_folder = '/remote-home/pli/mango/data_backup_pli/llama_results_processed/{}/results/stepnav_llama'.format(task_info['game_name'])
    
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


if __name__ == '__main__':
    in_path = '/remote-home/pli/mango/inhouse_llms_results_pli/advent/results/step_navi_llama'
    json_file_names = os.listdir(in_path)
    json_file_list = [read_json('{}/{}'.format(in_path, name)) for name in json_file_names]

    for task_info in json_file_list:
        exist, task_info = check_path_exist(task_info)
        print (exist)
