import os
import os.path as osp
import networkx as nx
import json
import csv
import pandas as pd
import tiktoken
import openai
import time
import traceback

from utils.map_utils import get_game_info
from utils.utils import find_json,read_json,save_json
from tqdm import tqdm


def call_openai_with_retry(model,message,temperature,stop=None,sleep_time=1.0,retry_cnt=4):
    i = 0
    while i < retry_cnt:
        time.sleep(i * sleep_time)
        try:
            return call_openai(model,message,temperature,stop=stop)
        except Exception as e:
            print(e)
            i += 1
    raise "gpt response error"

def call_openai(model,message,temperature,stop=None):
    completion = openai.ChatCompletion.create(
        model=model,
        messages=message,
        temperature=temperature,
        stop=stop,
    )
    return completion

def to_chat_json(role,text):
    
    return [
        {
            "role": role,
            "content": text
        }
    ]
      
def get_pretext(actions,locations,walkthrough,token_size_limit,model_name):
    
    def get_cut_off_and_walkthrough_text(walkthrough:str,token_size_limit:int,model_name:str):
        encoder = tiktoken.encoding_for_model(model_name)
        enc = encoder.encode(walkthrough)
        if len(enc) > token_size_limit:
            cut_off_walkthrough_text = encoder.decode(enc[:token_size_limit])
        else:
            cut_off_walkthrough_text = encoder.decode(enc)
        cut_off_number = int(cut_off_walkthrough_text.split('NUM: ')[-2].split('\n')[0])
        if cut_off_number > 70:
            cut_off_number = 70

        walkthrough_text = walkthrough.split('NUM: {}'.format(cut_off_number + 1))[0]

        return walkthrough_text,cut_off_number

    def get_action_text(actions:list)->str:
        action_text = f"The allowed actions are: {actions}"
        return action_text

    def get_location_text(locations:list)->str:
        locations_text = f"The list of places are: {locations}"
        return locations_text

    # G,actions,locations,all2all,all_pairs,walkthrough=get_game_info(map_dir,game_name)
    

    walkthrough_text,cut_off_number=get_cut_off_and_walkthrough_text(walkthrough,token_size_limit,model_name)
    action_text=get_action_text(actions)
    location_text = get_location_text(locations)
    
    config={
        "model": model_name,
        "temperature": 0,
        "cut_off":cut_off_number
    }
    
    pretext=to_chat_json("user",walkthrough_text)+to_chat_json("user",action_text)+to_chat_json("user",location_text)
    
    return {
        "config":config,
        "pretext":pretext,   
    }

def get_question(obj,task_name):
    assert task_name in ['pathgen','stepnav']
    
    src_node=obj["src_node"]
    dst_node=obj["dst_node"]

    if task_name=='stepnav':
        path_gt=obj["path_details"]
    
    
    
    if task_name=='pathgen':
        question = """
        Can you find a path from {} to {}, and format the output as a python list of python dictionary with keys'prev_node', 'node' and 'action'? Start your response with '['
        """.format(src_node, dst_node)
        
        return {
            "task":task_name,
            "src_node":src_node,
            "dst_node":dst_node,
            "task_id":obj["id"],
            "question":question,

        }
        
    elif task_name=='stepnav':
        action_list=[edge["action"] for edge in path_gt]
        question = """
    Starting from place {}, perform a list of action {}, where are you now? Describe the trajectory in a python list of python dictionary with keys 'prev_node', 'node' and 'action'. Start your response with '['.
    """.format(src_node, action_list)
    
        return {
            "task":task_name,
            "src_node":src_node,
            "action_list":action_list,
            "dst_node":dst_node,
            "task_id":obj["id"],
            "path_gt":path_gt,
            "question":question,

        }
    
def parse_response(response):
    path_str = '[' + response.split('[')[1].split(']')[0] + ']'
    path_lst = eval(path_str)
    for step in path_lst:
        assert isinstance(step, dict), 'Each step in the path should be a dictionary.'
    return path_lst

def evaluate_game(map_dir,result_dir,game_name,task_name,model_name):
    G,actions,locations,all2all,all_pairs,walkthrough=get_game_info(map_dir,game_name)
    
    if model_name.startswith('gpt-3.5'):
        token_size_limit=3600
    elif model_name.startswith('gpt-4'):
        token_size_limit=3600
        
    pretext=get_pretext(actions,locations,walkthrough,token_size_limit,model_name)
    
    final_dir_path=osp.join(result_dir,game_name,'results',f"{task_name}-{model_name}")
    if not osp.exists(final_dir_path):
        os.makedirs(final_dir_path)
        
    # collect evaluated task:
    json_list=find_json(final_dir_path)
    evaluated_tasks=set()
    for json_file in json_list:
        data=read_json(json_file)
        if 'task_id' in data.keys():
            evaluated_tasks.add(data['task_id'])
    
    # evaluate all the paths:
    error_task_ids=set()
    
    if task_name=='pathgen':
        task_list=all_pairs
    elif task_name=='stepnav':
        task_list=all2all


    for task in tqdm(task_list):
        
        # skip evaluated task
        if task['id'] in evaluated_tasks:
            print(f"{game_name}-{task_name}: task {task['id']} already evalutaed")
            continue
        
        # meet cut off limit
        if "path_min_cutoff" in task.keys():
            cut_off=task["path_min_cutoff"]
        elif "path_min_cutoffs" in task.keys():
            cut_off=min(task["path_min_cutoffs"])

        if cut_off>pretext["config"]["cut_off"]:
            print(f"{game_name}-{task_name}: task {task['id']} exceeds cutoff")
            continue
        
        question=get_question(task,task_name)
        message=pretext["pretext"]+to_chat_json("user",question["question"])
        
        # get response
        try:
            raw_response=call_openai_with_retry(pretext["config"]["model"],
                                            message,
                                            pretext["config"]["temperature"])
            
        except Exception as e:
            print(e,'gpt response:',f"{game_name}-{task_name}-{task['id']} failed 1st time")
            error_task_ids.add(task['id'])
            continue
        
        
        result={**pretext,**question}
        #parse response
        try:
            response = raw_response.choices[0].message['content']
            result['path'] = parse_response(response)
            result['raw_response'] = raw_response

        except Exception as e:
            print(e,'parsing:',f"{game_name}-{task_name}-{task['id']} failed in 1st time")
            error_task_ids.add(task['id'])
            continue
        
        save_json(final_dir_path, result,)
        
        evaluated_tasks.add(task['id'])
    
    # give failed task a second chance
    for task in tqdm(task_list):
        
        if task['id'] not in error_task_ids:
            continue
        
        question=get_question(task,task_name)
        message=pretext["pretext"]+to_chat_json("user",question["question"])

        # get response
        try:
            raw_response=call_openai_with_retry(pretext["config"]["model"],
                                            message,
                                            pretext["config"]["temperature"])
            
        except Exception as e:
            print(e,'gpt response:',f"{game_name}-{task_name}-{task['id']} failed in 2nd time")
            continue
        
    
        result={**pretext,**question}
        #parse response
        try:
            response = raw_response.choices[0].message['content']
            result['path'] = parse_response(response)
            result['raw_response'] = raw_response

        except Exception:
            print('parsing:',f"{game_name}-{task_name}-{task['id']} failed in 2nd time")
            result['error_message'] = traceback.format_exc()
            
        save_json(final_dir_path, result,)
        evaluated_tasks.add(task['id'])