from jericho import * # https://jericho-py.readthedocs.io/en/latest/index.html
from argparse import ArgumentParser


direction_abbrv_dict = {'e': 'east', 'w': 'west', 'n': 'north', 's': 'south',
                        'ne': 'northeast', 'nw': 'northwest', 'se': 'southeast', 'sw': 'southwest',
                        'u': 'up', 'd': 'down'} # jericho.defines.ABBRV_DICT
direction_vocab_abbrv = direction_abbrv_dict.keys()
direction_vocab = direction_abbrv_dict.values()
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

def read_csv(path_in, max_steps = 70):
    print ("Reading file {} ing ...".format(path_in))
    valid_moves = []
    with open(path_in, 'r', encoding='utf-8') as fin:
        lines = [line.strip() for line in fin.readlines()]
        print ("Head: {}".format(lines[0]))
        for line in lines[1:max_steps+1]:
            step_num, location_before, location_after = line.split(',')
            valid_moves.append({
                'step_num': step_num.strip(),
                'location_before': location_before.strip(),
                'location_after': location_after.strip(),
                'valid_move': (location_before.strip() != '')
            })
    print ("Done.")
    return valid_moves

def main():
    parser = ArgumentParser()
    parser.add_argument("--jericho_path", '-j', type=str, default="z-machine-games-master/jericho-game-suite")
    parser.add_argument("--output_dir", '-odir', type=str, default="./maps")
    args = parser.parse_args()

    game_name = 'zork1.z5'
    max_steps = 70
    print ('Game: {}, Max steps: {}'.format(game_name, max_steps))

    env = FrotzEnv("{}/{}".format(args.jericho_path, game_name))

    # walkthrough
    walkthrough = env.get_walkthrough()
    walkthrough = [direction_abbrv_dict[item.lower()] if item.lower() in direction_vocab_abbrv else item.lower() for item in walkthrough]

    # annotated valid moves
    file_path = '{}/{}.valid_moves.csv'.format(args.output_dir, game_name.split('.')[0])
    print ("From {}".format(file_path))
    valid_moves = read_csv(file_path, max_steps= max_steps)

    output_file = '{}/{}.map.human'.format(args.output_dir, game_name.split('.')[0])
    with open(output_file,'w', encoding='utf-8') as fout:
        for step_idx, move in enumerate(valid_moves):
            move['act'] = walkthrough[step_idx]
            if move['valid_move']:
                fout.write('{} --> {} --> {}, step {}\n'.format(move['location_before'],
                                                                move['act'],
                                                                move['location_after'],
                                                                move['step_num']))
    print ("Saved to {}".format(output_file))
    print ("Good Job!")

if __name__ == '__main__':
    main()