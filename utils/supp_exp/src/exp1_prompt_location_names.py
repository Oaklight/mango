"""
mango supplementary experiment 1

make chatgpt predict location names
"""

import os
import csv
from src.api import api_complete

SYSTEM_PROMPT = "You are a helpful AI assistant."


def read_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as fin:
        return fin.read()
    
def read_valid_moves(file_path):
    with open(file_path, 'r', encoding='utf-8') as fin:
        csv_reader = csv.reader(fin)
        lines = [row for row in csv_reader][1:71]
        results = [line[2].strip() for line in lines]
        results = [item if item != '' else 'None' for item in results]
    return results

def format_demo(idx, sample, location):
    return f"Example {idx+1}:\n{sample}\n==>LOCATION: {location}"


EXAMPLES = """Example 1:
==>ACT: wait
==>OBSERVATION: Plundered Hearts                                                                                                  Score: 0                Moves: 0              










 Cabin                                                                                                  Score: 0                Moves: 0              PLUNDERED HEARTS
Infocom interactive fiction
Copyright (c) 1987 by Infocom, Inc. All rights reserved.
PLUNDERED HEARTS is a trademark of Infocom, Inc.
Release 26 / Serial number 870730

LATE ONE SPRING NIGHT IN THE WEST INDIES...

   A crash overhead! Pirates are boarding the Lafond Deux! The first mate hurries you into Captain Davis's cabin.
   "Good, you brought the girl," Davis smirks. "She'll keep the pirates busy. She was only a tool of Lafond's, anyway. Let me just find that cof--" A man on deck screams in agony and Davis starts. "Let's go." The captain thrusts you on the bed and walks out, locking the door.
   His laugh echoes. "Best get comfortable, girl. You're likely to be there for the rest of your life."

Cabin, on the bed
   You are in an officer's cabin, lit by the firelight glowing through a porthole. A door is to starboard. Except for the built-in bed, the room seems to have been emptied thoroughly, if hurriedly.
==>LOCATION: Cabin, on the bed

Example 2:
==>ACT: stand up
==>OBSERVATION: You get out of the bed.
   "Cap'n Jamison! We've got 'em!" cries a rough voice.
==>LOCATION: Cabin

Example 3:
==>ACT: wait
==>OBSERVATION: Time passes...
   With a creak and a crash, somewhere a mast falls to the deck.
==>LOCATION: None

Example 4:
==>ACT: wait
==>OBSERVATION: Time passes...
   Suddenly, the ship lurches to one side, throwing you off balance. A coffer slides from under the bed and bumps against your foot.
   "The Falcon! The Falcon conquers!" yells someone.
==>LOCATION: None

Example 5:
==>ACT: get coffer
==>OBSERVATION: Taken.
   "Aaieeee!" echoes a scream, followed by several grunts and thumps.
==>LOCATION: None"""

def main():
    base_folder = "<MANGO_ROOT_PATH>"
    data_folder = os.path.join(base_folder, 'data')
    valid_moves_folder = os.path.join(base_folder,'data-intermediate')
    games = os.listdir(data_folder)
    print ("games: ", sorted(games))

    for game in sorted(games):
        if game != 'temple':
            continue
        walkthrough_path = os.path.join(data_folder, game, '{}.walkthrough'.format(game))
        walkthrough_text = read_txt(walkthrough_path)
        triples = walkthrough_text.split("===========")
        triples = [item.strip() for item in triples][1:-1]
        descriptions = ['==>ACT:' + item.split('==>ACT:')[1] for item in triples][1:71]

        valid_moves_path = os.path.join(valid_moves_folder, game, '{}.valid_moves.csv'.format(game))
        walkthrough_list = read_valid_moves(valid_moves_path)[:len(descriptions)]
        print ("len: {}".format(len(descriptions)))

        golden_examples = [format_demo(idx, item,walkthrough_list[idx]) for idx, item in enumerate(descriptions[:5])]
        examples = '\n\n'.join(golden_examples)
        result = []

        for desc in descriptions:
            print ("*" * 20)
            prompt = "The following description is an observation of a character in a game. Please determine the character's location based on the description. \nHere are some examples: \n{}\nIf you can identify the character's location from the text, please just reply with that location; otherwise, reply with 'None':\n\n{}\n==>LOCATION:".format(examples, desc)
            gpt_response = api_complete(system_prompt=SYSTEM_PROMPT, prompt=prompt).strip()
            
            result.append(gpt_response)
            print ("DESC: ", desc)
            print ("LOC: ", gpt_response)

        print (walkthrough_list)
        print (result)
        success = [walkthrough_list[i] == result[i] for i in range(len(walkthrough_list))]
        success_rate = sum(success)/len(success)
        print (success_rate)
        with open('./{}_extracting_location.txt'.format(game), 'w+', encoding='utf-8') as fout:
            fout.write(prompt)
            fout.write('\n')
            fout.write(', '.join(walkthrough_list))
            fout.write('\n')
            fout.write(', '.join(result))
            fout.write('\n')
            fout.write("success rate: {} * {}".format(success_rate, len(descriptions)))
            fout.write('\n')
        exit(0)




if __name__ == '__main__':
    main()