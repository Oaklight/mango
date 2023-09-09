"""
rank game: #revisited steps/#all steps --> rank all the games 
"""

import os
import re 
from collections import defaultdict

direction_list = ['east', 'west', 'north', 'south', 'northeast', 'northwest', 'southeast', 'up', 'down']
opposite_direction_dict = {
    'east': 'west',
    'west': 'east',
    'north': 'south',
    'south': 'north',
    'northeast': 'southwest',
    'southwest': 'northeast',
    'northwest': 'southeast',
    'southeast': 'northwest',
    'up': 'up',
    'down': 'down'
}

def extract_location(step):
    location = re.search(r'==>OBSERVATION:(.*?)\n', step).group(1).strip()
    if location == '>': # sherlock
        location = re.search(r'==>OBSERVATION: >\n(.*?)\n', step).group(1).strip()
    return location

def rank_game():
    max_steps = 71
    print ("max_steps: {}".format(max_steps))

    games_folder = './data'
    game_names = os.listdir(games_folder)

    dataset = {} # history, valid action, map, golden action

    return_list = []
    for game_name in game_names:
        walkthrough_file_path = os.path.join(games_folder, game_name, game_name + '.walkthrough')
        with open(walkthrough_file_path, 'r', encoding='utf-8') as fin:
            walkthrough = fin.read()
            steps = walkthrough.split('===========')[1:]

        revisited_steps = 0
        transition_steps = 0
        walkthrough_length = 0
        step_idx_list = []

        map = defaultdict(dict)
        last_location = 'Init'
        for step_idx, step in enumerate(steps[:max_steps]):
            # extract action
            if 'ACT' not in step:
                continue
            action = re.search(r'==>ACT:(.*?)\n', step).group(1).strip()

            # transition action
            if action in set(direction_list):
                location = extract_location(step)
                if location == last_location:
                    continue
                transition_steps += 1

                if len(map) == 0:
                    map[last_location] = {
                        location: action
                    }
                    map[location] = {
                        last_location: opposite_direction_dict[action]
                    }
                elif location not in map:
                    map[last_location][location] = action
                    map[location] = {
                        last_location: opposite_direction_dict[action]
                    }
                elif location not in map[last_location] or map[last_location][location] != action:
                    map[last_location][location] = action
                    map[location][last_location] = opposite_direction_dict[action]
                elif map[last_location][location] == action: # revisit
                    revisited_steps += 1
                    step_idx_list.append(step_idx)
                last_location = location

            walkthrough_length +=1 

        if transition_steps == 0:
            revisited_ratio = 0
        else:
            revisited_ratio = revisited_steps/transition_steps
        if revisited_steps < 10 or transition_steps < 20:
            continue
        return_list.append([game_name, revisited_steps, transition_steps, walkthrough_length, revisited_ratio, step_idx_list])

    sorted_return_list = sorted(return_list,key = lambda x: x[4],reverse=True)
    for item in sorted_return_list:
        print (item)
    print ("Well Done!")
                
if __name__ == '__main__':
    rank_game()