from digraph import build_graph_from_file, plot_graph, verify_path, parse_path

g = build_graph_from_file('../data/Zork_Locations.txt',
                          '../data/Zork_opposite_directions.txt')
plot_graph(g)

# verify path test
srcNode, dstNode, paths2verify = parse_path("../data/Zork_paths2verify.txt")
result = verify_path(g, srcNode, dstNode, paths2verify)
print(f"VERIFIED RESULT: \033[1m{result}\033[0m")