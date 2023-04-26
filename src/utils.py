# color print without extra library, in green
def printGreen(text):
    print("\033[92m {}\033[00m".format(text))


# , red, bold black
def printRed(text):
    print("\033[91m {}\033[00m".format(text))


# , bold black
def printBlack(text):
    print("\033[1m {}\033[00m".format(text))


# general color print, receive txt and color
def printColor(text, color):
    if color == "green" or color == "g":
        printGreen(text)
    elif color == "red" or color == "r":
        printRed(text)
    elif color == "black" or color == "b":
        printBlack(text)
    else:
        print(text)


# general input with color, receive txt and color
def inputColor(text, color):
    if color == "green" or color == "g":
        printGreen(text)
    elif color == "red" or color == "r":
        printRed(text)
    elif color == "black" or color == "b":
        printBlack(text)
    else:
        print(text)
    return input()


# a markdown line is either H1, H2, plain text, or empty.
# return type and content.
# There is no other type of line in the markdown file
# raise error if line is not one of the four types
def parseLine(line: str) -> tuple[str, str]:
    strType = None
    content = None
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