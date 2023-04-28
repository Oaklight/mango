# utils for convert md version to json version
import argparse
import json
import os

# - markdown

#   ```markdown
#   # srcNode --> dstNode || diff_shortest: *
#   action1
#   action2
#   ...
#   ```

# - json (not available yet)

#   ```json
#   {
#     "srcNode": "srcNode",
#     "dstNode": "dstNode",
#     "diff_shortest": diff_shortest,
#     "actions": [
#       "action1",
#       "action2",
#       ...
#     ]
#   }
#   ```


def md2json(md):
    """convert md version to json version

    Args:
        md (str): markdown version

    Returns:
        str: json version
    """
    # read in file line by line
    # if empty skip
    # if H1, title is "srdNode --> dstNode || diff_shortest: *"
    # if others, append to actions
    with open(md, "r") as f:
        lines = f.readlines()
    unit_list = []
    unit = {}
    for line in lines:
        line = line.strip().lower()
        if line == "":
            if len(unit) != 0:
                # append unit to unit_list
                unit_list.append(unit)
                unit = {}
            else:
                continue
        elif line[0] == "#":
            if "||" in line:
                fromTo, diff_shortest = [
                    each.strip() for each in line[1:].split("|| diff_shortest:")
                ]
            else:
                fromTo = line[1:].strip()
                diff_shortest = 0
            srcNode, dstNode = [each.strip() for each in fromTo.split("-->")]
            unit["srcNode"] = srcNode
            unit["dstNode"] = dstNode
            unit["diff_shortest"] = diff_shortest
            unit["actions"] = []
        else:
            unit["actions"].append(line)

    json_file = md[:-2] + "json"
    with open(json_file, "w") as f:
        json.dump(unit_list, f, indent=4)
    # iterate over md file line by line, if empty skip, if H1, title is "srdNode --> dstNode || diff_shortest: *", if others, append to actions


if __name__ == "__main__":
    # read in md file
    parser = argparse.ArgumentParser()
    parser.add_argument("md", type=str, help="path to md file")
    args = parser.parse_args()

    md2json(args.md)
