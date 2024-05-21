import os.path as osp
import json
import hashlib
import subprocess

def compute_hash(obj):
    #works for both dict and list of dict
    obj_str = json.dumps(obj,sort_keys=True).encode()
    obj_hashed = hashlib.sha256(obj_str)
    
    return obj_hashed.hexdigest()

def extract_path_gt_from_file(file_name):
    with open(file_name,'r') as f:
        result_json = json.load(f)
        
    path_gt=result_json["path_gt"]
    return path_gt

def extract_pair_from_file(file_name):
    with open(file_name,'r') as f:
        result_json = json.load(f)
        
    pair_dict={
        "src_node":result_json["src_node"],
        "dst_node":result_json["dst_node"]
    }
    return pair_dict

def extract_path_with_feature(path,feature_list):
    new_path=[]
    for edge in path:
        edge_new_attr={}
        for feature in feature_list:
            edge_new_attr[feature]=edge[feature]
        new_path.append(edge_new_attr)
    return new_path
    
def compute_hash_for_path(path:list,feature_list=["prev_node","node","action"]):
    # compute hash for a path:
#     path = [
#             {
#                 "prev_node": "Bathroom",
#                 "node": "Bedroom",
#                 "action": "north",
#                 "seen_in_forward": True,
#                 "step_min_cutoff": 3
#             }
#         ]

    new_path=extract_path_with_feature(path,feature_list)
    hash_code=compute_hash(new_path)
    return hash_code

def compute_hash_for_pair(pair:dict):
    # compute hash for a path:
    # {
    #     "src_node": "Bathroom",
    #     "dst_node": "Bedroom",
    #     "num_paths": 1,
    #     "path_min_cutoffs": [
    #         3
    #     ]
    # },

    pair_dict={
        "src_node":pair["src_node"],
        "dst_node":pair["dst_node"]
    }
    hash_code=compute_hash(pair_dict)
    return hash_code

def merge_dirs(src, dst):
    try:
        if osp.exists(dst):
            subprocess.run(["cp", "-r", src+'/.', dst], check=True)
        else:
            subprocess.run(["cp", "-r", src, dst], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to merge {src} into {dst}. Error: {str(e)}")
            

def get_path_id_set(all2all):
    path_id_set=set()
    for path in all2all:
        path_details=path["path_details"]
        path_id=compute_hash_for_path(path_details)
        path_id_set.add(path_id)
    return path_id_set

def get_pair_id_set(allpairs):
    pair_id_set=set()
    for pair in allpairs:
       pair_dict={
        "src_node":pair["src_node"],
        "dst_node":pair["dst_node"]
    }
       pair_hash=compute_hash_for_pair(pair_dict)
       pair_id_set.add(pair_hash)
       
    return pair_id_set