import argparse
import json

# argparse to read in annotated walkthrough file, check file extension for either txt or markdown mode
# output valid moves to json file


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("walkthrough_file", type=str, help="path to walkthrough file")
    args = parser.parse_args()

    if args.walkthrough_file.endswith(".md"):
        print("markdown mode")
        args.isMarkdown = True
    else:
        print("txt mode")
        args.isMarkdown = False
    SECTION_SPLITTER = "***" if args.isMarkdown else "==========="
    SECTION_HEADER = "# " if args.isMarkdown else "==>"
    TARGET_HEADER = "## " if args.isMarkdown else "==>"

    valid_moves = {}
    # read in walkthrough file
    with open(args.walkthrough_file, "r") as f:
        walkthrough = f.readlines()

        for line in walkthrough:
            # line = line.strip().lower()
            # parse line, skip empty line
            if line == "":
                continue

            # read in step number, check
            if f"{SECTION_HEADER}STEP NUM: " in line:
                step_num = int(line.split(f"{SECTION_HEADER}STEP NUM:")[1])

            if f"{TARGET_HEADER}MOVE: " in line:
                move = line.split(f"{TARGET_HEADER}MOVE:")[1]
                srcNode, action, dstNode = [
                    each.strip().lower() for each in move.split("-->")
                ]
                valid_moves[step_num] = {
                    "srcNode": srcNode,
                    "action": action,
                    "dstNode": dstNode,
                }
                print(
                    f"FOUND valid move [{step_num}]: {srcNode} --> {action} --> {dstNode}"
                )

    print(f"{len(valid_moves)} valid moves found in {args.walkthrough_file}")
    # dump valid moves to json file
    # output file name is gamename.valid_moves.json, gamename is part of walkthrough_file, in md mode, gamename.walkthrough.md, in txt mode, gamename.walkthrough
    output_file = args.walkthrough_file.split(".walkthrough")[0] + ".valid_moves.json"
    with open(output_file, "w") as f:
        json.dump(valid_moves, f, indent=4)
