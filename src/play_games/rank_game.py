"""
rank game: #revisited steps/#all steps --> rank all the games 
"""

import os
import csv
import re 

direction_list = ['east', 'west', 'north', 'south', 'northeast', 'northwest', 'southeast', 'up', 'down']


def calc_walkthrough():
    games_folder = './data'
    game_names = os.listdir(games_folder)
    print (game_names)

    return_list = []
    for game_name in game_names:
        walkthrough_file_path = os.path.join(games_folder, game_name, game_name + '.walkthrough')
        with open(walkthrough_file_path, 'r', encoding='utf-8') as fin:
            walkthrough = fin.read()
            steps = walkthrough.split('===========')

        location_history = set()
        revisited_steps = 0
        all_steps = 0
        walkthrough_length = 0

        for step in steps:
            if 'ACT' not in step:
                continue
            action = re.search(r'==>ACT:(.*?)\n', step).group(1).strip()
            if action in set(direction_list):
                location = re.search(r'==>OBSERVATION:(.*?)\n', step).group(1).strip()
                if location == '>': # sherlock
                    location = re.search(r'==>OBSERVATION: >\n(.*?)\n', step).group(1).strip()

                if location in location_history:
                    revisited_steps += 1
                else:
                    location_history.add(location)
                all_steps += 1
            walkthrough_length +=1 

        if all_steps == 0:
            revisited_ratio = 0
        else:
            revisited_ratio = revisited_steps/all_steps
        return_list.append([game_name, revisited_steps, all_steps, walkthrough_length, revisited_ratio])
    sorted_return_list = sorted(return_list,key = lambda x: x[4],reverse=True)
    for item in sorted_return_list:
        print (item)
    print ("Well Done!")
                

if __name__ == '__main__':
    calc_walkthrough()


"""
def calc_valid_moves():
    games_folder = './data-intermediate'
    game_names = os.listdir(games_folder)
    print (game_names)

    return_list = []
    for game_name in game_names:
        valid_moves_file_path = os.path.join(games_folder, game_name, game_name + '.valid_moves.csv')
        with open(valid_moves_file_path, 'r', encoding='utf-8') as fin:
            lines = list(csv.reader(fin))[1:]
            valid_moves = [line[:3] for line in lines]

        location_history = set()
        revisited_steps = 0
        all_steps = 0
        for move in valid_moves:
            if move[1] == '':
                continue
            location_history.add(move[1].strip())

            if move[2] in location_history:
                revisited_steps += 1
            else:
                location_history.add(move[2].strip())
            all_steps += 1

        if all_steps == 0:
            revisited_ratio = 0
        else:
            revisited_ratio = revisited_steps/all_steps
        return_list.append([game_name, revisited_steps, all_steps, revisited_ratio])

    sorted_return_list = sorted(return_list,key = lambda x: x[3],reverse=True)
    for item in sorted_return_list:
        print (item)
    print ("Well Done!")
"""