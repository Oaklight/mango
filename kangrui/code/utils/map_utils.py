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
                'step': int(step),
                'desc': desc,
            }

            edges.append(edge)

    return edges

def build_graph(edges):
    G = nx.DiGraph()
    for edge in edges:
        G.add_edge(edge['start_node'], edge['end_node'], action=edge['action'], step=edge['step'], desc=edge['desc'])
    return G

def add_edges_to_graph(G, edges):
    for edge in edges:
        G.add_edge(edge['start_node'], edge['end_node'], action=edge['action'], step=edge['step'], desc=edge['desc'])
    return G

def build_graph_from_edges(forward_edge,reverse_edge):
    G=build_graph(forward_edge)
    add_edges_to_graph(G, reverse_edge)
    return G

def find_all_paths(G):
    all_paths = []
    for start_node in G.nodes:
        for end_node in G.nodes:
            if start_node != end_node:
                for path in nx.all_simple_paths(G, start_node, end_node):
                    all_paths.append(path)
    return all_paths

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
        forward_edge_dict[(edge['start_node'],edge['end_node'])]=edge['desc']

    for edge in G.edges(data=True):
        key=(edge[0],edge[1])
        if key in forward_edge_dict.keys():
            edge[2]['desc']=forward_edge_dict[key]
    
    return G,all2all,all_pairs,anno2code,code2anno