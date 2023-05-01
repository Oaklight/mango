import argparse
import json


if __name__ == "__main__":
    # argparse to read in game.all2all.json and game.anno2code.json and game.code2anno.json
    parser = argparse.ArgumentParser()
    parser.add_argument("paths_file", type=str, help="path to game.all2all.json")
    parser.add_argument("anno2code_json", type=str, help="path to game.anno2code.json")
    parser.add_argument("code2anno_json", type=str, help="path to game.code2anno.json")
    args = parser.parse_args()

    # read in each file
    with open(args.paths_file, "r") as f:
        paths = json.load(f)
    with open(args.anno2code_json, "r") as f:
        anno2code = json.load(f)
    with open(args.code2anno_json, "r") as f:
        code2anno = json.load(f)

    # check each path in paths, if either of its src_node or dst_node has siblings with the same annotation, then it is not unique
    # how do we know if a node has siblings? check if anno2code[anno] has more than one element
    # TODO maybe we need to check if path is shortest path? if not, technically it is not unique
    for path in paths:
        src, dst = path["src_node"], path["dst_node"]
        src_anno, dst_anno = code2anno[src], code2anno[dst]
        if len(anno2code[src_anno]) > 1 or len(anno2code[dst_anno]) > 1:
            path["unique"] = False
        else:
            path["unique"] = True

    # write back to file
    with open(args.paths_file, "w") as f:
        json.dump(paths, f, indent=4)
