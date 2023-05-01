# color print without extra library, in green
import argparse


def printGreen(text, inline=False):
    if not inline:
        print("\033[92m {}\033[00m".format(text))
    else:
        print("\033[92m {}\033[00m".format(text), end="")


# , red, bold black
def printRed(text, inline=False):
    if not inline:
        print("\033[91m {}\033[00m".format(text))
    else:
        print("\033[91m {}\033[00m".format(text), end="")


# , bold black
def printBlack(text, inline=False):
    if not inline:
        print("\033[1m {}\033[00m".format(text))
    else:
        print("\033[1m {}\033[00m".format(text), end="")


# general color print, receive txt and color
def printColor(text, color, inline=False):
    if color == "green" or color == "g":
        printGreen(text, inline)
    elif color == "red" or color == "r":
        printRed(text, inline)
    elif color == "black" or color == "b":
        printBlack(text, inline)
    else:
        print(text, end="" if inline else "\n")


# general input with color, receive txt and color
def inputColor(text, color, inline=False):
    if color == "green" or color == "g":
        printGreen(text, inline)
    elif color == "red" or color == "r":
        printRed(text, inline)
    elif color == "black" or color == "b":
        printBlack(text, inline)
    else:
        print(text, end="" if inline else "\n")
    return input()


# a markdown line is either H1, H2, plain text, or empty.
# return type and content.
# There is no other type of line in the markdown file
# raise error if line is not one of the four types
def parseLine(line: str) -> tuple[str, str]:
    strType = None
    content = None
    line = line.strip()
    if line == "":
        strType = "empty"
        content = ""
    elif line.startswith("# "):
        strType = "H1"
        content = line[2:]
    elif line.startswith("## "):
        strType = "H2"
        content = line[3:]
    else:
        strType = "plain"
        content = line

    return strType, content.strip().lower()


def extractDirectionText(line: str) -> tuple[str, str]:
    action, toWhere = [each.strip().lower() for each in line.split("-->")]
    return action, toWhere


def extractItemText(line: str) -> tuple[str, str, str]:
    name = line.split("(")[0].strip()
    description = line.split("(")[1].split(")")[0].strip()
    actions = line.split("[")[1].split("]")[0].strip()
    return name, description, actions


def get_args_all2all():
    parser = argparse.ArgumentParser()
    parser.add_argument("--map", "-m", type=str, required=True)

    # mutually exclusive group for actions and reverse_map
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--actions", "-a", type=str)
    group.add_argument("--reverse_map", "-r", type=str)

    parser.add_argument("--output_dir", "-odir", type=str)
    args = parser.parse_args()

    # output_dir is default to be the same as map file
    if args.output_dir is None:
        args.output_dir = "/".join(args.map.split("/")[:-1]) + "/"
    if args.output_dir[-1] != "/":
        args.output_dir += "/"

    # output_path is default to be the same as map file, with .all2all.json
    args.output_path = (
        args.output_dir + args.map.split("/")[-1].split(".")[0] + ".all2all.json"
    )

    print_args(args)
    return args


def print_args(args):
    # for each of args' attributes, print it out. Using vars(args) returns a dict
    for k, v in vars(args).items():
        printColor(f"\t{k}: ", "b", inline=True)
        print(v)


def confirm_continue():
    confirm = inputColor("Continue? (y/n) ", "b", inline=True)
    if confirm == "y":
        pass
    else:
        printColor("Aborted!", "b")
        exit(1)
