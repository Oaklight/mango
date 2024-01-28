import argparse
import os
import sys

from jericho.util import unabbreviate

from tqdm import tqdm

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from gen_moves.utils import load_env, load_walkthrough_acts


def gen_walkthrough(args):
    env = load_env(args)

    # use provided walkthrough_acts or load from game env
    walkthrough_acts = load_walkthrough_acts(args, env, keep_again=False)

    # init act
    initial_observation, _ = env.reset()

    done = False
    step_num = 0
    sample_info = {
        "step": step_num,
        "act": "Init",
        "observation": initial_observation,
    }

    walkthrough_list = []
    walkthrough_list.append(sample_info)
    for act in tqdm(walkthrough_acts):
        step_num += 1
        observation, _, done, _ = env.step(act)
        sample_info = {
            "step": step_num,
            "act": unabbreviate(act),
            "observation": observation,
        }
        # print (sample_info)
        walkthrough_list.append(sample_info)
    assert done == True, "Not Done"

    # 1. output walkthrough
    outfile = "{}/{}.walkthrough".format(args.output_dir, args.game_name.split(".")[0])
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
        "{}/{}.walkthrough_acts".format(args.output_dir, args.game_name.split(".")[0]),
        "w",
        encoding="utf-8",
    ) as fout:
        for i, act in enumerate(walkthrough_acts):
            fout.write("{}: {}\n".format(i + 1, act))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--game_name", "-g", type=str, required=True)
    parser.add_argument("--jericho_path", "-j", type=str, required=True)
    parser.add_argument("--output_dir", "-odir", type=str, required=True)
    parser.add_argument(
        "--walk_acts",
        "-acts",
        action="store_true",
        default=False,
        help="Override walkthrough acts with *.walkthrough_acts file",
    )
    args = parser.parse_args()

    args.game_name_raw = args.game_name.split(".")[0]
    args.output_dir = f"{args.output_dir}/{args.game_name_raw}"

    # create output dir if not exist
    if os.path.exists(args.output_dir) == False:
        os.makedirs(args.output_dir)

    return args


if __name__ == "__main__":
    args = parse_args()
    print("Args: {}".format(args))
    gen_walkthrough(args)
