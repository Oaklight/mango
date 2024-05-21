import fire
import os
import json
import networkx as nx
from mango.inter2data.utils.clean_utils import compute_hash_for_path, compute_hash_for_pair
from collections import defaultdict

def build_graph(edges):
    """
    "src_node": "bedroom",
        "dst_node": "bathroom",
        "action": "south",
        "seen_in_forward": 3,
        "seen_in_reversed": 10,
        "edge_min_step": 3,
        "seen_in_forward_answerable": 3,
        "seen_in_reversed_answerable": 10,
        "edge_min_step_answerable": 3
    """
    G = nx.MultiDiGraph()
    for edge in edges:
        G.add_edge(
            edge['src_node'], 
            edge['dst_node'], 
            action=edge['action'], 
            seen_in_forward=edge['seen_in_forward'], 
            seen_in_reversed=edge['seen_in_reversed'],
            edge_min_step=edge['edge_min_step'],
            seen_in_forward_answerable=edge['seen_in_forward_answerable'],
            seen_in_reversed_answerable=edge['seen_in_reversed_answerable'],
            edge_min_step_answerable=edge['edge_min_step_answerable'],
        )
    return G


def inter2data(map_path, new_map_path):
    """
    Args:
    inter: str, dir_path to the intermediate file
    data: str, dir_path to the data file
    """
    # make directory
    os.makedirs(new_map_path, exist_ok=True)
    # get the *.edges.json file in "map_path" directory
    edge_file_name= [f for f in os.listdir(map_path) if f.endswith('.edges.json')][0]

    # read the edge file
    with open(os.path.join(map_path, edge_file_name), 'r') as f:
        edges = json.load(f)

    # create a graph
    G = build_graph(edges)

     # generate edge list
    with open(os.path.join(new_map_path, 'edges.json'), 'w') as f:
        json.dump(edges, f,indent=4)

    # generate action list
    actions = set()
    for edge in edges:
        actions.add(edge['action'])
    actions = list(actions)
    with open(os.path.join(new_map_path, 'actions.json'), 'w') as f:
        json.dump(actions, f,indent=4)

    # generate location list
    locations = list(set(list(G.nodes)))
    with open(os.path.join(new_map_path, 'locations.json'), 'w') as f:
        json.dump(locations, f,indent=4)
        
    # get all2all
    all2all = []
    start_end_dict=defaultdict(dict)
    all2all_hash= set()
    
    all2all_file_name=[f for f in os.listdir(map_path) if f.endswith('.all2all.json')][0]
    
    with open(os.path.join(new_map_path, 'all2all.jsonl'), 'w') as fw:
        with open(os.path.join(map_path, all2all_file_name), 'rb') as fr:
             for line in fr:
                clean_line = line.strip()
                if not clean_line:  # Ensure the line is not empty
                    continue
                path=json.loads(clean_line)
                path['id'] = compute_hash_for_path(path["path_details"])
                if path['id'] in all2all_hash:
                    print(f"Duplicate path in all2all: {path['id']}")
                    continue
                all2all_hash.add(path['id'])
                

                
                path['min_step_forward'] = path['path_seen_in_forward']
                path['min_step_total'] = path['path_min_step']
                path['min_step_forward_answerable'] = path['path_seen_in_forward_answerable']
                path['min_step_total_answerable'] = path['path_min_step_answerable']
                # remove key: path_seen_in_forward,path_seen_in_forward_answerable,path_min_step,path_min_step_answerable
                path.pop('path_seen_in_forward', None)
                path.pop('path_seen_in_forward_answerable', None)
                path.pop('path_min_step', None)
                path.pop('path_min_step_answerable', None)
                
                if path['dst_node'] in start_end_dict[path['src_node']].keys():
                    start_end_dict[path['src_node']][path['dst_node']].append(path['min_step_total_answerable'])
                else:
                    start_end_dict[path['src_node']][path['dst_node']]=[path['min_step_total_answerable']]
                
                fw.write(json.dumps(path) + '\n')
    
    # get all_pairs
    all_pairs = []
    all_pairs_hash= set()
    
    
    all_pairs_file_name=[f for f in os.listdir(map_path) if f.endswith('.all_pairs.json')][0]
    
    with open(os.path.join(new_map_path, 'all_pairs.jsonl'), 'w') as fw:
        with open(os.path.join(map_path, all_pairs_file_name), 'r') as fr:
             for line in fr:
                clean_line = line.strip()
                if not clean_line:
                    continue   # Ensure the line is not empty
                pair=json.loads(clean_line)
                pair['id'] = compute_hash_for_pair(pair)
                if pair['id'] in all_pairs_hash:
                    print(f"Duplicate pair in all_pairs: {pair['id']}")
                    continue
                all_pairs_hash.add(pair['id'])
                pair['path_min_step_forward'] = pair['path_seen_in_forward']
                pair['path_min_step_forward_answerable'] = pair['path_seen_in_forward_answerable']
                pair['path_min_step_total'] = pair['path_min_steps']
                
                if pair['dst_node'] in start_end_dict[pair['src_node']]:
                    pair['path_min_step_total_answerable']=start_end_dict[pair['src_node']][pair['dst_node']]
                else:
                    pair['path_min_step_total_answerable']=[]
                
                
                pair['min_step_forward'] =min(pair['path_min_step_forward']) if len(pair['path_min_step_forward'])>0 else 9999
                pair['min_step_total'] = min(pair['path_min_step_total']) if len(pair['path_min_step_total'])>0 else 9999
                pair['min_step_forward_answerable'] = min(pair['path_min_step_forward_answerable']) if len(pair['path_min_step_forward_answerable'])>0 else 9999
                pair['min_step_total_answerable'] = min(pair['path_min_step_total_answerable']) if len(pair['path_min_step_total_answerable'])>0 else 9999
                
                pair.pop("path_min_steps", None)
                pair.pop("path_seen_in_forward", None)
                pair.pop("path_seen_in_forward_answerable", None)
                pair.pop("path_min_step_total_answerable", None)
                pair.pop("path_min_step_forward_answerable", None)
                pair.pop("path_min_step_forward", None)
                pair.pop("path_min_step_total", None)
                fw.write(json.dumps(pair) + '\n')
    """
    for pair in all_pairs:
        pair['id'] = compute_hash_for_pair(pair)
        if pair['id'] in all_pairs_hash:
            print(f"Duplicate pair in all_pairs: {pair['id']}")
        # remove key: path_seen_in_forward,path_seen_in_forward_answerable,path_min_step,path_min_step_answerable
        pair['path_min_step_forward'] = pair['path_seen_in_forward']
        pair['path_min_step_forward_answerable'] = pair['path_seen_in_forward_answerable']
        pair['path_min_step_total'] = pair['path_min_steps']
        pair['path_min_step_total_answerable'] = []
        for path in all2all:
            if path['src_node'] == pair['src_node'] and path['dst_node'] == pair['dst_node']:
                pair['path_min_step_total_answerable'].append(path['min_step_total_answerable'])
        pair.pop("path_min_steps", None)
        pair.pop("path_seen_in_forward", None)
        pair.pop("path_seen_in_forward_answerable", None)
        
        pair['min_step_forward'] =min(pair['path_min_step_forward']) if len(pair['path_min_step_forward'])>0 else 9999
        pair['min_step_total'] = min(pair['path_min_step_total']) if len(pair['path_min_step_total'])>0 else 9999
        pair['min_step_forward_answerable'] = min(pair['path_min_step_forward_answerable']) if len(pair['path_min_step_forward_answerable'])>0 else 9999
        pair['min_step_total_answerable'] = min(pair['path_min_step_total_answerable']) if len(pair['path_min_step_total_answerable'])>0 else 9999

    #save all_pairs
    with open(os.path.join(new_map_path, 'all_pairs.json'), 'w') as f:
        json.dump(all_pairs, f, indent=4)
    
    
    for path in all2all:
        path['id'] = compute_hash_for_path(path["path_details"])
        if path['id'] in all2all_hash:
            print(f"Duplicate path in all2all: {path['id']}")
        all2all_hash.add(path['id'])
        # min_step_forward = max([edge['seen_in_forward_answerable'] for edge in path['path_details']])
        # min_step_total= max([min(edge['seen_in_forward_answerable'],edge['seen_in_reversed_answerable']) for edge in path['path_details']])
        path['min_step_forward'] = path['path_seen_in_forward']
        path['min_step_total'] = path['path_min_step']
        path['min_step_forward_answerable'] = path['path_seen_in_forward_answerable']
        path['min_step_total_answerable'] = path['path_min_step_answerable']
        # remove key: path_seen_in_forward,path_seen_in_forward_answerable,path_min_step,path_min_step_answerable
        path.pop('path_seen_in_forward', None)
        path.pop('path_seen_in_forward_answerable', None)
        path.pop('path_min_step', None)
        path.pop('path_min_step_answerable', None)
    
    #save all2all
    with open(os.path.join(new_map_path, 'all2all.json'), 'w') as f:
        json.dump(all2all, f, indent=4)

    """
    print(f"Done with {map_path}")
    

if __name__ == '__main__':
    fire.Fire(inter2data) 

    
    

    
