import os
import csv
from api import api_complete

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

def main():
    base_folder = "/home-nfs/pengli/workspace/projects/mango"
    data_folder = os.path.join(base_folder, 'data')
    valid_moves_folder = os.path.join(base_folder,'data-intermediate')
    games = os.listdir(data_folder)
    print ("games: ", sorted(games))

    for game in sorted(games):
        if game not in ['zork1','night', 'partyfoul','plundered','spirit','temple']:
            continue
        walkthrough_path = os.path.join(data_folder, game, '{}.walkthrough'.format(game))
        walkthrough_text = read_txt(walkthrough_path)
        triples = walkthrough_text.split("===========")[:30]
        walkthrough_text_30 = '\n'.join(triples)

        prompt = "!! Here is a walkthrough of a textgame: {}\n\n".format(walkthrough_text_30)
        prompt += "!! Please identify the changes in the location of the character from this walkthrough. Output a list of dictionaries with keys 'location before,' 'action,' and 'location after.' Start your response with '['."
        print ("prompt: ", prompt)
        gpt_response = api_complete(system_prompt=SYSTEM_PROMPT, prompt=prompt).strip()
        print ("prompt: ", gpt_response)
        with open('./{}_prompt_location.txt'.format(game), 'w+', encoding='utf-8') as fout:
            fout.write(game + '\n')
            fout.write(prompt + '\n')
            fout.write(gpt_response)




if __name__ == '__main__':
    main()