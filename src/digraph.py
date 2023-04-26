import networkx
import openai
import time
import matplotlib.pyplot as plt
from config import *

opposite_directions = {}


def load_valid_actions(actionFile):
    '''
    load valid action files. Each file has two sections
    - Directions
    - Non directions
    '''
    # test if actionFile not exist, create an empty txt file
    try:
        with open(actionFile, 'r') as f:
            pass
    except FileNotFoundError:
        with open(actionFile, 'w') as f:
            pass

    with open(actionFile, 'r') as f:
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
            fromDir, toDir = [
                each.strip().lower() for each in line.split('--')
            ]
            opposite_directions[fromDir] = toDir
            opposite_directions[toDir] = fromDir
                # TODO: see if we need to check allowed action in "non-directions"?

    print(opposite_directions)


def load_opposite_direcions(directionFile):
    '''
    load cached opposite direction files in case useful 
    '''
    # test if directionFile not exist, create an empty txt file
    try:
        with open(directionFile, 'r') as f:
            pass
    except FileNotFoundError:
        with open(directionFile, 'w') as f:
            pass

    # each line is in format "direction -- opposite"
    with open(directionFile, 'r') as f:
        for line in f:
            line = line.strip()
            fromDir, toDir = [
                each.strip().lower() for each in line.split('-->')
            ]
            opposite_directions[fromDir] = toDir
            opposite_directions[toDir] = fromDir
    return opposite_directions


def query_chatgpt(prompt, message):
    if message == "":
        query_messages = [{"role": "user", "content": prompt}]
    else:
        query_messages = [
            {
                "role": "system",
                "content": message
            },
            {
                "role": "user",
                "content": prompt
            },
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
    '''
    check if direction is in the cache, if not query gpt-3.5-turbo for result and cache it
    '''
    direction = direction.lower()
    if direction not in opposite_directions:
        message = "answer opposite direction of given '{input_phrase}' without reasoning. If it's not a direction, return 'no clue'."
        opposite = query_chatgpt(direction, message).lower()
        # remove sentence ending punctuation
        if opposite[-1] in ['.', '?', '!']:
            opposite = opposite[:-1]
        # cache both way
        if opposite == 'no clue':
            opposite = direction
            print(
                f'no clue for direction: [{direction}]. It might be some special action.'
            )
        opposite_directions[direction] = opposite
        opposite_directions[opposite] = direction
    print(
        f'opposite direction of [{direction}] is [{opposite_directions[direction]}]'
    )
    return opposite_directions[direction]


def build_graph_from_file(pathFile: str = "data/gameName.map",
                          actionFile: str = "data/gameName.actions",
                          verbose: bool = True) -> object:
    '''
    builds a graph from a txt file, each line is in format "from,to"
    '''
    with open(pathFile, 'r') as f:
        lines = f.readlines()

    load_valid_actions(actionFile)
    # build graph from file

    G = networkx.DiGraph()

    for line in lines:
        line = line.strip('\ufeff')
        if line == "":
            continue
        elements = [each.strip().lower() for each in line.split("-->")]
        print(elements)
        srcNode, direction, dstNode = elements
        G.add_edge(srcNode, dstNode, direction=direction)

        # TODO: drop reverse path if direction is not from valid direction list
        if direction not in opposite_directions:
            if verbose:
                print(
                    f"direction [{direction}] not in opposite_directions, skip reverse path"
                )
            continue
        G.add_edge(dstNode,
                   srcNode,
                   direction=get_opposite_direction(direction))

    # # persist oposite directions as txt
    # with open(oppositeFile, "w") as f:
    #     for key, value in opposite_directions.items():
    #         f.write(key + " --> " + value + "\n")
    return G


def plot_graph(g: object):
    '''
    plot a graph
    '''
    pos = networkx.spring_layout(g)
    networkx.draw(g,
                  pos,
                  with_labels=True,
                  node_size=1000,
                  node_color='skyblue',
                  font_size=8,
                  connectionstyle='arc3,rad=0.2')

    # Get the edge labels as a dictionary
    edge_labels = {(u, v): f"({u}->{v})\n{d['direction']}"
                   for u, v, d in g.edges(data=True)}

    # Draw the edge labels
    networkx.draw_networkx_edge_labels(g,
                                       pos,
                                       edge_labels=edge_labels,
                                       font_color='red',
                                       label_pos=0.75,
                                       rotate=False)

    plt.show(block=False)
    print("\n============ MAP READY =============\n")


def get_shortest_path(g: object, src: str, dst: str):
    '''
    get shortest path from src to dst
    '''
    try:
        path = networkx.shortest_path(g, src, dst)
        return path
    except networkx.exception.NetworkXNoPath:
        return []


def get_all_paths(g: object, src: str, dst: str):
    '''
    get all paths from src to dst
    '''
    try:
        paths = networkx.all_simple_paths(g, src, dst)
        return list(paths)
    except networkx.exception.NetworkXNoPath:
        return []


def verify_path(g: object, srcNode, dstNode, paths2verify: list):
    '''
    given srcNode and dstNode, verify if the paths2verify is valid
    paths2verify is a list of `direction`
    '''
    # empty path: false
    if len(paths2verify) == 0:
        print("empty path")
        return False
    if srcNode == dstNode:
        print("srcNode == dstNode, ONLY CHECK DIFFERENT NODES")
        return False

    # TODO: check each step is a valid step
    print("CHECK FROM \033[1m[" + srcNode + "]\033[0m TO \033[1m[" + dstNode +
          "]\033[0m")

    via_list = [srcNode]
    node = srcNode
    # iterate over neighbors of node, check if edge direction is correct
    for i in range(len(paths2verify)):
        neighbors = list(g.neighbors(node))
        check_edge_directions = [
            same_direction_test(paths2verify[i],
                                get_edge_direction(g, node, each))
            for each in neighbors
        ]
        # assert at least 1 True instance
        if not any(check_edge_directions):
            print("edge direction not correct ", node, paths2verify[i],
                  check_edge_directions)
            return False
        else:
            assert check_edge_directions.count(
                True) == 1, "more than 1 edge direction is correct, MAP ERROR"
            node = neighbors[check_edge_directions.index(True)]
            via_list.append(node)
    # check if the last node is dstNode
    if node != dstNode:
        print("not end with dstNode ", dstNode, node)
        return False

    print_path(g, via_list)
    return True


def parse_path(pathFile: str = "data/path2.verify"):
    '''
    parse paths2verify file to a list of triplets (srcNode, dstNode, direction)
    '''
    with open(pathFile, 'r') as f:
        # first line is srcNode, dstNode
        srcNode, dstNode = [
            each.strip().lower() for each in f.readline().split(",")
        ]
        # rest are paths2verify proposed
        lines = f.readlines()

    paths2verify = []
    for line in lines:
        line = line.strip('\ufeff')
        if line == "":
            continue
        direction = line.strip().lower()
        paths2verify.append(direction)
    return srcNode, dstNode, paths2verify


def same_direction_test(given_direction: str, proposed_direction: str):
    '''
    check if given direction is the same as correct direction
    '''
    # strip and lower
    given_direction = given_direction.strip().lower()
    proposed_direction = proposed_direction.strip().lower()

    # exact match or gpt similar test
    if given_direction == proposed_direction:
        return True
    return False


def get_edge_direction(G, n1, n2):
    if G.has_edge(n1, n2):
        # Get the edge attributes
        edge_data = G.get_edge_data(n1, n2).get('direction')
        return edge_data
    else:
        print("Edge not found.")


def print_path(g: object, path: list, verbose: bool = True):
    '''
    print the path (list of nodes) with detailed direction
    '''
    # get srcNode and dstNode and print them
    srcNode = path[0]
    dstNode = path[-1]
    print(f'# {srcNode} --> {dstNode}')

    prevNode = path[0]
    path_details = []
    if len(path) == 1:
        if verbose:
            print(f'ARRIVE_AT: \033[1m[{prevNode}]\033[0m.')
    else:
        for node in path[1:]:
            direction = get_edge_direction(g, prevNode, node)
            if verbose:
                current_step = ("START_FROM \033[1m[" + prevNode +
                                "]\033[0m, DO \033[1m(" + direction +
                                ")\033[0m, ARRIVE_AT \033[1m[" + node +
                                "]\033[0m")
            else:
                current_step = direction
            path_details.append(current_step)
            prevNode = node
    path_string = "\n".join(path_details) + "\n"
    print(path_string)


def print_all_paths(g: object, all_paths: list, verbose: bool = True):
    '''
    iterate over all paths and print each
    '''
    if verbose:
        print(f"FOUND \033[1m{len(all_paths)}\033[0m PATHS\n")
    # sort all_paths by len of each
    all_paths.sort(key=lambda x: len(x))
    for path in all_paths:
        if verbose:
            print(f"LENGTH OF CURRENT PATH: \033[1m{len(path)}\033[0m")
        print_path(g, path, verbose=verbose)


if __name__ == "__main__":
    g = build_graph_from_file('../data/zork1.map',
                              '../data/zork1.actions')
    plot_graph(g)

    while True:

        # prompt for srcNode and dstNode, check if they exist in graph first
        while True:
            print("\033[92mWhere are you from? \033[0m")
            srcNode = input().strip().lower()
            # check if srcNode exist in graph
            if srcNode not in g.nodes:
                print(f'[{srcNode}] is not a valid location.')
                continue
            break

        while True:
            print("\033[92mWhere are you going? \033[0m")
            dstNode = input().strip().lower()
            # check if dstNode exist in graph
            if dstNode not in g.nodes:
                print(f'[{dstNode}] is not a valid location.')
                continue
            break

        # shortest path test
        shortestPath = get_shortest_path(g, src=srcNode, dst=dstNode)
        print_path(g, shortestPath)

        # all path test
        allPaths = get_all_paths(g, src=srcNode, dst=dstNode)
        print_all_paths(g, allPaths)

        # verify path test
        srcNode, dstNode, paths2verify = parse_path(
            "../data/zork1.verify")
        result = verify_path(g, srcNode, dstNode, paths2verify)
        print(f"VERIFIED RESULT: \033[1m{result}\033[0m")
