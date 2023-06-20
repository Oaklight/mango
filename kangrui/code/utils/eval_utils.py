import os
import os.path as osp
import networkx as nx
import json
import matplotlib.pyplot as plt
import csv
import pandas as pd

# general eval functions 
def get_cutoff(result):
    # load the json and read off the config field
    load_path = result["config"]["load_path"]
    # get the last num from walkthrough json filename in the config field, iterate to find walkthrough json
    for path in load_path:
        if "walkthrough" in path:
            cutoff = path.split("/")[-1].split(".")[1].split("_")[-1]
            cutoff = int(cutoff)
            return cutoff
        
def find_node_pair(src_node,dst_node,all_pairs):
    pair = None
    for pair in all_pairs:
        if pair['src_node']==src_node and pair['dst_node']==dst_node:
            return pair
    return pair
    

def get_code_from_anno(anno,anno2code):
    anno_dealt = anno.strip().lower() if isinstance(anno, str) else str(anno).strip().lower()

    for k,v in anno2code.items():
        if anno_dealt == k.strip().lower():
            return v[0]
    
    print(f"{anno} is not in anno2code")
    return anno

def deal_anno(result_json,anno2code):
    # change anno into code
    
    src_node=get_code_from_anno(result_json["src_node"],anno2code)
    dst_node=get_code_from_anno(result_json["dst_node"],anno2code)
    
    path=result_json['path']
    new_path=[]
    for edge in path:
        new_edge={}
        try:
            new_edge['prev_node']=get_code_from_anno(edge['prev_node'],anno2code)
            new_edge['node']=get_code_from_anno(edge['node'],anno2code)
            new_edge['action']=edge['action']
        except Exception as e:
            print("deal annotations error:",edge,e)
            new_path.append(edge)
            continue
        new_path.append(new_edge)
       
    return src_node,dst_node,new_path

# specific eval for dest finding
def eval_df(file,G,all2all,all_pairs,anno2code,code2anno):
    #evaluate destination finding given one question
    with open(file,'r') as f:
        result_json = json.load(f)
    
    if not 'path' in result_json.keys():
        print(file,'path not existed, skip eval')
        return -1,-1
    
    cutoff=get_cutoff(result_json)   
    src_node,dst_node,path=deal_anno(result_json,anno2code)
    pair=find_node_pair(src_node,dst_node,all_pairs)
    
    if (not isinstance(path[-1],dict)) or ('node' not in path[-1].keys()):
        print(file,'path format error')
        return -1,-1
    
    if pair is None:
        print(file,'pair is none, skip eval')
        return -1,-1
        
    
    if pair['num_paths']<1:
        print(file,'pair unreachable, skip eval')
        return -1,-1
    
    if min(pair['path_min_cutoffs'])>cutoff:
        print(file,f"path_min_cutoffs {min(pair['path_min_cutoffs'])} > {cutoff} exceeded, skip eval")
        return -1,-1
    
    # evaluation begins
    flag_eval=dst_node==path[-1]['node']
    flag_hard=False
    for edge in result_json['path_gt']:
        if edge["seen"]==False:
            flag_hard=True
            break
    
    return flag_eval,flag_hard



def eval_df_gpt_batch(game_name,result_dir,G,all2all,all_pairs,anno2code,code2anno,model_name='gpt-4'):
    task_type='stepnav'
    src_dir=osp.join(result_dir,game_name,'results',f"{task_type}-{model_name}")
    file_list=[]
    for file in os.listdir(src_dir):
        file_list.append(osp.join(src_dir,file))
    eval_cnt=0
    total=0
    
    hard_total=0
    hard_eval=0
    
    norm_total=0
    norm_eval=0
    for file in file_list:  
        try:
            flag_eval,flag_hard=eval_df(file,G,all2all,all_pairs,anno2code,code2anno)
        except Exception as e:
            print(file,e)
            continue
        if flag_eval!=-1:
            eval_cnt+=flag_eval
            total+=1
            if flag_hard:
                hard_total+=1
                hard_eval+=flag_eval
            else:
                norm_total+=1
                norm_eval+=flag_eval                       
        
    
    return {
    'pos': eval_cnt,
    'total': total,
    'hard_pos': hard_eval,
    'hard_total': hard_total,
    'norm_pos': norm_eval,
    'norm_total': norm_total,
}

def get_csv_df(rst_dict,path):
    fieldnames = ['name', 'nice_acc', 'harsh_acc','hard_nice_acc','hard_harsh_acc', 'norm_nice_acc', 'norm_harsh_acc']  
    fieldnames.extend(rst_dict[list(rst_dict.keys())[0]].keys()) 
    with open(path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for name, values in rst_dict.items():
            row = {
                'name': name, 
                'nice_acc': values['pos'] / values['total'], 
                'hard_nice_acc': values['hard_pos'] / values['hard_total'] if values['hard_total'] != 0 else 'NA',
                'norm_nice_acc': values['norm_pos'] / values['norm_total'] if values['norm_total'] != 0 else 'NA',
            }
            row.update(values)  
            writer.writerow(row)

# specific eval for route finding
def nice_eval(G, path, start_node, end_node):
    cur_node = start_node
    for node_info in path:
        prev_node = cur_node
        edges = G.out_edges(cur_node, data=True)
        for edge in edges:
            if edge[2]["action"] == node_info["action"]:
                cur_node = edge[1]  # Update current node
                break
        if cur_node == prev_node:
            return 0
    return 1 if cur_node == end_node else 0


def harsh_eval(G, path, start_node, end_node):
    if path[0]["prev_node"] != start_node or path[-1]["node"] != end_node:
        return 0

    for node_info in path:
        if not G.has_edge(node_info["prev_node"], node_info["node"]):
            return 0

        edge_data = G.get_edge_data(node_info["prev_node"], node_info["node"])
        if edge_data["action"] != node_info["action"]:
            return 0
    return 1

def eval_rf(file,G,all2all,all_pairs,anno2code,code2anno):
    #evaluate route finding given one question
    with open(file,'r') as f:
        result_json = json.load(f)
    
    if not 'path' in result_json.keys():
        print(file,'path not existed, skip eval')
        return -1,-1,-1
    
    cutoff=get_cutoff(result_json)   
    src_node,dst_node,path=deal_anno(result_json,anno2code)
    pair=find_node_pair(src_node,dst_node,all_pairs)
    
    
    if pair is None:
        print(file,'pair is none, skip eval')
        return -1,-1,-1
        
    
    if pair['num_paths']<1:
        print(file,'pair unreachable, skip eval')
        return -1,-1,-1
    
    if min(pair['path_min_cutoffs'])>cutoff:
        print(file,f"path_min_cutoffs {min(pair['path_min_cutoffs'])} > {cutoff} exceeded, skip eval")
        return -1,-1,-1
    
    
    flag_easy=nice_eval(G, path,src_node,dst_node)
    flag_harsh=harsh_eval(G, path,src_node,dst_node)
    
    shortest_path=None
    for p in all2all:
        if p["src_node"]==src_node and p["dst_node"]==dst_node and p["diff_shortest"]==0:
            shortest_path=p
            break
    if shortest_path is None:
        print("error, shortest path not found")
    flag_hard=shortest_path["all_steps_seen_in_forward"] is not True
    
    return flag_easy,flag_harsh,flag_hard

def eval_rf_gpt_batch(game_name,result_dir,G,all2all,all_pairs,anno2code,code2anno,model_name='gpt-4'):
    task_type='pathgen'
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
    for file in file_list:  
        try:
            easy,harsh,hard=eval_rf(file,G,all2all,all_pairs,anno2code,code2anno)
        except Exception as e:
            print(file,e)
            continue
        if easy!=-1:
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
    'easy_cnt': easy_cnt,
    'harsh_cnt': harsh_cnt,
    'total': total,
    'hard_total': hard_total,
    'hard_easy': hard_easy,
    'hard_harsh': hard_harsh,
    'norm_total': norm_total,
    'norm_easy': norm_easy,
    'norm_harsh': norm_harsh
}

def get_csv_rf(rst_dict,path):
    fieldnames = ['name', 'nice_acc', 'harsh_acc','hard_nice_acc','hard_harsh_acc', 'norm_nice_acc', 'norm_harsh_acc']  
    fieldnames.extend(rst_dict[list(rst_dict.keys())[0]].keys()) 
    with open(path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for name, values in rst_dict.items():
            row = {
                'name': name, 
                'nice_acc': values['easy_cnt'] / values['total'], 
                'harsh_acc': values['harsh_cnt'] / values['total'], 
                'hard_nice_acc': values['hard_easy'] / values['hard_total'] if values['hard_total'] != 0 else 'NA',
                'hard_harsh_acc': values['hard_harsh'] / values['hard_total'] if values['hard_total'] != 0 else 'NA',
                'norm_nice_acc': values['norm_easy'] / values['norm_total'] if values['norm_total'] != 0 else 'NA',
                'norm_harsh_acc': values['norm_harsh'] / values['norm_total'] if values['norm_total'] != 0 else 'NA'
            }
            row.update(values)  
            writer.writerow(row)


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

