from digraph import build_graph_from_file, plot_graph, get_shortest_path, print_path

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