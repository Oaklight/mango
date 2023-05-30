# read in game.map.human and game.map.reversed
# read in game.anno2code.json and game.code2anno.json

import argparse
import os
import json


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


def code_to_annos(code: str, code2anno: dict):
    """
    convert code to annotation
    code and keys in code2anno may not be in the same case, so lower case all keys in code2anno
    """
    code = code.lower()
    code2anno = {k.lower(): v for k, v in code2anno.items()}

    if code in code2anno:
        return code2anno[code]
    else:
        print(f"code [{code}] is not in code2anno")
        return None


if __name__ == "__main__":
    # argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path", "-p", type=str, required=True, help="path to all game maps"
    )
    parser.add_argument("--game", "-g", type=str, required=True, help="game name")
    args = parser.parse_args()

    # assert game is a subfolder under path
    assert os.path.isdir(
        os.path.join(args.path, args.game)
    ), f"{args.game} is not available under {args.path}"
    args.output_dir = os.path.join(args.path, args.game)

    map_human_path = os.path.join(args.output_dir, f"{args.game}.map.human")
    map_reversed_path = os.path.join(args.output_dir, f"{args.game}.map.reversed")
    anno2code_path = os.path.join(args.output_dir, f"{args.game}.anno2code.json")
    code2anno_path = os.path.join(args.output_dir, f"{args.game}.code2anno.json")

    # assert all files exist
    assert os.path.isfile(map_human_path), f"{map_human_path} does not exist"
    assert os.path.isfile(map_reversed_path), f"{map_reversed_path} does not exist"
    assert os.path.isfile(anno2code_path), f"{anno2code_path} does not exist"
    assert os.path.isfile(code2anno_path), f"{code2anno_path} does not exist"

    # load json mapping
    with open(anno2code_path, "r") as f:
        anno2code = json.load(f)
        # anno2code is key: [value1, value2, ...]
    with open(code2anno_path, "r") as f:
        code2anno = json.load(f)
        # code2anno is key: value

    # lower and strip all key and values in anno2code and code2anno
    anno2code = {
        k.lower().strip(): [v.lower().strip() for v in v_list]
        for k, v_list in anno2code.items()
    }
    code2anno = {k.lower().strip(): v.lower().strip() for k, v in code2anno.items()}

    # iterate over map.human and map.reversed, parse each line and replace anno with code
    # human: Endless Stair --> south --> Junction, step 2
    # reversed: Junction (obj63) --> north --> Endless Stair (obj64), step 2, desc: None

    # perform node merge using code from anno2code
    # by replacing all anno in map.human and map.reversed with the first code in anno2code
    # because they are determined to be human non-distinguishable, at least from walkthrough naming perspective

    human_lines = []
    with open(map_human_path, "r") as f:
        for line in f:
            line = line.strip()
            if line == "":
                continue
            line, step_num = line.split(", step ")
            line = line.split(" --> ")
            src = line[0]
            dst = line[2]
            src = anno_to_code(src, anno2code)
            dst = anno_to_code(dst, anno2code)
            if src is None or dst is None:
                # abort!
                print(f"[{args.game}.map.human] | abort! src or dst is None", src, dst)
                exit(1)
            human_lines.append(f"{src} --> {line[1]} --> {dst}, step {step_num}")
    # dump back to map.human
    with open(map_human_path, "w") as f:
        for line in human_lines:
            f.write(f"{line}\n")

    print(f"[{args.game}.map.human] | node merge & naming space convertion DONE!")

    reversed_lines = []
    with open(map_reversed_path, "r") as f:
        for line in f:
            line = line.strip()
            if line == "":
                continue
            line_step, desc = line.split(", desc: ")
            line, step_num = line_step.split(", step ")
            line = line.split(" --> ")
            # in map.reversed: locations are named as "Junction (obj63)", "(obj63)" is the id, Junction is the annotation
            src = line[0].lower().split("(")[0].strip()
            dst = line[2].lower().split("(")[0].strip()
            src = anno_to_code(src, anno2code)
            dst = anno_to_code(dst, anno2code)
            if src is None or dst is None:
                # abort!
                print(
                    f"[{args.game}.map.reversed] | abort! src or dst is None", src, dst
                )
                exit(1)
            reversed_lines.append(
                f"{src} --> {line[1]} --> {dst}, step {step_num}, desc: {desc}"
            )
    # dump back to map.reversed
    with open(map_reversed_path, "w") as f:
        for line in reversed_lines:
            f.write(f"{line}\n")

    print(f"[{args.game}.map.reversed] | node merge & naming space convertion DONE!")
