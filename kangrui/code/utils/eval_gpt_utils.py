import os
import os.path as osp
import networkx as nx
import json
import matplotlib.pyplot as plt
import csv
import pandas as pd
from collections import deque
import time
        
def find_pair(task_id,all_pairs):
    pair = None
    for pair in all_pairs:
        if pair['id']==task_id:
            return pair
    return pair

def find_path(task_id,all2all):
    path = None
    for path in all2all:
        if path['id']==task_id:
            return path
    return path

# edit distance score
def normalized_edit_distance(s1, s2):
    s1 = s1.lower()
    s2 = s2.lower()
    
    m = len(s1) + 1
    n = len(s2) + 1

    dp = [[0] * n for _ in range(m)]

    for i in range(m):
        dp[i][0] = i

    for j in range(n):
        dp[0][j] = j

    for i in range(1, m):
        for j in range(1, n):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = min(
                    dp[i - 1][j] + 1,  # deletion
                    dp[i][j - 1] + 1,  # insertion
                    dp[i - 1][j - 1] + 1  # substitution
                )
    
    # Compute the normalized score
    max_len = max(len(s1), len(s2))
    score = 1 - dp[m - 1][n - 1] / max_len
    return score


# specific eval for dest finding

def get_multi_des(G,src_node,actions):
    # return all the nodes that can be reached given G,source_node and action list
    def bfs_get_multi_des(G,src_node,actions):
        dest_nodes=[]
        queue = deque([(src_node, 0)])

        while queue:
            current_node, step = queue.popleft()

            # If we've finished all actions
            if step == len(actions):
                dest_nodes.append(current_node)

            # If we haven't finished all actions yet
            if step < len(actions):
                for (_, next_node, attr) in G.out_edges(current_node, data=True):
                    if attr['action'].lower() == actions[step].lower(): 
                        queue.append((next_node, step + 1))

        return dest_nodes
   
    return bfs_get_multi_des(G,src_node,actions)




# new eval function sets, for both route_finding and dest_finding
def nice_eval(G, path, src_node, dst_node,eval_difficulty='strict'):
    assert eval_difficulty in ['strict','loose']

    # Get unique action list from the graph
    actions_gt = list({attr.get('action').lower() for (_, _, attr) in G.edges(data=True)})
    
    # get action list of the path
    path_actions=[]
    for node_info in path:
        if "action" in node_info.keys() and isinstance(node_info["action"],str):
            node_action=node_info["action"].lower()
            if eval_difficulty=='loose':
                action=max(actions_gt, key=lambda v: normalized_edit_distance(node_action, v))
            elif eval_difficulty=='strict':
                action=node_action
            path_actions.append(action)
    
    #try if src_node->path_actions->dst_node

    # def dfs_route_finding(G,src_node,dst_node,actions,step):
    #     if step>=len(actions):
    #         return src_node==dst_node
        
    #     for (_, next_node, attr) in G.out_edges(src_node, data=True):
    #         if attr['action']==actions[step] and dfs_route_finding(G, next_node, dst_node, actions, step + 1):
    #             return True
    #     return False
    

    def bfs_route_finding(G,src_node,dst_node,actions):
        start_time=time.time()
        queue = deque([(src_node, 0)])
        # visited = set([src_node])

        while queue:
            if time.time()-start_time>60:
                raise "maxloop limit exceeds"
            current_node, step = queue.popleft()

            # If we've arrived at the destination and finished all actions
            if current_node == dst_node and step == len(actions):
                return True

            # If we haven't finished all actions yet
            if step < len(actions):
                for (_, next_node, attr) in G.out_edges(current_node, data=True):
                    if attr['action'].lower() == actions[step].lower(): #and next_node not in visited:
                        # visited.add(next_node)
                        queue.append((next_node, step + 1))

        return False
    
    return bfs_route_finding(G,src_node,dst_node,path_actions)

    # normal evaluation
    # cur_node=src_node
    # for action in path_actions:
    #     prev_node=cur_node
    #     for (_, next_node, attr) in G.out_edges(cur_node, data=True):
    #         if attr['action'].lower()==action:
    #             cur_node=next_node
    #     if cur_node==prev_node:
    #         return False
    # return cur_node==dst_node

def harsh_eval(G, path, start_node, end_node):
    if path[0]["prev_node"]!= start_node or path[-1]["node"] != end_node:
        return 0

    for node_info in path:
        if not G.has_edge(node_info["prev_node"], node_info["node"]):
            return 0

        # support both DiGraph and MultiDiGraph
        edge_data = G.get_edge_data(node_info["prev_node"], node_info["node"])
        action_list=[]
        if 'action' in edge_data.keys():
            action_list.append(edge_data['action'])
        for k,v in edge_data.items():
            if isinstance(v,dict) and 'action' in v.keys():
                action_list.append(v['action'])

        if not node_info["action"] in action_list:
            return 0
    return 1

def success_eval(G, path,src_node,dst_node,actions=None,eval_difficulty='strict',task_type='pathgen'):
    assert task_type in ['pathgen','stepnav']

    if task_type=='pathgen':
        return nice_eval(G, path, src_node, dst_node,eval_difficulty)
    
    elif task_type=='stepnav':
        dst_nodes=get_multi_des(G,src_node,actions)
        lower_dst_nodes=[node.lower() for node in dst_nodes]
        assert dst_node.lower() in lower_dst_nodes

        if eval_difficulty=="strict":
            flag_eval=path[-1]['node'].lower() in lower_dst_nodes
        else:
            flag_eval=max([normalized_edit_distance(path[-1]['node'].lower(), v) for v in lower_dst_nodes])
        return flag_eval

def reasoning_eval(G, path,src_node,dst_node,actions,task_type):
    assert task_type in ['pathgen','stepnav']
    if task_type=='pathgen':
        return harsh_eval(G, path, src_node, dst_node)
    elif task_type=='stepnav':
        if len(path)!=len(actions):
            return False
        for idx,edge in enumerate(path):
            if edge['action']!=actions[idx]:
                return False
        return harsh_eval(G, path, src_node, path[-1]['node'])


def get_task_id(result_json):
    return result_json['task_id']


# general eval functions 
def get_cutoff(result_json):
    # load the json and read off the config field

    if "load_path" in result_json["config"].keys():
        load_path = result_json["config"]["load_path"]
        # get the last num from walkthrough json filename in the config field, iterate to find walkthrough json
        for path in load_path:
            if "walkthrough" in path:
                cutoff = path.split("/")[-1].split(".")[1].split("_")[-1]
                cutoff = int(cutoff)
                return cutoff
    elif "cut_off" in result_json["config"].keys():
        return int(result_json["config"]["cut_off"])
    
def eval_game(file,G,all2all,all_pairs,eval_difficulty='strict',task_type='pathgen',eval_set=None):
    #evaluate both route finding and destination finding
    # 'pathgen' for rf, 'stepnav' for df

    assert task_type in ['pathgen','stepnav']

    with open(file,'r') as f:
        result_json = json.load(f)
    
    task_id=get_task_id(result_json)
    # step0: check setlimit:
    if eval_set is not None: 
        if task_id not in eval_set:
            # print(file,'task_id not in eval_set, skip eval')
            return -1,-1,-1
        
    # step1: check cutoff
    cutoff=get_cutoff(result_json)
    path_gt=None
    pair_gt=None
    if task_type=='pathgen':
        pair_gt=find_pair(task_id,all_pairs)
        if pair_gt is None:
            print(file,'pair is none, skip eval')
            return -1,-1,-1
    else:
        path_gt=find_path(task_id,all2all)
        if path_gt is None:
            print(file,'path is none, skip eval')
            return -1,-1,-1  
    if task_type=='pathgen' and min(pair_gt['path_min_cutoffs'])>cutoff:
        print(file,f"pair_min_cutoffs {min(pair_gt['path_min_cutoffs'])} > {cutoff} exceeded, skip eval")
        return -1,-1,-1
    elif task_type=='stepnav' and path_gt['path_min_cutoff']>cutoff:
        print(file,f"path_min_cutoffs {path_gt['path_min_cutoff']} > {cutoff} exceeded, skip eval")
        return -1,-1,-1
    

    # step2: check answer format
    if not 'path' in result_json.keys():
        print(file,'path not existed, skip eval')
        return -2,-1,-1
    
    path=result_json['path']

    if not isinstance(path,list):
        print(file,'path is not list')
        return -2,-1,-1
    
    if len(path)==0:
        return -2,-1,-1
    
    for idx,edge in enumerate(path):
        if not isinstance(edge,dict):
            print(file,'path edge is not dict')
            return -2,-1,-1
        
        if 'prev_node' not in edge.keys() or 'node' not in edge.keys() or 'action' not in edge.keys():
            print(file,'path edge key error')
            return -2,-1,-1
        
        if not isinstance(path[idx]['prev_node'],str) or not isinstance(path[idx]['node'],str) or not isinstance(path[idx]['action'],str):
            print(file,'path edge value error')
            return -2,-1,-1
        

    src_node=result_json["src_node"]
    dst_node=result_json["dst_node"]
    actions=None
    if task_type=='stepnav':
        actions=result_json["action_list"]
    
    flag_easy=success_eval(G, path,src_node,dst_node,actions,eval_difficulty,task_type)
    flag_harsh=reasoning_eval(G, path,src_node,dst_node,actions,task_type)
    
    # hard for rf

    if task_type=='pathgen':
        shortest_path=None
        for p in all2all:
            if p["src_node"]==src_node and p["dst_node"]==dst_node and p["diff_shortest"]==0:
                shortest_path=p
                break
        if shortest_path is None:
            print("error, shortest path not found")
        flag_hard=shortest_path["all_steps_seen_in_forward"] is not True

    elif task_type=='stepnav':
        flag_hard=False
        for edge in result_json['path_gt']:

            if 'seen' in edge.keys():
                seen=edge["seen"]
            elif 'seen_in_forward' in edge.keys():
                seen=edge['seen_in_forward']

            if seen==False:
                flag_hard=True
                break
    
    return flag_easy,flag_harsh,flag_hard

def get_valid_task(file,G,all2all,all_pairs,eval_difficulty='strict',task_type='pathgen'):
    #evaluate both route finding and destination finding
    # 'pathgen' for rf, 'stepnav' for df

    assert task_type in ['pathgen','stepnav']

    with open(file,'r') as f:
        result_json = json.load(f)
    
    task_id=get_task_id(result_json)
    
    # step1: check cutoff
    cutoff=get_cutoff(result_json)
    path_gt=None
    pair_gt=None
    if task_type=='pathgen':
        pair_gt=find_pair(task_id,all_pairs)
        if pair_gt is None:
            print(file,'pair is none, skip eval')
            return None
    else:
        path_gt=find_path(task_id,all2all)
        if path_gt is None:
            print(file,'path is none, skip eval')
            return None  
    if task_type=='pathgen' and min(pair_gt['path_min_cutoffs'])>cutoff:
        print(file,f"pair_min_cutoffs {min(pair_gt['path_min_cutoffs'])} > {cutoff} exceeded, skip eval")
        return None
    elif task_type=='stepnav' and path_gt['path_min_cutoff']>cutoff:
        print(file,f"path_min_cutoffs {path_gt['path_min_cutoff']} > {cutoff} exceeded, skip eval")
        return None
    

    # step2: check answer format
    if not 'path' in result_json.keys():
        print(file,'path not existed, skip eval')
        return None
    
    path=result_json['path']

    if not isinstance(path,list):
        print(file,'path is not list')
        return None
    
    if len(path)==0:
        return None
    
    for idx,edge in enumerate(path):
        if not isinstance(edge,dict):
            print(file,'path edge is not dict')
            return None
        
        if 'prev_node' not in edge.keys() or 'node' not in edge.keys() or 'action' not in edge.keys():
            print(file,'path edge key error')
            return None
        
        if not isinstance(path[idx]['prev_node'],str) or not isinstance(path[idx]['node'],str) or not isinstance(path[idx]['action'],str):
            print(file,'path edge value error')
            return None
        

    
    return task_id

def get_gpt_valid_batch(game_name,result_dir,G,all2all,all_pairs,task_type='pathgen',model_name='gpt-4',eval_difficulty='strict'):
    rst=set()
    src_dir=osp.join(result_dir,game_name,'results',f"{task_type}-{model_name}")
    file_list=[]
    for file in os.listdir(src_dir):
        file_list.append(osp.join(src_dir,file))

    for file in file_list:  
        try:
            task_id=get_valid_task(file,G,all2all,all_pairs,eval_difficulty,task_type)
            if task_id is not None:
               rst.add(task_id) 
        except Exception as e:
            print(file,e)
            continue
   
    return rst

def eval_gpt_batch(game_name,result_dir,G,all2all,all_pairs,task_type='pathgen',model_name='gpt-4',eval_difficulty='strict',eval_set=None):
    src_dir=osp.join(result_dir,game_name,'results',f"{task_type}-{model_name}")
    file_list=[]
    for file in os.listdir(src_dir):
        file_list.append(osp.join(src_dir,file))
    easy_cnt=0
    harsh_cnt=0
    total=0
    
    hard_total=0
    hard_easy=0
    hard_harsh=0
    
    norm_total=0
    norm_easy=0
    norm_harsh=0

    format_fail=0
    total_file=0
    for file in file_list:  
        try:
            if eval_set is not None:
                easy,harsh,hard=eval_game(file,G,all2all,all_pairs,eval_difficulty,task_type,eval_set)
            else:
                easy,harsh,hard=eval_game(file,G,all2all,all_pairs,eval_difficulty,task_type)
        except Exception as e:
            print(file,e)
            continue


        if easy!=-1:
            total_file+=1
        if easy==-2:
            format_fail+=1


        if easy>=0:
            easy_cnt+=easy
            harsh_cnt+=harsh
            total+=1
            if hard:
                hard_total+=1
                hard_easy+=easy
                hard_harsh+=harsh
            else:
                norm_total+=1
                norm_easy+=easy
                norm_harsh+=harsh
   
    return {
    'success_cnt': easy_cnt,
    'reasoning_cnt': harsh_cnt,
    'total': total,
    'hard_success_cnt': hard_easy,
    'hard_reasoning_cnt': hard_harsh,
    'hard_total': hard_total,
    'easy_success_cnt': norm_easy,
    'easy_reasoning_cnt': norm_harsh,
    'easy_total': norm_total,
    'total_evaluted': total_file,
    'total_format_failed':format_fail,
}

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


