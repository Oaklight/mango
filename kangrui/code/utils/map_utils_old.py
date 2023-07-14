import os
import os.path as osp
import networkx as nx
import matplotlib.pyplot as plt
import json
import hashlib
import shutil
import subprocess

# build graph for game 
# used for data-intermediate

def get_edge(file_path)->list:
    # load edge from .human or .reversed
    edges = []

    with open(file_path, 'r') as file:
        for line in file:
            
            line_components = line.strip().split('-->')
            start_node=line_components[0].strip()
            action=line_components[1].strip()
            
            end_node,left=line_components[2].strip().split(', step ')
            
            if ", desc: " in left:# reverse
                left.strip().split(", desc: ")
                step,desc=left.strip().split(", desc: ")
                step=step.strip()
                if "None" in desc:
                    desc='reverse'
                else:
                    continue
            else:
                step=left.strip()
                desc='forward'
            

            # build the edge dict and add it to the list
            edge = {
                'start_node': start_node,
                'action': action,
                'end_node': end_node,
                'step_min_cutoff': int(step),
                'desc': desc,
            }

            edges.append(edge)

    return edges

def build_graph(edges):
    G = nx.MultiDiGraph()
    for edge in edges:
        G.add_edge(edge['start_node'], edge['end_node'], action=edge['action'], step_min_cutoff=edge['step_min_cutoff'], desc=edge['desc'])
    return G

def add_edges_to_graph(G, edges):
    for edge in edges:
        src=edge['start_node']
        dest=edge['end_node']
        action_=edge['action']
        if G.has_edge(src, dest) and action_ in set(value['action'] for value in G[src][dest].values()):
            continue     
        G.add_edge(src, dest, action=action_, step_min_cutoff=edge['step_min_cutoff'], desc=edge['desc'])        
    return G

def prune_edges(G):
    # Create a new MultiDiGraph to store the pruned edges
    pruned_G = nx.MultiDiGraph()

    # Iterate over all edges
    for src, dest, data in G.edges(data=True):
        # If the pruned graph already contains an edge between src and dest with the same action
        if pruned_G.has_edge(src, dest) and 'action' in data:
            update_edge=False
            for edge_key, edge_data in pruned_G[src][dest].items():
                if edge_data.get('action') == data['action']:
                    # If the current edge's step_min_cutoff is less than the existing edge's, replace it
                    if data['step_min_cutoff'] < edge_data['step_min_cutoff']:
                        pruned_G[src][dest][edge_key]['step_min_cutoff'] = data['step_min_cutoff']
                    update_edge=True
                    break
            if update_edge:
                continue
        pruned_G.add_edge(src, dest, **data)

    return pruned_G


def build_graph_from_edges(forward_edge,reverse_edge):
    G=build_graph(forward_edge)
    G=prune_edges(G)
    add_edges_to_graph(G, reverse_edge)
    return prune_edges(G)

def all_simple_paths_with_edge_attributes(G, source, target):
    # This function will store the paths
    def dfs_path(G, source, target, visited, path):
        # Mark the node as visited
        visited.add(source)

        # If this is the target, add the path to paths
        if source == target:
            paths.append(list(path))
        else:
            # Recurse for all the neighbors
            for neighbor in G[source]:
                # If the neighbor is not visited
                if neighbor not in visited:
                    # Recurse over the edges
                    edge_data = G[source][neighbor]
                    for key in edge_data:
                        # Get all edge attributes
                        data = edge_data[key]
                        # Add triplet to the path
                        path.append((source, neighbor, data))
                        dfs_path(G, neighbor, target, visited, path)
                        # Remove triplet from the path
                        path.pop()

        # Mark node as unvisited
        visited.remove(source)

    paths = []
    visited = set()
    dfs_path(G, source, target, visited, [])

    return paths

def find_all_paths(G):
    all_paths = []
    for start_node in G.nodes:
        for end_node in G.nodes:
            if start_node != end_node:
                for path in all_simple_paths_with_edge_attributes(G, start_node, end_node):
                    all_paths.append(path)
    all_path_new=[]
    for path in all_paths:
        new_path=[]
        for edge in path:
            new_edge={'prev_node': edge[0], 
                      'node': edge[1], 
                      'action': edge[2]['action'], 
                      'seen_in_forward': edge[2]['seen_in_forward'], 
                      'step_min_cutoff': edge[2]['step_min_cutoff']}
            new_path.append(new_edge)
        all_path_new.append(new_path)
    return all_path_new

def show_graph_info(G):
    plt.figure(figsize=(30, 30))
    nx.draw(G, with_labels=True, node_size=3000, node_color="skyblue", font_size=25)
    plt.show()
    all_paths=find_all_paths(G)
    print("Number of nodes:", G.number_of_nodes())
    print("Number of edges:", G.number_of_edges())
    print("Number of paths:", len(all_paths))
    print("Strongly connected components:", list(nx.strongly_connected_components(G)))
    
    print(len(list(nx.strongly_connected_components(G))))
    
def build_graph_for_game(map_dir,game_name):
    human_path=osp.join(map_dir,game_name,f'{game_name}.map.human')
    reversed_path=osp.join(map_dir,game_name,f'{game_name}.map.reversed')
    human_edge=get_edge(human_path)
    reversed_edge=get_edge(reversed_path)
    G=build_graph_from_edges(human_edge,reversed_edge)
    return G

def get_game_info(map_dir,game_name):
    all2all_path=osp.join(map_dir,game_name,f'{game_name}.all2all.json')
    all_pairs_path=osp.join(map_dir,game_name,f'{game_name}.all_pairs.json')
    anno2code_path=osp.join(map_dir,game_name,f'{game_name}.anno2code.json')
    code2anno_path=osp.join(map_dir,game_name,f'{game_name}.code2anno.json')
    
    with open(all2all_path,'r') as f:
        all2all = json.load(f)
    with open(all_pairs_path,'r') as f:
        all_pairs= json.load(f)
    with open(anno2code_path,'r') as f:
         anno2code= json.load(f)
    with open(code2anno_path,'r') as f:
        code2anno= json.load(f)
    G=build_graph_for_game(map_dir,game_name)


    human_path=osp.join(map_dir,game_name,f'{game_name}.map.human')
    forward_edges=get_edge(human_path)
    forward_edge_dict={}
    for edge in forward_edges:
        forward_edge_dict[(edge['start_node'],edge['end_node'],edge['action'])]=edge['desc']

    for edge in G.edges(data=True):
        key=(edge[0],edge[1],edge[2]['action'])
        if key in forward_edge_dict.keys():
            edge[2]['desc']=forward_edge_dict[key]
    
    return G,all2all,all_pairs,anno2code,code2anno