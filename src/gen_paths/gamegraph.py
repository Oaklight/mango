import os
import sys

import matplotlib.pyplot as plt
import networkx

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from gen_paths.utils import generate_combinations, print_color

opposite_directions = {
    "east": "west",
    "west": "east",
    "north": "south",
    "south": "north",
    "up": "down",
    "down": "up",
    "northeast": "southwest",
    "southwest": "northeast",
    "northwest": "southeast",
    "southeast": "northwest",
}


def load_valid_actions(action_file):
    """
    load valid action files. Each file has two sections
    - Directions
    - Non directions
    """
    # test if action_file not exist, create an empty txt file
    try:
        with open(action_file, "r") as f:
            pass
    except FileNotFoundError:
        with open(action_file, "w") as f:
            pass

    with open(action_file, "r") as f:
        for line in f:
            line = line.strip().lower()
            if line == "direction:":
                continue
            elif line == "non direction:":
                break
            # skip empty line
            elif line == "":
                continue

            # parse non-empty lines
            print("line: ", line)
            from_dir, to_dir = [each.strip().lower() for each in line.split("--")]
            opposite_directions[from_dir] = to_dir
            opposite_directions[to_dir] = from_dir
            # TODO: see if we need to check allowed action in "non-directions"?

    print(opposite_directions)


def build_graph_from_file(
    path_file: str = "data/game.map",
    action_file: str = "data/game.actions",
    verbose: bool = True,
) -> object:
    """
    builds a graph from a csv file,
    - forward path: path (src_node --> action --> dst_node), step_num
    - backward path: path (dst_node --> opposite_action --> src_node), step_num, description
      if description is "None" this is a valid path, otherwise it's an invalid path
    """
    with open(path_file, "r") as f:
        lines = f.readlines()

    if action_file is None:
        print("No action file provided, skip reverse links.")
    else:
        load_valid_actions(action_file)
    # build graph from file

    # use MultiDiGraph instead to accomodate special game with multiple valid action between two nodes
    G = networkx.MultiDiGraph()

    edges_to_add = []
    for line in lines:
        line = line.strip("\ufeff").strip()
        print_color(line, "b", inline=True)
        if line == "":
            print("skip empty line")
            continue
        if "desc:" in line:
            print("revered path detected")
            # parse reversed path
            line, desc = [each.strip().lower() for each in line.split(", desc:")]

            if desc != "none":
                print("invalid path detected", line, desc)
                continue
        else:
            print("normal path detected")
            # path = line

        path, step_num = [each.strip().lower() for each in line.split(", step")]
        step_num = int(step_num)
        elements = [each.strip().lower() for each in path.split("-->")]
        print(elements)
        src_node, direction, dst_node = elements
        edges_to_add.append((src_node, dst_node, direction, step_num))

    # sort by step_number
    edges_to_add.sort(key=lambda x: x[3])

    prev_step_number = -1
    for src_node, dst_node, direction, step_number in edges_to_add:
        assert step_number > prev_step_number, "step_number must be increasing"
        prev_step_number = step_number

        # add edges with attributes
        # only add triplet (src, dst, direction) once, and store the minimum step_num
        if (src_node, dst_node, direction) not in [
            (u, v, data["direction"]) for u, v, data in G.edges(data=True)
        ]:
            G.add_edge(src_node, dst_node, direction=direction, step_num=step_num)
        else:
            pass

    return G


def build_graph_from_file_with_reverse(
    path_file: str = "data/game.map",
    reverse_file: str = "data/game.map.reversed",
    verbose: bool = True,
) -> object:
    """
    build map graph based on forward map (path_file) and reverse map (reverse_file)
    """
    # reverse map should have less or equal number of edges than forward map
    # each matching entry of reverse map should have the same set of nodes as its counterpart in forward map

    # load forward and reverse map file and count its number of lines
    with open(path_file, "r") as f:
        lines_forward = f.readlines()
    with open(reverse_file, "r") as f:
        lines_reverse = f.readlines()
    num_lines_forward = len(lines_forward)
    num_lines_reverse = len(lines_reverse)
    assert (
        num_lines_reverse <= num_lines_forward
    ), "reverse map should have less or equal number of edges than forward map"

    # go over each entry of both file, check if entries with matching step_num has same set of nodes
    # forward entry: West of House --> north --> North of House, step 1
    # backward entry: North of House (obj81) --> south --> West of House (obj180), step 1, desc: North of House || You are facing the north side of a white house. There is no door here, and all the windows are boarded up. To the north a narrow path winds through the trees.
    # backward entry with non-None description is an invalid path
    # i-th reverse entry must have bigger or equal step_num than i-th forward entry
    reverse_nodes = {}
    forward_nodes = {}
    for i in range(num_lines_reverse):
        # get step_num and path
        line_reverse = lines_reverse[i].strip("\ufeff").strip()
        line_reverse, skip_flag = line_reverse.split(", desc:")
        line_reverse = line_reverse.strip()
        skip_flag = skip_flag.strip()
        if skip_flag != "None":
            print("skip invalid path", line_reverse, f"[{skip_flag}]")
            continue
        if len(line_reverse) == 0:
            continue
        path_reverse, step_num_reverse = [
            each.strip().lower() for each in line_reverse.split(", step")
        ]
        step_num_reverse = int(step_num_reverse)
        # get src_node, direction, dst_node
        elements_reverse = [each.strip().lower() for each in path_reverse.split("-->")]
        print(elements_reverse)
        src_node_reverse, _, dst_node_reverse = elements_reverse
        reverse_nodes[step_num_reverse] = (src_node_reverse, dst_node_reverse)

    print("\n\n\n\n\n\n")
    for i in range(num_lines_forward):
        # get step_num and path
        line_forward = lines_forward[i].strip("\ufeff").strip()
        if len(line_forward) == 0:
            continue
        path_forward, step_num_forward = [
            each.strip().lower() for each in line_forward.split(", step")
        ]
        step_num_forward = int(step_num_forward)
        # get src_node, direction, dst_node
        elements_forward = [each.strip().lower() for each in path_forward.split("-->")]
        print(elements_forward)
        src_node_forward, _, dst_node_forward = elements_forward
        forward_nodes[step_num_forward] = (src_node_forward, dst_node_forward)

    # check if reverse map has same set of nodes as forward map
    for step_num in reverse_nodes:
        assert (
            step_num in forward_nodes
        ), "reverse map should have less or equal number of edges than forward map"
        # since namespace converted, we just need to check forward node has the same id as reverse node
        forward_id = forward_nodes[step_num][0].split("(")[-1].split(")")[0]
        assert forward_id in reverse_nodes[step_num][1], (
            f"[{step_num}] forward src_node should be in reverse dst_node",
            forward_nodes[step_num][0],
            reverse_nodes[step_num][1],
        )
        forward_id = forward_nodes[step_num][1].split("(")[-1].split(")")[0]
        assert forward_id in reverse_nodes[step_num][0], (
            f"[{step_num}] forward dst_node should be in reverse src_node",
            forward_nodes[step_num][1],
            reverse_nodes[step_num][0],
        )
        print(reverse_nodes[step_num], forward_nodes[step_num])
    # exit(-1)
    # In some cases, human map may contain more or less entries than the machine forward map.
    # reverse map is from machine forward map.
    G_forward = build_graph_from_file(path_file, action_file=None, verbose=verbose)
    G_backward = build_graph_from_file(reverse_file, action_file=None, verbose=verbose)

    # use G_forward as the base graph, add edges from G_backward
    # if and only if triplet (src, dst, direction) not in G_forward.edges(data=True)
    G = G_forward.copy()
    for edge in G_backward.edges(data=True):
        src, dst, attrs = edge
        direction = attrs["direction"]
        if (src, dst, direction) not in [
            (u, v, data["direction"]) for u, v, data in G.edges(data=True)
        ]:
            G.add_edge(src, dst, **attrs)

    setattr(G, "forward", G_forward)
    setattr(G, "backward", G_backward)

    return G


def plot_graph(g: object):
    """
    plot a graph
    """
    pos = networkx.spring_layout(g)
    networkx.draw(
        g,
        pos,
        with_labels=True,
        node_size=1000,
        node_color="skyblue",
        font_size=8,
        connectionstyle="arc3,rad=0.2",
    )

    # Get the edge labels as a dictionary
    edge_labels = {
        (u, v): f"({u}->{v})\n{d['direction']}" for u, v, d in g.edges(data=True)
    }

    # Draw the edge labels
    networkx.draw_networkx_edge_labels(
        g, pos, edge_labels=edge_labels, font_color="red", label_pos=0.75, rotate=False
    )

    plt.show(block=False)
    print("\n============ MAP READY =============\n")


def get_shortest_path(g: object, src: str, dst: str):
    """
    get shortest path from src to dst
    """
    try:
        path = networkx.shortest_path(g, src, dst)
        return path
    except networkx.exception.NetworkXNoPath:
        return []


def get_all_paths(g: object, src: str, dst: str):
    """
    get all paths from src to dst in MultiDiGraph
    then format the path to a list of quaduples (src, dst, direction, step_num)
    """
    try:
        simple_paths = networkx.all_simple_paths(g, src, dst)
        expanded_simple_paths = []

        for path in simple_paths:
            expanded_path = []
            for i in range(len(path) - 1):
                # get all variants of edges between path[i] and path[i+1]
                src = path[i]
                dst = path[i + 1]
                edges_attrs = g.get_edge_data(src, dst)
                edges_with_attrs = [
                    (src, dst, data["direction"], data["step_num"])
                    for data in edges_attrs.values()
                ]

                expanded_path = generate_combinations(expanded_path, edges_with_attrs)
        expanded_simple_paths.extend(expanded_path)

        return expanded_simple_paths
    except networkx.exception.NetworkXNoPath:
        return []


def anno_to_code(anno: str, anno2code: dict):
    """
    convert annotation to code
    anno and keys in anno2code may not be in the same case, so lower case all keys in anno2code
    """
    if anno is None:
        return None

    anno = anno.lower() if isinstance(anno, str) else str(anno)
    anno2code = {k.lower(): v for k, v in anno2code.items()}

    if anno in anno2code:
        return anno2code[anno][0]
    else:
        print(f"anno [{anno}] is not in anno2code")
        return None


PathCheck = {
    0: "ERROR: empty path",
    1: "ERROR: node not in anno2code",
    2: "ERROR: prev_node not in anno2code",
    3: "ERROR: 1st prev_node != src_node",
    4: "ERROR: node not in prev_node.neighbor()",
    5: "ERROR: edge not adjacent",
    6: "ERROR: action is not valid",
    7: "GOOD: seen",  # the 1st cheering one :) it means the edge is in the forward subgraph
    8: "GOOD: unseen",  # the 2nd cheering one :) it means the edge is in the backward subgraph
}


def walk_path_to_dst(g: object, src_anno: str, actions: list[str], anno2code: dict):
    """
    given src_annotation and actions, walk along the actions and return dst_anno
    """
    if len(actions) == 0:
        return None, "ERROR: empty action list"

    src_node = anno_to_code(src_anno, anno2code)
    if src_node is None:
        return None, "ERROR: src_anno not in anno2code"

    prev_node = src_node
    for i in range(len(actions)):
        action = actions[i]
        neighbors = list(g.neighbors(prev_node))
        pos_directions = [g[prev_node][each]["direction"] for each in neighbors]
        print(neighbors)
        print(pos_directions)
        # if action not in pos_directions then stay at the same node
        if action not in pos_directions:
            pass
        # else move to the next node
        else:
            next_node = neighbors[pos_directions.index(action)]
            prev_node = next_node

    # by now prev_node is the dst_node
    return prev_node, "GOOD: arrived"


def walk_and_label_path(g: object, src_anno: str, path: list[dict], anno2code: dict):
    """
    given src_annotation and path, walk along the path and label the path
    src_anno: annotation of src_node
    anno2code: mapping from annotation to codename list, usually len(codenames) == 1
    code2anno: mapping from codename to annotation, one to one mapping
    path: list of dict: {"prev_node", "node", "action"}
    return dst_anno, stop_step, labeled path, and path check message
    """

    if len(path) == 0:
        return None, -2, path, PathCheck[0]

    # check if src_anno is in anno2code
    src_node = anno_to_code(src_anno, anno2code)
    if src_node is None:
        return None, -1, path, PathCheck[1]

    # walk along the path

    # load first prev_node, check if it is in anno2code
    # print(path[0], type(path[0]))
    prev_node = path[0]["prev_node"]
    prev_node = anno_to_code(prev_node, anno2code)
    if prev_node is None:
        path[0]["msg"] = PathCheck[2]
        return None, 0, path, PathCheck[2]

    # check if path[0]["prev_node"] is src_node
    if prev_node != src_node:
        path[0]["msg"] = PathCheck[3]
        return None, 0, path, PathCheck[3]

    for i in range(len(path)):
        # check current line's prev_node is the same as previous line's node. If not , edges not adjacent
        if i > 0:
            if path[i]["prev_node"] != path[i - 1]["node"]:
                path[i]["msg"] = PathCheck[5]
                return prev_node, i, path, PathCheck[5]

        node = path[i]["node"]
        node = anno_to_code(node, anno2code)
        if node is None:
            path[i]["msg"] = PathCheck[1]
            return prev_node, i, path, PathCheck[1]

        # check if node is neighbor of prev_node
        if node not in g.neighbors(prev_node):
            path[i]["msg"] = PathCheck[4]
            return prev_node, i, path, PathCheck[4]

        # nodes are all good, now check if action is valid
        action = path[i]["action"]
        real_action = g[prev_node][node]["direction"]
        if action != real_action:
            path[i]["msg"] = PathCheck[6]
            return prev_node, i, path, PathCheck[6]

        # all good, check if edge is in the forward subgraph
        if g.forward.has_edge(prev_node, node):
            path[i]["msg"] = PathCheck[7]
        else:
            path[i]["msg"] = PathCheck[8]

        # update prev_node
        prev_node = node

    # done walking
    dst_node = prev_node
    # dst_anno = code2anno[dst_node]
    return dst_node, len(path), path, "all good"


def parse_path(path_file: str = "data/path2.verify"):
    """
    parse paths2verify file to a list of triplets (src_node, dst_node, direction)
    """
    with open(path_file, "r") as f:
        # first line is src_node, dst_node
        src_node, dst_node = [each.strip().lower() for each in f.readline().split(",")]
        # rest are paths2verify proposed
        lines = f.readlines()

    paths2verify = []
    for line in lines:
        line = line.strip("\ufeff")
        if line == "":
            continue
        direction = line.strip().lower()
        paths2verify.append(direction)
    return src_node, dst_node, paths2verify


def get_edge_direction(G, n1, n2):
    if G.has_edge(n1, n2):
        # Get the edge attributes
        edge_data = G.get_edge_data(n1, n2).get("direction")
        return edge_data
    else:
        print("Edge not found.")


def get_path_json(g, path, shortest_length=None):
    """
    return path json
    path is a list of quadruplets (prev_node, node, action, step_num)
    """
    # get src_node and dst_node and print them
    src_node = path[0][0]
    dst_node = path[-1][1]

    path_json = {"src_node": src_node, "dst_node": dst_node}
    if shortest_length:
        diff_shortest = len(path) - shortest_length
        path_json["diff_shortest"] = diff_shortest

    path_details = []
    if len(path) == 0:
        pass
    else:
        for edge in path:
            prev_node, node, direction, step_num = edge
            if (prev_node, node, direction) in [
                (u, v, data["direction"]) for u, v, data in g.forward.edges(data=True)
            ]:
                seen = True
            else:
                seen = False

            # use dict instead
            entry = {
                "prev_node": prev_node,
                "node": node,
                "action": direction,
                "seen_in_forward": seen,
                "step_min_cutoff": step_num,
            }
            path_details.append(entry)
            prev_node = node
    path_json["path_details"] = path_details
    path_json["step_count"] = len(path_details)
    path_json["path_min_cutoff"] = max(
        [each["step_min_cutoff"] for each in path_details]
    )
    path_json["all_steps_seen_in_forward"] = all(
        [each["seen_in_forward"] for each in path_details]
    )

    return path_json


def get_all_paths_json(g, all_paths, diff_shortest=False):
    """
    iterate over all paths and print each
    all_paths is the expanded simple paths. Outter most list the collection of simple paths. Inner lists are lists of edge quadruplets (src_node, dst_node, direction, step_num)
    """
    path_json_list = []
    if len(all_paths) == 0:
        print("no path found")
        return path_json_list

    # sort all_paths by len of each
    all_paths.sort(key=lambda x: len(x))
    shortest_len = len(all_paths[0])

    for path in all_paths:
        if diff_shortest:
            path_json = get_path_json(g, path, shortest_length=shortest_len)
        else:
            path_json = get_path_json(g, path)
        path_json_list.append(path_json)

    return path_json_list


if __name__ == "__main__":
    g = build_graph_from_file("../data/zork1.map", "../data/zork1.actions")
    plot_graph(g)

    while True:
        # prompt for src_node and dst_node, check if they exist in graph first
        while True:
            print("\033[92mWhere are you from? \033[0m")
            src_node = input().strip().lower()
            # check if src_node exist in graph
            if src_node not in g.nodes:
                print(f"[{src_node}] is not a valid location.")
                continue
            break

        while True:
            print("\033[92mWhere are you going? \033[0m")
            dst_node = input().strip().lower()
            # check if dst_node exist in graph
            if dst_node not in g.nodes:
                print(f"[{dst_node}] is not a valid location.")
                continue
            break

        # shortest path test
        shortestPath = get_shortest_path(g, src=src_node, dst=dst_node)
        # print_path(g, shortestPath)

        # all path test
        allPaths = get_all_paths(g, src=src_node, dst=dst_node)
        # print_all_paths(g, allPaths)
