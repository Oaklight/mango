from jericho import *
# Create the environment, optionally specifying a random seed
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--jericho_path", '-j', type=str, default="z-machine-games-master/jericho-game-suite")
parser.add_argument("--output_dir", '-odir', type=str, default="./maps")
args = parser.parse_args()

game_name = 'zork1.z5'
env = FrotzEnv("{}/{}".format(args.jericho_path, game_name))

# direction dict
# todo: not wens, like 'pray'
direction_abbrv_dict = {'e': 'east', 'w': 'west', 'n': 'north', 's': 'south',
                        'ne': 'northeast', 'nw': 'northwest', 'se': 'southeast', 'sw': 'southwest'} # jericho.defines.ABBRV_DICT
direction_abbrv_vocab = direction_abbrv_dict.keys()
direction_vocab = direction_abbrv_dict.values()
opposite_direction_dict = {
    'east': 'west',
    'west': 'east',
    'north': 'south',
    'south': 'north',
    'northeast': 'southwest',
    'southwest': 'northeast',
    'northwest': 'southeast',
    'southeast': 'northwest'
}

# walkthrough
walkthrough = env.get_walkthrough()
walkthrough_direction = [direction_abbrv_dict[w.lower()] for w in walkthrough if w.lower() in direction_abbrv_vocab]
print ('===> walkthrough direction: {}'.format(walkthrough_direction))

map_list = []
walkthrough_list = []

initial_observation, info = env.reset()
print ('init ob: {}, info: {}'.format(initial_observation, info))
loc_before = 'West of House'
done = False
sample_info = {
    'act': 'Init',
    'observation': initial_observation,
    'step': info['moves']
}
walkthrough_list.append(sample_info)

for act in walkthrough:
    observation, reward, done, info = env.step(act)
    valid_actions = env.get_valid_actions()
    # print('act: {}, observation: {}, reward: {}, done: {}, info: {}'.format(act,observation.replace('\n','||'),reward,done,info))
    # print ('==> valid actions: {}'.format(valid_actions))
    sample_info = {
        'act': act,
        'observation': observation,
        'step': info['moves']
    }
    print (sample_info)
    walkthrough_list.append(sample_info)

    # todo: check loc_before and loc_after
    if act.lower() in direction_abbrv_vocab:
        act = direction_abbrv_dict[act.lower()]
        oppo_act = opposite_direction_dict[act]
        valid_actions = [a for a in valid_actions if a in direction_vocab]
        oppo_direction_valid = (oppo_act in valid_actions)
        if oppo_direction_valid == True:
            desc = 'None'
        else:
            obsrv_splitted = observation.split('\n')
            if len(obsrv_splitted) == 1:
                desc = obsrv_splitted[0]
            else:
                desc = '{} || {}'.format(obsrv_splitted[0], "".join(obsrv_splitted[1:]))

        sample = {
            'loc_before': loc_before,
            'act': act,
            'loc_after': observation.split('\n')[0],
            'valid_actions': valid_actions,
            'oppo_direction_valid': oppo_direction_valid,
            'description': desc
        }
        map_list.append(sample)
        # print (sample)
        loc_before = observation.split('\n')[0]

assert done == True
print ('Scored', info['score'], 'out of', env.get_max_score())

outfile = '{}/{}.walkthrough'.format(args.output_dir, game_name.split('.')[0])
with open(outfile, 'w', encoding='utf-8') as fout:
    fout.write('===========\n')
    for sample in walkthrough_list:
        fout.write('==>STEP NUM: {}\n==>ACT: {}\n==>OBSERVATION: {}\n'.format(sample['step'], sample['act'], sample['observation'].strip()))
        fout.write('\n===========\n')

outfile = '{}/{}.map'.format(args.output_dir, game_name.split('.')[0])
with open(outfile, 'w', encoding='utf-8') as fout:
    for sample in map_list:
        fout.write('{} --> {} --> {}\n'.format(sample['loc_before'], sample['act'], sample['loc_after']))

outfile = '{}/{}.map.reversed'.format(args.output_dir, game_name.split('.')[0])
with open(outfile, 'w', encoding='utf-8') as fout:
    for sample in map_list:
        if sample['oppo_direction_valid']:
            fout.write('{} --> {} --> {}, True\n'.format(sample['loc_after'], opposite_direction_dict[sample['act']], sample['loc_before']))
        else:
            fout.write('{} --> {} --> {}, False, {}\n'.format(sample['loc_after'], opposite_direction_dict[sample['act']], sample['loc_before'], sample['description']))

print ('Well Done!')