import os.path as osp
import networkx as nx
import json


def get_game_info(map_dir:str,game_name:str):
    all2all_path=osp.join(map_dir,game_name,f'{game_name}.all2all.jsonl')
    all_pairs_path=osp.join(map_dir,game_name,f'{game_name}.all_pairs.jsonl')
    edges_path=osp.join(map_dir,game_name,f'{game_name}.edges.json')
    actions_path=osp.join(map_dir,game_name,f'{game_name}.actions.json')
    locations_path=osp.join(map_dir,game_name,f'{game_name}.locations.json')
    walkthrough_path=osp.join(map_dir,game_name,f'{game_name}.walkthrough')
    all2all={}
    with open(all2all_path,'r') as f:
        for line in f:
            data=json.loads(line)
            all2all[data['id']]=data
    all_pairs={}
    with open(all_pairs_path,'r') as f:
         for line in f:
            data=json.loads(line)
            all_pairs[data['id']]=data
    with open(edges_path,'r') as f:
        edges= json.load(f)
    with open(actions_path,'r') as f:
        actions= json.load(f)
    with open(locations_path,'r') as f:
        locations= json.load(f)
    with open(walkthrough_path,'r') as f:
        walkthrough= f.read()

    G = nx.MultiDiGraph()
    for edge in edges:
        G.add_edge(edge['src_node'], edge['dst_node'], action=edge['action'], 
                   edge_min_step_answerable=edge["edge_min_step_answerable"],seen_in_forward_answerable=['seen_in_forward_answerable'])

    return G,all2all,all_pairs,actions,locations,walkthrough

def get_game_info_with_G_eval(map_dir:str,game_name:str):
    reverse_dict = {
    "up": "down",
    "down": "up",
    "north": "south",
    "south": "north",
    "east": "west",
    "west": "east",
    "northeast": "southwest",
    "northwest": "southeast",
    "southeast": "northwest",
    "southwest": "northeast"
}
    G,all2all,all_pairs,actions,locations,walkthrough=get_game_info(map_dir,game_name)
    G_eval = nx.MultiDiGraph()
    for (u, v, data) in G.edges(data=True):
        G_eval.add_edge(u, v, **data)
    for (u, v, data) in G.edges(data=True):
        # If the 'action' attribute of the edge is in reverse_direction_dict
        action_=data.get('action')
        if action_ in reverse_dict.keys():
            # Add an edge in the reverse direction in G_reverse
            reverse_action=reverse_dict[action_]
            if G_eval.has_edge(v, u) and reverse_action in set(value['action'] for value in G_eval[v][u].values()):
                continue
            G_eval.add_edge(v, u, action=reverse_action)
    return G_eval,G,actions,locations,all2all,all_pairs,walkthrough