from mango.evaluation.utils.metric_utils import EvalMetric, TaskType, success_rate,reasoning_acc
import json
import os
import csv

"""Eval format:

{
    "task_type": "--rf --df:str",
    "map_name": "name of the map:str",
    "step_num":"--int:int",
    "task_id":"hash of the question:str",
    "walkthrough":"input to the llm:str",
    "src_node": "src_node:str",
    "dst_node": "dst_node:str",
    "action_list": "type: python list, for df:list",
    "question":"question:str",
    "raw_output":"output of the llm [{'location_before:','action:','location_after'}]: str"
}

"""

    

def parse_raw_output(raw_output):
    """
    raw_output is in the format of ... [{'location_before:','action:','location_after'}...]..., need to extract the path

    use regex to extract the path
    find the first '[' and the first ']'   
    extract the string between the two brackets
    check if the list is in the correct format

    """
    raw_output=raw_output.strip()

    first_bracket_open_index = raw_output.find('[')
    first_bracket_close_index = raw_output.find(']')

    path=eval(raw_output[first_bracket_open_index:first_bracket_close_index+1])
    
    if not isinstance(path,list):
        print('path is not list')
        return None
    for edge in path:
        if 'location_before' not in edge.keys() or 'location_after' not in edge.keys() or 'action' not in edge.keys():
            print('path edge key error')
            return None
        elif not isinstance(edge['location_before'],str) or not isinstance(edge['location_after'],str) or not isinstance(edge['action'],str):
            print('path edge value error')
            return None
        
    return path

def eval_file(file,G,all_path_or_pair,eval_metric,task_type,eval_set=None,average_by_len=False):
   
    assert task_type in TaskType
    assert eval_metric in EvalMetric
    return_rst={'success':0,
                'reasoning':0,
                'is_hard':0,
                'path_len':0,
                'parsing_error':0,
                'id_error':0,
                'step_num_error':0}

    with open(file,'r') as f:
        infer_rst = json.load(f)
    
    if (eval_set is not None and infer_rst['task_id'] not in eval_set) or infer_rst['task_id'] not in all_path_or_pair:
        print('task_id not in eval_set, skip eval')
        return_rst['id_error']=1
        return return_rst
    
    if infer_rst['step_num']<all_path_or_pair[infer_rst['task_id']]['min_step_total_answerable']:
        print('step_num not meet cutoff, skip eval')
        return_rst['step_num_error']=1
        return return_rst
    
    path=parse_raw_output(infer_rst['raw_output'])
    if path is None:
        print('parsing error, skip eval')
        return_rst['parsing_error']=1
        return return_rst
    
    src_node=infer_rst["src_node"]
    dst_node=infer_rst["dst_node"]
    actions=infer_rst['action_list'] if task_type==TaskType.StepNav else None

    return_rst['path_len']=len(actions) if task_type==TaskType.StepNav and average_by_len else 1
    return_rst['success']=success_rate(G, path,src_node,dst_node,eval_metric,task_type,actions)
    return_rst['reasoning']=reasoning_acc(G, path,src_node,dst_node,actions,task_type)
    return_rst['is_hard']=infer_rst['step_num']>all_path_or_pair[infer_rst['task_id']]['min_step_forward_answerable']
    
    return return_rst

def get_valid_task(file,all_path_or_pair):
    with open(file,'r') as f:
        infer_rst = json.load(f)
    if infer_rst['task_id'] not in all_path_or_pair:
        return None
    if infer_rst['step_num']<all_path_or_pair[infer_rst['task_id']]['min_step_total_answerable']:
        return None
    path=parse_raw_output(infer_rst['raw_output'])
    if path is None:
        return None
    return infer_rst['task_id']

def get_valid_task_per_game(result_dir,game_name,all_path_or_pair):
    rst=set()
    src_dir=os.path.join(result_dir,game_name)
    file_list=[]
    for file in os.listdir(src_dir):
        file_list.append(os.path.join(src_dir,file))
    for file in file_list:  
        try:
            task_id=get_valid_task(file,all_path_or_pair)
            if task_id is not None:
               rst.add(task_id) 
        except Exception as e:
            print(file,e)
            continue
    return rst

def eval_file_per_game(result_dir,game_name,G,all_path_or_pair,eval_metric,task_type,eval_set=None,average_by_len=False):
    src_dir=os.path.join(result_dir,game_name)
    file_list=[]
    for file in os.listdir(src_dir):
        file_list.append(os.path.join(src_dir,file))
    
    eval_rst={'success_cnt':0,
                'reasoning_cnt':0,
                'total':0,
                'hard_success_cnt':0,
                'hard_reasoning_cnt':0,
                'hard_total':0,
                'easy_success_cnt':0,
                'easy_reasoning_cnt':0,
                'easy_total':0,
                'total_evaluted':0,
                'total_format_failed':0}
    
    for file in file_list:  
        try:
            return_rst=eval_file(G,all_path_or_pair,eval_metric,task_type,eval_set)

        except Exception as e:
            print(file,e)
            continue



        eval_rst['success_cnt']+=return_rst['success']*return_rst['path_len']
        eval_rst['reasoning_cnt']+=return_rst['reasoning']*return_rst['path_len']
        eval_rst['total']+=return_rst['path_len']
        eval_rst['hard_total']+=return_rst['path_len']*return_rst['is_hard']
        eval_rst['hard_success_cnt']+=return_rst['success']*return_rst['path_len']*return_rst['is_hard']
        eval_rst['hard_reasoning_cnt']+=return_rst['reasoning']*return_rst['path_len']*return_rst['is_hard']
        eval_rst['easy_total']+=return_rst['path_len']*(1-return_rst['is_hard'])
        eval_rst['easy_success_cnt']+=return_rst['success']*return_rst['path_len']*(1-return_rst['is_hard'])
        eval_rst['easy_reasoning_cnt']+=return_rst['reasoning']*return_rst['path_len']*(1-return_rst['is_hard'])
        eval_rst['total_evaluted']+=(1-return_rst['id_error'])*(1-return_rst['step_num_error'])
        eval_rst['total_format_failed']+=return_rst['parsing_error']
    
    return eval_rst




def get_csv(rst_dict,path):
    fieldnames = ['name', 'success_rate', 'reasoning_acc','easy_success_rate', 'hard_success_rate','easy_reasoning_acc','hard_reasoning_acc',]  
    fieldnames.extend(rst_dict[list(rst_dict.keys())[0]].keys()) 
    with open(path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for name, values in rst_dict.items():
            row = {
                'name': name, 
                'success_rate': values['success_cnt'] / values['total'], 
                'reasoning_acc': values['reasoning_cnt'] / values['total'], 
                'easy_success_rate': values['easy_success_cnt'] / values['easy_total'] if values['easy_total'] != 0 else 'NA',
                'hard_success_rate': values['hard_success_cnt'] / values['hard_total'] if values['hard_total'] != 0 else 'NA',
                'easy_reasoning_acc': values['easy_reasoning_cnt'] / values['easy_total'] if values['easy_total'] != 0 else 'NA',
                'hard_reasoning_acc': values['hard_reasoning_cnt'] / values['hard_total'] if values['hard_total'] != 0 else 'NA',
            }
            row.update(values)  
            writer.writerow(row)