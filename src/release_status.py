# map_dev: data/maps/
# map_release: data/maps-release
# status sheet: data/release_status.csv
# status sheet has following columns: at row 0
#  release (-1, 0, 1), status_code, game, walkthrough, map.machine, moves, valid_moves, map.human, code2anno, anno2code, map.reversed, all2all
# from row 1, it's the games in the map_dev folder

# I need a script to go over map_dev and check each folder (game) for the following files:
# - *.walkthrough
# - *.map.machine
# - *.moves
# - *.valid_moves.csv
# - *.map.human
# - *.code2anno.json
# - *.anno2code.json
# - *.map.reversed
# - *.all2all.json

# if such files exist, label corresponding csv entry as 1, if not label as 0
# when finish checking each folder, change status_code column by concate all digit in the row
# if 111111111 then release label as 1, otherwise 0, if map.machine missing, then -1

# start coding:
import os
import csv
import json

# get all games in map_dev
map_dev = 'data/maps/'
games = os.listdir(map_dev)
games = [game for game in games if os.path.isdir(os.path.join(map_dev, game))]
games.sort()

# get all games in map_release
map_release = 'data/maps-release/'
games_release = os.listdir(map_release)
games_release = [game for game in games_release if os.path.isdir(os.path.join(map_release, game))]
games_release.sort()

# get all games in status sheet
status_sheet = 'data/release_status.csv'
# drop old file if exist and open a new one
if os.path.exists(status_sheet):
    os.remove(status_sheet)
status = []
games_status = []


# check each game folder for those wanted files, and label corresponding csv entry
for game in games:
    # these are needed:
    # - *.walkthrough
    # - *.map.machine
    # - *.moves
    # - *.valid_moves.csv
    # - *.map.human
    # - *.code2anno.json
    # - *.anno2code.json
    # - *.map.reversed
    # - *.all2all.json
    # if such files exist, label corresponding csv entry as 1, if not label as 0
    
    # get files in the game folder
    game_folder = os.path.join(map_dev, game)
    files = os.listdir(game_folder)
    files = [file for file in files if os.path.isfile(os.path.join(game_folder, file))]
    files.sort()

    # check if all files exist
    walkthrough = 1 if game + '.walkthrough' in files else ""
    map_machine = 1 if game + '.map.machine' in files else ""
    moves = 1 if game + '.moves' in files else ""
    valid_moves = 1 if game + '.valid_moves.csv' in files else ""
    map_human = 1 if game + '.map.human' in files else ""
    code2anno = 1 if game + '.code2anno.json' in files else ""
    anno2code = 1 if game + '.anno2code.json' in files else ""
    map_reversed = 1 if game + '.map.reversed' in files else ""
    all2all = 1 if game + '.all2all.json' in files else ""
    
    # status_code = f"{walkthrough}{map_machine}{moves}{valid_moves}{map_human}{code2anno}{anno2code}{map_reversed}{all2all}"
    # if variable above is "" then treat it as 0, make status_code:
    status_code = ""
    status_code += "1" if walkthrough else "0"
    status_code += "1" if map_machine else "0"
    status_code += "1" if moves else "0"
    status_code += "1" if valid_moves else "0"
    status_code += "1" if map_human else "0"
    status_code += "1" if code2anno else "0"
    status_code += "1" if anno2code else "0"
    status_code += "1" if map_reversed else "0"
    status_code += "1" if all2all else "0"

    # if all 1, then release 1; if walkthrough or map.machine missing, then release -1; otherwise ""
    release = ""
    if status_code == "111111111":
        release = "1"
    elif walkthrough == "" or map_machine == "":
        release = "-1"


    # label csv by replace it with a new entry if exist, add new entry if not
    if game in games_status:
        index = games_status.index(game)
        status[index] = [release, status_code, game, walkthrough, map_machine, moves, valid_moves, map_human, code2anno, anno2code, map_reversed, all2all]
    else:
        status.append([release, status_code, game, walkthrough, map_machine, moves, valid_moves, map_human, code2anno, anno2code, map_reversed, all2all])

# update local csv file
with open(status_sheet, 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['release', 'status_code', 'game', 'walkthrough', 'map.machine', 'moves', 'valid_moves', 'map.human', 'code2anno', 'anno2code', 'map.reversed', 'all2all'])
    writer.writerows(status)