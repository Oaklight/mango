# utils for convert md version to json version
import argparse
import json
import os

# - markdown

#   ```markdown
#   # src_node --> dst_node || diff_shortest: *
#   action1
#   action2
#   ...
#   ```

# - json (not available yet)

#   ```json
#   {
#     "src_node": "src_node",
#     "dst_node": "dst_node",
#     "diff_shortest": diff_shortest,
#     "actions": [
#       "action1",
#       "action2",
#       ...
#     ]
#   }
#   ```


def md2json(md, write2file=False):
    """convert md version to json version

    Args:
        md (str): markdown version

    Returns:
        str: json version
    """
    # read in file line by line
    # if empty skip
    # if H1, title is "srdNode --> dst_node || diff_shortest: *"
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
            src_node, dst_node = [each.strip() for each in fromTo.split("-->")]
            unit["src_node"] = src_node
            unit["dst_node"] = dst_node
            unit["diff_shortest"] = diff_shortest
            unit["actions"] = []
        else:
            unit["actions"].append(line)

    if write2file:
        # save to json file
        with open(md.replace(".md", ".json"), "w") as f:
            json.dump(unit_list, f, indent=4)

    return unit_list



if __name__ == "__main__":
    # read in md file
    parser = argparse.ArgumentParser(
        description="Convert Markdown file to JSON, YAML, or TOML"
    )
    parser.add_argument("md", type=str, help="the path to the Markdown file to convert")
    parser.add_argument(
        "format",
        type=str,
        help='the format to convert to (either "json", "yaml", or "toml")',
    )

    # Parse command-line arguments
    args = parser.parse_args()

    # Convert Markdown to JSON
    json_data = md2json(args.md)
    
    # Convert JSON to desired format
    if args.format == 'json':
        output_data = json.dumps(json_data, indent=4)
    # elif args.format == 'yaml':
    #     output_data = yaml.dump(json_data, indent=4)
    # elif args.format == 'toml':
    #     output_data = toml.dumps(json_data)
    else:
        raise ValueError('Invalid output format specified')

    # Save output to file with same name in same folder
    basename, _ = os.path.splitext(args.md)
    output_filename = f'{basename}.{args.format}'
    with open(output_filename, 'w') as f:
        f.write(output_data)
        
    print(f'Successfully converted {args.md} to {output_filename}')
