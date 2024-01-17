# export TIKTOKEN_CACHE_DIR=./cache
import os, json
import tiktoken


def to_chat_json(text):
    return [
        {
            "role": "user",
            "content": text
        }
    ]

def read_json(json_path):
    with open(json_path, 'r') as f:
        json_object = json.load(f)
    return json_object

def save_json(json_content, json_path):
    json_object = json.dumps(json_content, indent=4)
    with open(json_path, "w") as outfile:
        outfile.write(json_object)

mango_path = '/home-nfs/pengli/workspace/projects/mango'
maps_folder = mango_path + '/data'
chats_folder = mango_path + '/models/claude/chats'
claude_configs_folder = mango_path + '/models/claude/claude_configs'

cut_off_number_dict = {}

for game in os.listdir(maps_folder):
    print('game: {}'.format(game))
    game_maps_path = os.path.join(maps_folder, game)
    game_chats_folder = os.path.join(chats_folder, game)
    if not os.path.exists(game_chats_folder):
        os.makedirs(game_chats_folder)

    ###############################################
    # create walkthrough chat
    ###############################################
    walkthrough_path = os.path.join(game_maps_path, '{}.walkthrough'.format(game))
    with open(walkthrough_path, 'r') as f:
        raw_walkthrough_text = f.read()

    # # filter the first 70 steps
    # walkthrough_text = walkthrough_text.split('NUM: 71')[0]
    # walkthrough_text = '\n'.join(walkthrough_text.split('\n')[:-1])

    # cut off according to token size limit
    token_size_limit = 3600
    encoder = tiktoken.encoding_for_model("gpt-4-0314")
    enc = encoder.encode(raw_walkthrough_text)
    print('length of original walkthrough_text tokens: {}'.format(len(enc)))
    if len(enc) > token_size_limit:
        cut_off_walkthrough_text = encoder.decode(enc[:token_size_limit])
        # print('raw cut off walkthrough_text: {}'.format(cut_off_walkthrough_text))
    cut_off_number = int(cut_off_walkthrough_text.split('NUM: ')[-2].split('\n')[0])
    if cut_off_number > 70:
        cut_off_number = 70
    print('cut_off_number: {}'.format(cut_off_number))
    cut_off_number_dict[game] = cut_off_number
    walkthrough_text = raw_walkthrough_text.split('NUM: {}'.format(cut_off_number + 1))[0]
    walkthrough_text = '\n'.join(walkthrough_text.split('\n')[:-1])
    # print(walkthrough_text)

    walkthrough_name = 'walkthrough_{}'.format(cut_off_number)
    walkthrough_json_path = os.path.join(game_chats_folder, '{}.{}.json'.format(game, walkthrough_name))
    save_json(to_chat_json(walkthrough_text), walkthrough_json_path)
    print('{} saved to {}'.format(walkthrough_name, walkthrough_json_path))

    ###############################################
    # create action space chat
    ###############################################
    moves_path = os.path.join(game_maps_path, '{}.actions.json'.format(game))
    action_text = "The allowed actions are: {}".format(read_json(moves_path))
    print(action_text)

    action_json_path = os.path.join(game_chats_folder, '{}.action_space.json'.format(game))
    save_json(to_chat_json(action_text), action_json_path)
    print('action_space saved to {}'.format(action_json_path))

    ###############################################
    # create allowed places chat
    ###############################################

    places_path = os.path.join(game_maps_path, '{}.locations.json'.format(game))
    allowed_places_text = "The list of places are: {}".format(read_json(places_path))
    print(allowed_places_text)

    place_names_json_path = os.path.join(game_chats_folder, '{}.place_names.json'.format(game))
    save_json(to_chat_json(allowed_places_text), place_names_json_path)
    print('place_names saved to {}'.format(place_names_json_path))

    ###############################################
    # create claude config
    ###############################################
    claude_config_folder = os.path.join(claude_configs_folder, game)
    if not os.path.exists(claude_config_folder):
        os.makedirs(claude_config_folder)

    claude_2_config = {
        "model": "claude-2",
        "temperature": 0,
        "max_tokens_to_sample": 500,
        "load_path": [
            walkthrough_json_path,
            action_json_path,
            place_names_json_path
        ],
        "save_path": "outputs/{}/results/".format(game)
    }

    claude_instant_1_config = {
        "model": "claude-instant-1",
        "temperature": 0,
        "max_tokens_to_sample": 500,
        "load_path": [
            walkthrough_json_path,
            action_json_path,
            place_names_json_path
        ],
        "save_path": "outputs/{}/results/".format(game)
    }

    claude_2_config_path = os.path.join(claude_config_folder, '{}.claude2.json'.format(game))
    save_json(claude_2_config, claude_2_config_path)
    print('gpt3 config saved to {}'.format(claude_2_config_path))

    claude_instant_1_config_path = os.path.join(claude_config_folder, '{}.claude_instant_1.json'.format(game))
    save_json(claude_instant_1_config, claude_instant_1_config_path)
    print('gpt4 config saved to {}'.format(claude_instant_1_config_path))

    # break

print('cut_off_number_dict: {}'.format(cut_off_number_dict))
"""
cut_off_number_dict: {'gold': 47, 'awaken': 44, 'moonlit': 45, 'enchanter': 53, 'afflicted': 40, 'trinity': 45, 'advent': 70, 'hollywood': 50, 'karn': 65, 'inhumane': 49, 'zenon': 63, 'planetfall': 68, 'balances': 67, 'partyfoul': 24, 'zork3': 61, 'snacktime': 61, 'jewel': 60, 'deephome': 49, 'spirit': 50, 'omniquest': 70, 'lurking': 56, 'loose': 39, 'cutthroat': 62, 'huntdark': 55, 'sorcerer': 54, 'library': 49, 'enter': 20, 'reverb': 40, 'infidel': 55, 'ztuu': 43, 'anchor': 24, 'wishbringer': 45, 'sherlock': 33, 'hhgg': 51, 'temple': 46, 'pentari': 48, 'ballyhoo': 56, 'zork1': 70, '905': 70, 'seastalker': 53, 'murdac': 70, 'lostpig': 56, 'spellbrkr': 52, 'plundered': 32, 'adventureland': 70, 'curses': 53, 'ludicorp': 70, 'yomomma': 41, 'tryst205': 65, 'dragon': 29, 'detective': 43, 'night': 70, 'zork2': 50}
"""
