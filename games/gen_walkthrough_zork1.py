from jericho import *
# Create the environment, optionally specifying a random seed
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--jericho_path", '-j', type=str, default="z-machine-games-master/jericho-game-suite")
parser.add_argument("--output_dir", '-odir', type=str, default="./maps")
parser.add_argument("--walk_md", '-md', action='store_true', help='toggle to output walkthrough.md, otherwise output walkthrough.txt')
args = parser.parse_args()

game_name = 'zork1.z5'
env = FrotzEnv("{}/{}".format(args.jericho_path, game_name))

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

# walkthrough
walkthrough = env.get_walkthrough()
walkthrough = [direction_abbrv_dict[w.lower()] if w.lower() in direction_vocab_abbrv else w.lower() for w in walkthrough]
print ('===> walkthrough: {}'.format(walkthrough))

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

assert done == True
print ('Scored', info['score'], 'out of', env.get_max_score())

if args.walk_md:
    outfile = '{}/{}.walkthrough.md'.format(args.output_dir, game_name.split('.')[0])
    with open(outfile, 'w', encoding='utf-8') as fout:
        fout.write('***\n')
        for sample in walkthrough_list:
            fout.write('# STEP NUM: {}\n## ACT: {}\n## OBSERVATION: {}\n'.format(sample['step'], sample['act'], sample['observation'].strip()))
            fout.write('\n***\n')
else:
    outfile = '{}/{}.walkthrough'.format(args.output_dir, game_name.split('.')[0])
    with open(outfile, 'w', encoding='utf-8') as fout:
        fout.write('===========\n')
        for sample in walkthrough_list:
            fout.write('==>STEP NUM: {}\n==>ACT: {}\n==>OBSERVATION: {}\n'.format(sample['step'], sample['act'], sample['observation'].strip()))
            fout.write('\n===========\n')

print ('Well Done!')