"""
# https://jericho-py.readthedocs.io/en/latest/index.html
"""

import os
import datetime
import argparse
import json

from jericho import *

def play_game(args):
    jericho_path = args.jericho_path
    game_name = args.game_name

    # env
    env = FrotzEnv("{}/{}".format(jericho_path, game_name))
    
    # init
    initial_observation, info = env.reset()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--game_name", '-g', type=str, default="zork1.z5")
    parser.add_argument("--jericho_path", '-j', type=str, default="./z-machine-games-master/jericho-game-suite")
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    print ("Args: {}".format(args))
    play_game(args)