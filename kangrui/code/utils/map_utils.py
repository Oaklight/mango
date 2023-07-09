import os
import os.path as osp
import networkx as nx
import json
import matplotlib.pyplot as plt



def get_game_info(map_dir,game_name):
    all2all_path=osp.join(map_dir,game_name,f'{game_name}.all2all.json')
    all_pairs_path=osp.join(map_dir,game_name,f'{game_name}.all_pairs.json')
    edges_path=osp.join(map_dir,game_name,f'{game_name}.edges.json')
    actions_path=osp.join(map_dir,game_name,f'{game_name}.actions.json')
    locations_path=osp.join(map_dir,game_name,f'{game_name}.locations.json')
    walkthrough_path=osp.join(map_dir,game_name,f'{game_name}.walkthrough')
    
    with open(all2all_path,'r') as f:
        all2all = json.load(f)
    with open(all_pairs_path,'r') as f:
        all_pairs= json.load(f)
    with open(edges_path,'r') as f:
        edges= json.load(f)
    with open(actions_path,'r') as f:
        actions= json.load(f)
    with open(locations_path,'r') as f:
        locations= json.load(f)
    with open(walkthrough_path, 'r') as file:
        walkthrough = file.read()


    G = nx.MultiDiGraph()
    for edge in edges:
        G.add_edge(edge['prev_node'], edge['node'], action=edge['action'], step_min_cutoff=edge["step_min_cutoff"], seen_in_forward=edge["seen_in_forward"])

    return G,actions,locations,all2all,all_pairs,walkthrough

def get_game_info_with_G_eval(map_dir,game_name):
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
    G,actions,locations,all2all,all_pairs,walkthrough=get_game_info(map_dir,game_name)
    G_eval = nx.MultiDiGraph()
    for (u, v, data) in G.edges(data=True):
        # If the 'action' attribute of the edge is in reverse_direction_dict
        if data.get('action') in reverse_dict:
            # Add an edge in the reverse direction in G_reverse
            if G.has_edge(v, u) and G.edges[v, u]['action'] == reverse_dict[data['action']]:
                continue
            G_eval.add_edge(v, u, action=reverse_dict[data['action']])
    for (u, v, data) in G.edges(data=True):
        G_eval.add_edge(u, v, **data)
    return G_eval,G,actions,locations,all2all,all_pairs,walkthrough
    

    


def find_all_paths(G):
    all_paths = []
    for start_node in G.nodes:
        for end_node in G.nodes:
            if start_node != end_node:
                for path in nx.all_simple_paths(G, start_node, end_node):
                    all_paths.append(path)
    return all_paths

def show_graph_info(G):
    plt.figure(figsize=(20, 20))
    nx.draw(G, with_labels=True, node_size=3000, node_color="skyblue", font_size=25)
    plt.show()
    all_paths=find_all_paths(G)
    print("Number of nodes:", G.number_of_nodes())
    print("Number of edges:", G.number_of_edges())
    print("Number of paths:", len(all_paths))
    print("Strongly connected components:", list(nx.strongly_connected_components(G)))
    
    print(len(list(nx.strongly_connected_components(G))))
    
    
    