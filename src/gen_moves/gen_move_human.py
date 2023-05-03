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


# from jericho import * # https://jericho-py.readthedocs.io/en/latest/index.html
# from argparse import ArgumentParser
#
#
# direction_abbrv_dict = {'e': 'east', 'w': 'west', 'n': 'north', 's': 'south',
#                         'ne': 'northeast', 'nw': 'northwest', 'se': 'southeast', 'sw': 'southwest',
#                         'u': 'up', 'd': 'down'} # jericho.defines.ABBRV_DICT
# direction_vocab_abbrv = direction_abbrv_dict.keys()
# direction_vocab = direction_abbrv_dict.values()
# opposite_direction_dict = {
#     'east': 'west',
#     'west': 'east',
#     'north': 'south',
#     'south': 'north',
#     'northeast': 'southwest',
#     'southwest': 'northeast',
#     'northwest': 'southeast',
#     'southeast': 'northwest',
#     'up': 'up',
#     'down': 'down'
# }
#
# def read_csv(path_in, max_steps = 70):
#     print ("Reading file {} ing ...".format(path_in))
#     valid_moves = []
#     with open(path_in, 'r', encoding='utf-8') as fin:
#         lines = [line.strip() for line in fin.readlines()]
#         print ("Head: {}".format(lines[0]))
#         for line in lines[1:max_steps+1]:
#             step_num, location_before, location_after = line.split(',')
#             valid_moves.append({
#                 'step_num': step_num.strip(),
#                 'location_before': location_before.strip(),
#                 'location_after': location_after.strip(),
#                 'valid_move': (location_before.strip() != '')
#             })
#     print ("Done.")
#     return valid_moves
#
# def main():
#     parser = ArgumentParser()
#     parser.add_argument("--jericho_path", '-j', type=str, default="z-machine-games-master/jericho-game-suite")
#     parser.add_argument("--output_dir", '-odir', type=str, default="./maps")
#     args = parser.parse_args()
#
#     game_name = 'zork1.z5'
#     max_steps = 70
#     print ('Game: {}, Max steps: {}'.format(game_name, max_steps))
#
#     env = FrotzEnv("{}/{}".format(args.jericho_path, game_name))
#
#     # walkthrough
#     walkthrough = env.get_walkthrough()
#     walkthrough = [direction_abbrv_dict[item.lower()] if item.lower() in direction_vocab_abbrv else item.lower() for item in walkthrough]
#
#     # annotated valid moves
#     file_path = '{}/{}.valid_moves.csv'.format(args.output_dir, game_name.split('.')[0])
#     print ("From {}".format(file_path))
#     valid_moves = read_csv(file_path, max_steps= max_steps)
#
#     output_file = '{}/{}.map.human'.format(args.output_dir, game_name.split('.')[0])
#     with open(output_file,'w', encoding='utf-8') as fout:
#         for step_idx, move in enumerate(valid_moves):
#             move['act'] = walkthrough[step_idx]
#             if move['valid_move']:
#                 fout.write('{} --> {} --> {}, step {}\n'.format(move['location_before'],
#                                                                 move['act'],
#                                                                 move['location_after'],
#                                                                 move['step_num']))
#     print ("Saved to {}".format(output_file))
#     print ("Good Job!")
#
# if __name__ == '__main__':
#     main()