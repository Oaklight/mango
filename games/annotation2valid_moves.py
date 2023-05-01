import argparse
import json

# argparse to read in annotated walkthrough file, check file extension for either txt or markdown mode
# output valid moves to json file


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("walkthrough_file", type=str, help="path to walkthrough file")
    parser.add_argument(
        "--csvOrjson", "-coj", type=str, default="csv", help="output to csv file"
    )
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
                src_node, action, dst_node = [
                    each.strip().lower() for each in move.split("-->")
                ]
                valid_moves[step_num] = {
                    "src_node": src_node,
                    "action": action,
                    "dst_node": dst_node,
                }
                print(
                    f"FOUND valid move [{step_num}]: {src_node} --> {action} --> {dst_node}"
                )

    print(f"{len(valid_moves)} valid moves found in {args.walkthrough_file}")
    # dump valid moves to json file
    # output file name is game.valid_moves.json, game is part of walkthrough_file, in md mode, game.walkthrough.md, in txt mode, game.walkthrough
    if args.csvOrjson == "csv":
        output_file = (
            args.walkthrough_file.split(".walkthrough")[0] + ".valid_moves.csv"
        )
        with open(output_file, "w") as f:
            f.write("Step Num, Location Before, Location After\n")
            # write lines starting with step number, regardless of whether it's in valid_moves
            for i in range(step_num):
                if i == 0:
                    continue
                if i in valid_moves:
                    f.write(
                        f"{i}, {valid_moves[i]['src_node']}, {valid_moves[i]['dst_node']}\n"
                    )
                else:
                    f.write(f"{i}, , \n")

    elif args.csvOrjson == "json":
        output_file = (
            args.walkthrough_file.split(".walkthrough")[0] + ".valid_moves.json"
        )
        with open(output_file, "w") as f:
            json.dump(valid_moves, f, indent=4)
    else:
        raise NotImplementedError
