import os
import argparse
from tqdm import tqdm
from jericho import *
from jericho.util import unabbreviate

def gen_walkthrough(args):
    game_name = args.game_name
    env = FrotzEnv("{}/{}".format(args.jericho_path, game_name))

    # walkthrough
    walkthrough_acts = env.get_walkthrough()
    # print ('===> walkthrough_acts: {}'.format(walkthrough_acts))

    # init act
    initial_observation, info = env.reset()
    # print ('init ob: {}, info: {}'.format(initial_observation, info))
    done = False
    # start_moves = info['moves']
    step_num = 0
    act_info = {
        'act': 'Init',
        'observation': initial_observation,
        'step': step_num
    }
    walkthrough_list = []
    walkthrough_list.append(act_info)
    for act in tqdm(walkthrough_acts):
        step_num += 1
        observation, reward, done, info = env.step(act)
        sample_info = {
            'step': step_num,
            'act': unabbreviate(act),
            'observation': observation,
        }
        # print (sample_info)
        walkthrough_list.append(sample_info)
    assert done == True, "Not Done"

    output_dir = args.output_dir + '/' + game_name.split('.')[0]
    if os.path.exists(output_dir) == False:
        os.makedirs(output_dir)

    if args.walk_md:
        outfile = '{}/{}.walkthrough.md'.format(output_dir, game_name.split('.')[0])
        with open(outfile, 'w', encoding='utf-8') as fout:
            fout.write('***\n')
            for sample in walkthrough_list:
                fout.write('# STEP NUM: {}\n## ACT: {}\n## OBSERVATION: {}\n'.format(sample['step'], sample['act'], sample['observation'].strip()))
                fout.write('\n***\n')
    else:
        outfile = '{}/{}.walkthrough'.format(output_dir, game_name.split('.')[0])
        with open(outfile, 'w', encoding='utf-8') as fout:
            fout.write('===========\n')
            for sample in walkthrough_list:
                fout.write('==>STEP NUM: {}\n==>ACT: {}\n==>OBSERVATION: {}\n'.format(sample['step'], sample['act'], sample['observation'].strip()))
                fout.write('\n===========\n')
    print ('Well Done!')

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--game_name", '-g', type=str)
    parser.add_argument("--jericho_path", '-j', type=str, default="./data/z-machine-games-master/jericho-game-suite")
    parser.add_argument("--output_dir", '-odir', type=str, default="./data/maps")
    parser.add_argument("--walk_md", '-md', action='store_true', help='toggle to output walkthrough.md, otherwise output walkthrough.txt')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    print ("Args: {}".format(args))
    gen_walkthrough(args)