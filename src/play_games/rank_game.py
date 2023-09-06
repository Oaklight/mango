"""
rank game: #revisited steps/#all steps --> rank all the games 
"""

import os
import csv






def main():
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
        return_list.append(['game: {}'.format(game_name), 'revisited steps: {}'.format(revisited_steps), 'all steps: {}'.format(all_steps), 'revisited ratio: {}'.format(revisited_ratio)])

    sorted_return_list = sorted(return_list,key = lambda x: x[2],reverse=True)
    for item in sorted_return_list:
        print (item)

    print ("Well Done!")



if __name__ == '__main__':
    main()