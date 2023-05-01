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

def main():
    parser = ArgumentParser()
    parser.add_argument("--jericho_path", '-j', type=str, default="z-machine-games-master/jericho-game-suite")
    parser.add_argument("--output_dir", '-odir', type=str, default="./maps")
    args = parser.parse_args()

    game_name = 'zork1.z5'
    max_steps = 70
    print ('Game: {}, Max steps: {}'.format(game_name, max_steps))

    # env
    env = FrotzEnv("{}/{}".format(args.jericho_path, game_name))
    initial_observation, info = env.reset()
    location_before = env.get_player_location().name.strip().lower()
    location_before_id = env.get_player_location().num

    # walkthrough
    walkthrough = env.get_walkthrough()
    walkthrough = [direction_abbrv_dict[item.lower()] if item.lower() in direction_vocab_abbrv else item.lower() for item in walkthrough]

    map_list = []
    map_reversed_list = []
    for step_idx, act in enumerate(walkthrough[:max_steps]):
        observation, reward, done, info = env.step(act)
        location_after = env.get_player_location().name.strip().lower()
        location_after_id = env.get_player_location().num
        if location_after_id != location_before_id:
            map_list.append({
                'location_before': location_before,
                'location_before_id': location_before_id,
                'act': act,
                'location_after': location_after,
                'location_after_id': location_after_id,
                'step_num': step_idx + 1
            })

            # reverse
            valid_actions = env.get_valid_actions()
            if act in direction_vocab:
                if opposite_direction_dict[act] in valid_actions:
                    desc = 'None'
                else:
                    obsrv_splitted = observation.split('\n')
                    if len(obsrv_splitted) == 1:
                        desc = obsrv_splitted[0]
                    else:
                        desc = '{} || {}'.format(obsrv_splitted[0], "".join(obsrv_splitted[1:]))

                map_reversed_list.append({
                    'location_before': location_after,
                    'location_before_id': location_after_id,
                    'act': opposite_direction_dict[act],
                    'location_after': location_before,
                    'location_after_id': location_before_id,
                    'step_num': step_idx + 1,
                    'desc': desc
                }
                )

            else:
                map_reversed_list.append({
                    'location_before': None,
                    'location_before_id': None,
                    'act': None,
                    'location_after': None,
                    'location_after_id': None,
                    'step_num': None,
                    'desc': None
                }
                )

            location_before = location_after
            location_before_id = location_after_id

    output_file = '{}/{}.map.machine'.format(args.output_dir,game_name.split('.')[0])
    with open(output_file,'w', encoding='utf-8') as fout:
        for item in map_list:
            fout.write('{} (obj{}) --> {} --> {} (obj{}), step {}\n'.format(item['location_before'],
                                                                              item['location_before_id'],
                                                                              item['act'],
                                                                              item['location_after'],
                                                                              item['location_after_id'],
                                                                              item['step_num']))
    print ("Saved to {}".format(output_file))

    output_file = '{}/{}.map.machine.reversed'.format(args.output_dir, game_name.split('.')[0])
    with open(output_file,'w', encoding='utf-8') as fout:
        for item in map_reversed_list:
            if item['act'] != None:
                fout.write('{} (obj{}) --> {} --> {} (obj{}), step {}, desc: {}\n'.format(item['location_before'],
                                                                                            item['location_before_id'],
                                                                                            item['act'],
                                                                                            item['location_after'],
                                                                                            item['location_after_id'],
                                                                                            item['step_num'],
                                                                                            item['desc']))
            else:
                fout.write('\n')

    print ("Saved to {}".format(output_file))
    print ("Good Job!")




if __name__ == '__main__':
    main()