# color print without extra library, in green
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
