import os
import argparse
from tqdm import tqdm
from jericho import *
from jericho.util import unabbreviate
import glob


def gen_walkthrough(args):
    game_name = args.game_name
    game_file_path = None
    for game_file in glob.glob(f"{args.jericho_path}/*"):
        if game_name == os.path.splitext(os.path.basename(game_file))[0]:
            game_file_path = game_file
            break
    if game_file_path is None:
        print(f"Game file {game_name} not found in {args.jericho_path}")
        return -1
    env = FrotzEnv(game_file_path)

    # create output dir if not exist
    output_dir = args.output_dir + "/" + game_name.split(".")[0]
    if os.path.exists(output_dir) == False:
        os.makedirs(output_dir)

    # use provided walkthrough_acts or load from game env
    walkthrough_acts = []
    if args.walk_acts:
        # with open(args.walk_acts, "r", encoding="utf-8") as fin:
        with open(
            f"{output_dir}/{game_name}.walkthrough_acts", "r", encoding="utf-8"
        ) as fin:
            for line in fin:
                # sometimes there are void action, use whatever after ":"
                act = line.split(":")[1].strip()
                walkthrough_acts.append(act)
        print(
            f"Walkthrough Acts provided has been loaded, total {len(walkthrough_acts)} steps"
        )
    else:
        # walkthrough
        walkthrough_acts = env.get_walkthrough()

    # init act
    initial_observation, info = env.reset()
    # print ('init ob: {}, info: {}'.format(initial_observation, info))
    done = False
    # start_moves = info['moves']
    step_num = 0
    act_info = {"act": "Init", "observation": initial_observation, "step": step_num}
    walkthrough_list = []
    walkthrough_list.append(act_info)
    for act in tqdm(walkthrough_acts):
        step_num += 1
        observation, reward, done, info = env.step(act)
        sample_info = {
            "step": step_num,
            "act": unabbreviate(act),
            "observation": observation,
        }
        # print (sample_info)
        walkthrough_list.append(sample_info)
    assert done == True, "Not Done"

    # 1. output walkthrough
    outfile = "{}/{}.walkthrough".format(output_dir, game_name.split(".")[0])
    with open(outfile, "w", encoding="utf-8") as fout:
        fout.write("===========\n")
        for sample in walkthrough_list:
            fout.write(
                "==>STEP NUM: {}\n==>ACT: {}\n==>OBSERVATION: {}\n".format(
                    sample["step"], sample["act"], sample["observation"].strip()
                )
            )
            fout.write("\n===========\n")
    print("Well Done!")

    # 2. output walkthrough_acts as a numbered dict, index+1 as step number
    with open(
        "{}/{}.walkthrough_acts".format(output_dir, game_name.split(".")[0]),
        "w",
        encoding="utf-8",
    ) as fout:
        for i, act in enumerate(walkthrough_acts):
            fout.write("{}: {}\n".format(i + 1, act))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--game_name", "-g", type=str)
    parser.add_argument(
        "--jericho_path",
        "-j",
        type=str,
        default="./data/z-machine-games-master/jericho-game-suite",
    )
    parser.add_argument("--output_dir", "-odir", type=str, default="./data/maps")
    parser.add_argument(
        "--walk_acts",
        "-acts",
        action="store_true",
        default=False,
        help="Override walkthrough acts with *.walkthrough_acts file",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print("Args: {}".format(args))
    gen_walkthrough(args)
