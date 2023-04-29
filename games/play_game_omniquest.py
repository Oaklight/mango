from jericho import *
# Create the environment, optionally specifying a random seed

game_name = 'omniquest.z5'
env = FrotzEnv("z-machine-games-master/jericho-game-suite/{}".format(game_name))

# direction dict
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

initial_observation, info = env.reset()
print ('init ob: {}, info: {}'.format(initial_observation, info))
map_list = []
loc_before = 'Large Clearing'
done = False
for act in walkthrough:
    observation, reward, done, info = env.step(act)
    valid_actions = env.get_valid_actions()
    # print('===> act: {}, observation: {}, reward: {}, done: {}, info: {}'.format(act,observation,reward,done,info))
    # print ('==> valid actions: {}'.format(valid_actions))
    if act.lower() in direction_abbrv_vocab:
        observation_abbr = observation.split('\n')[1]

        act = direction_abbrv_dict[act.lower()]
        oppo_act = opposite_direction_dict[act]
        valid_actions = [a for a in valid_actions if a in direction_vocab]
        oppo_direction_valid = (oppo_act in valid_actions)
        if oppo_direction_valid == True:
            desc = 'None'
        else:
            desc = observation

        sample = {
            'loc_before': loc_before,
            'act': act,
            'loc_after': observation_abbr,
            'valid_actions': valid_actions,
            'oppo_direction_valid': oppo_direction_valid,
            'description': desc
        }
        map_list.append(sample)
        print (sample)
        loc_before = observation_abbr

assert done == True
print ('Scored', info['score'], 'out of', env.get_max_score())

outfile = './{}.map'.format(game_name.split('.')[0])
with open(outfile, 'w', encoding='utf-8') as fout:
    for sample in map_list:
        fout.write('{} --> {} --> {}\n'.format(sample['loc_before'], sample['act'], sample['loc_after']))

outfile = './{}.map.reversed'.format(game_name.split('.')[0])
with open(outfile, 'w', encoding='utf-8') as fout:
    for sample in map_list:
        if sample['oppo_direction_valid']:
            fout.write('{} --> {} --> {}, True\n'.format(sample['loc_after'], opposite_direction_dict[sample['act']], sample['loc_before']))
        else:
            fout.write('{} --> {} --> {}, False, {}\n'.format(sample['loc_after'], opposite_direction_dict[sample['act']], sample['loc_before'], sample['description']))

print ('Well Done!')