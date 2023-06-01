import networkx
import openai
import time
import matplotlib.pyplot as plt
from config import *
from utils import print_color

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


def intuitive_reverse_map(
    path_file: str = "data/game.map", action_file: str = "data/game.actions"
):
    """
    build a reverse map from a txt file, each line is in format "from,to"
    """
    with open(path_file, "r") as f:
        lines = f.readlines()
        # lines.reverse()

    load_valid_actions(action_file)
    # build graph from file

    reverse_map_list = []

    # from last step walk intuitively back to the first step
    for line in lines:
        line = line.strip("\ufeff")
        if line == "":
            continue
        elements = [each.strip().lower() for each in line.split("-->")]
        # print(elements)
        src_node, direction, dst_node = elements
        if direction not in opposite_directions:
            print(
                f"direction [{direction}] not in opposite_directions, skip reverse path"
            )
            reverse_map_list.append("")
            continue
        reverse_step = (
            f"{dst_node} --> {get_opposite_direction(direction)} --> {src_node}"
        )
        reverse_map_list.append(reverse_step)

    # dump list to file line by line
    with open(path_file + ".reversed", "w") as f:
        for line in reverse_map_list:
            f.write(line + "\n")


def query_chatgpt(prompt, message):
    if message == "":
        query_messages = [{"role": "user", "content": prompt}]
    else:
        query_messages = [
            {"role": "system", "content": message},
            {"role": "user", "content": prompt},
        ]
    while True:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=query_messages,
            )
            break
        except Exception as e:
            print(e)
            print("Retry in 10 seconds")
            time.sleep(10)

    text = response["choices"][0]["message"]["content"]
    return text.strip()


def get_opposite_direction(direction: str):
    """
    check if direction is in the cache, if not query gpt-3.5-turbo for result and cache it
    """
    direction = direction.lower().strip()
    if direction not in opposite_directions:
        message = "answer opposite direction of given '{input_phrase}' without reasoning. If it's not a direction, return 'no clue'."
        opposite = query_chatgpt(direction, message).lower()
        # remove sentence ending punctuation
        if opposite[-1] in [".", "?", "!"]:
            opposite = opposite[:-1]
        # cache both way
        if opposite == "no clue":
            opposite = direction
            print(
                f"no clue for direction: [{direction}]. It might be some special action."
            )
        opposite_directions[direction] = opposite
        opposite_directions[opposite] = direction
    print(f"opposite direction of [{direction}] is [{opposite_directions[direction]}]")
    return opposite_directions[direction]


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

    G = networkx.DiGraph()

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
        G.add_edge(src_node, dst_node, direction=direction)

        if direction not in opposite_directions:
            if verbose:
                print(
                    f"direction [{direction}] not in opposite_directions, skip reverse path"
                )
            continue
        G.add_edge(dst_node, src_node, direction=get_opposite_direction(direction))

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
        if skip_flag != "None":
            print("skip invalid path", line_reverse)
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

    G = networkx.compose(G_forward, G_backward)
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
    get all paths from src to dst
    """
    try:
        paths = networkx.all_simple_paths(g, src, dst)
        return list(paths)
    except networkx.exception.NetworkXNoPath:
        return []


def anno_to_code(anno: str, anno2code: dict):
    """
    convert annotation to code
    anno and keys in anno2code may not be in the same case, so lower case all keys in anno2code
    """
    anno = anno.lower()
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


def verify_path(g: object, src_node, dst_node, paths2verify: list):
    """
    given src_node and dst_node, verify if the paths2verify is valid
    paths2verify is a list of `direction`
    """
    # empty path: false
    if len(paths2verify) == 0:
        print("empty path")
        return False
    if src_node == dst_node:
        print("src_node == dst_node, ONLY CHECK DIFFERENT NODES")
        return False

    # TODO: check each step is a valid step
    print(
        "CHECK FROM \033[1m["
        + src_node
        + "]\033[0m TO \033[1m["
        + dst_node
        + "]\033[0m"
    )

    via_list = [src_node]
    node = src_node
    # iterate over neighbors of node, check if edge direction is correct
    for i in range(len(paths2verify)):
        neighbors = list(g.neighbors(node))
        node_neighbor_edge_directions = [
            get_edge_direction(g, node, each) for each in neighbors
        ]
        # print(node_neighbor_edge_directions)
        check_edge_directions = [
            same_direction_test(paths2verify[i], each)
            for each in node_neighbor_edge_directions
        ]
        # assert at least 1 True instance
        if not any(check_edge_directions):
            print(
                "edge direction not correct ",
                node,
                paths2verify[i],
                check_edge_directions,
            )
            return False
        else:
            assert check_edge_directions.count(True) == 1, (
                f"more than 1 edge direction is correct, MAP ERROR [{src_node}] --> [{dst_node}], via {node}, go {paths2verify[i]}",
                neighbors,
                node_neighbor_edge_directions,
                check_edge_directions,
            )
            node = neighbors[check_edge_directions.index(True)]
            via_list.append(node)
    # check if the last node is dst_node
    if node != dst_node:
        print("not end with dst_node ", dst_node, node)
        return False

    return True


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


def same_direction_test(given_direction: str, proposed_direction: str):
    """
    check if given direction is the same as correct direction
    """
    # strip and lower
    # print(given_direction, proposed_direction)
    given_direction = given_direction.strip().lower()
    proposed_direction = proposed_direction.strip().lower()

    # exact match or gpt similar test
    if given_direction == proposed_direction:
        return True
    return False


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
    """
    # get src_node and dst_node and print them
    src_node = path[0]
    dst_node = path[-1]

    path_json = {"src_node": src_node, "dst_node": dst_node}
    if shortest_length:
        diff_shortest = len(path) - shortest_length
        path_json["diff_shortest"] = diff_shortest

    prev_node = path[0]
    path_details = []
    if len(path) == 1:
        pass
    else:
        for node in path[1:]:
            seen = g.forward.has_edge(prev_node, node)
            direction = get_edge_direction(g, prev_node, node)
            # path_details.append((prev_node, node, direction, seen))
            # use dict instead
            path_details.append(
                {
                    "prev_node": prev_node,
                    "node": node,
                    "action": direction,
                    "seen": seen,
                }
            )
            prev_node = node
    path_json["path_details"] = path_details
    path_json["step_count"] = len(path_details)

    return path_json


def get_all_paths_json(g, all_paths, diff_shortest=False):
    """
    iterate over all paths and print each
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

        # verify path test
        src_node, dst_node, paths2verify = parse_path("../data/zork1.verify")
        result = verify_path(g, src_node, dst_node, paths2verify)
        print(f"VERIFIED RESULT: \033[1m{result}\033[0m")
