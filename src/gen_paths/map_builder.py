import argparse
from utils import (
    input_color,
    print_color,
    parse_line,
    extract_direction_text,
    extract_item_text,
)

"""
map should be a list of locations
location should have name, description, directions, items
direction should have action, to_where
item should have name, description, action

for simplicity, we use markdown to serialize the map
each location is a H1 title, with H2 titles for directions and items
direction entry are lines plain text under H2 title "directions", where each line follows the format 'action --> to_where'
item entry are lines of plain text under H2 title "items", where each line follows the format 'name (description) [action]'
note, each location must have entries under directions, but may not have entries under items

for example
```markdown
# west of house
## directions
n --> north of house
w --> forest 1
s --> south of house
## items
door (description of door) [open, close, lock, unlock]

# south of house
## directions
w --> west of house
s --> forest 2
e --> behind house
## items

# behind house
## directions
n --> north of house
w --> kitchen
s --> south of house
e --> clearing
enter house --> kitchen
## items

...
```
"""


# struct of a direction, has action and to_where
class Direction:
    def __init__(self, action, to_where):
        self.action = abbr2full(action)
        self.to_where = to_where

    def __repr__(self) -> str:
        return f"{self.action} --> {self.to_where}"


# struct of items, may have action and description
class Item:
    def __init__(self, name, description="", action: str = None):
        self.name = name
        self.description = description
        # TODO: action should be a list of actions, take care later
        self.action = action

    def __repr__(self) -> str:
        return f"{self.name} ({self.description}) [{self.action}]"


# struct of a location, must have directions and may have items, optional description
class Location:
    def __init__(self, name, description=""):
        self.name = name
        self.description = description
        self.directions = []
        self.items = []

    # return Location struct as a markdown string, where name is H1 title, directions and items are H2 titles, their entries are plain text, serialize use each struct.__repr__
    def __repr__(self) -> str:
        # serialize directions
        # sort directions and items by action and name
        self.directions.sort(key=lambda direction: direction.action)
        self.items.sort(key=lambda item: item.name)

        directions = "\n".join([direction.__repr__() for direction in self.directions])
        # serialize items
        items = "\n".join([item.__repr__() for item in self.items])
        # serialize location
        location = f"# {self.name}\n## directions\n{directions}\n## items\n{items}"
        return location

    def addDirection(self):
        # self.directions.append(direction)
        # keep prompt for directions if not recieve "done"
        # print black bar
        print_color("--------------------------------------------------", "b")
        while True:
            print_color(f"Enter a DIRECTION for [{self.name}]", "g")
            # prompt to receive a direction
            # add new direction to directions
            action = input_color("action? ", "g", inline=True)
            # if action is "done", break
            if (
                action == "done"
                or action == "no more"
                or action == "none"
                or action == ""
            ):
                break

            to_where = input_color("to where? ", "g", inline=True)
            newDirection = Direction(action, to_where)
            self.directions.append(newDirection)
            print()
        print()

    def addItem(self):
        # self.items.append(item)
        # keep prompt for items if not recieve "no more" or "none"
        # print black bar
        print_color("--------------------------------------------------", "b")
        while True:
            # prompt to receive a item
            print_color(f"Enter an ITEM for [{self.name}] ", "r")
            # if item is "done", break
            item = input_color("what item?: ", "r", inline=True)
            if item == "no more" or item == "none" or item == "done" or item == "":
                break

            action = input_color("action available? ", "r", inline=True)
            description = input_color("Any item description? ", "r")
            newItem = Item(item, action=action, description=description)
            self.items.append(newItem)
            print()
        print()


# function to add a location with details
def addLocation(gameMapDict: dict = None):
    updateFlag = False

    name = input_color("Enter a LOCATION name: ", "b", inline=True)
    if name == "map done" or name == "no more" or name == "done" or name == "":
        return None

    # check if location already exist, if so it's an update
    if gameMapDict is not None and name in gameMapDict:
        print_color(f"Location [{name}] already EXISTS!", "b")
        newLocation = gameMapDict[name]
        updateFlag = True
        print(newLocation)
        print_color(f"Update location [{name}]", "b")
    else:
        description = input_color("Any LOCATION description? ", "b")
        newLocation = Location(name, description)

    # FIXME: assume adding new entries, we don't check if entry already exist
    # add directions and items
    newLocation.addDirection()
    newLocation.addItem()

    # print_color(f"Location [{name}] added: {newLocation}", 'b')
    # print new location
    print_color(f"Location [{name}] added!", "b")
    print()
    return newLocation, updateFlag


# function to build map and persist to map.md
def buildMap(mapMarkdown: str = "../data/map.md"):
    gameMap = []

    # load map if exist, otherwise create empty markdown
    try:
        with open(mapMarkdown, "r") as f:
            gameMap = loadMap(mapMarkdown)
    except FileNotFoundError:
        with open(mapMarkdown, "w") as f:
            f.write("")

    # get a dict view into gameMap for fast lookup
    gameMapDict = {location.name: location for location in gameMap}

    # keep prompt for locations if not recieve "map done" or "no more"
    while True:
        # print current available locations' names
        print_color("--------------------------------------------------", "b")
        print_color("Current available locations: ", "b")
        # print_color(", ".join([location.name for location in gameMap]), 'b')
        # print each line as a bullet point, with their available directions' action and item names
        for location in gameMap:
            # print(f"- {location.name}")
            print_color(f"- {location.name}: ", "b", inline=True)
            print_color("|directions| ", "g", inline=True)
            print(f"{[direction.action for direction in location.directions]} ", end="")
            if len(location.items) > 0:
                # ptrString += f"|items| {[item.name for item in location.items]}"
                print_color("|items| ", "r", inline=True)
                print(f" {[item.name for item in location.items]} ")
            else:
                print()
        print_color("--------------------------------------------------", "b")
        newLocation, updateFlag = addLocation()
        if newLocation is None:
            break

        if updateFlag:
            # update location in gameMap via gameMapDict
            gameMapDict[newLocation.name] = newLocation
            gameMap = list(gameMapDict.values())
        else:
            gameMap.append(newLocation)

        # persist every time a new location is added
        persistMap(gameMap, mapMarkdown)

    # persist gameMap to map.md once more
    persistMap(gameMap, mapMarkdown)


# function to load a map.md to list of Location
def loadMap(mapMarkdown: str = "../data/map.md"):
    # mode is either "location", "directions", or "items"
    mode = "location"
    # load map.md
    with open(mapMarkdown, "r") as f:
        # read lines
        lines = f.readlines()

    # parse lines
    gameMap = []
    newLocation = None
    # append to gameMap at end of lines or when new location is created
    for line in lines:
        str_type, content = parse_line(line)
        # print(str_type, content)
        # if line is H1 title, it's a new location, create new location, with title as name, skip description
        if str_type == "H1":
            name = content
            newLocation = Location(name)
            mode = "location"
        # if line is H2 title, it's directions or items
        if str_type == "H2":
            if content == "directions":
                mode = "directions"
            elif content == "items":
                mode = "items"
        # if line is plain text, it's a direction or item, check mode to decide
        if str_type == "plain":
            if mode == "directions":
                action, to_where = extract_direction_text(content)
                newDirection = Direction(action, to_where)
                newLocation.directions.append(newDirection)
            elif mode == "items":
                name, description, action = extract_item_text(content)
                newItem = Item(name, description, action)
                newLocation.items.append(newItem)
        if str_type == "empty":
            if newLocation is not None:
                gameMap.append(newLocation)
                newLocation = None
            else:
                # continuous empty lines, skip
                continue

    # append last location
    if newLocation is not None:
        gameMap.append(newLocation)

    return gameMap


def persistMap(gameMap: list, mapMarkdown: str = "../data/map.md"):
    # sort gameMap by name
    gameMap.sort(key=lambda location: location.name)
    # persist gameMap to map.md
    with open(mapMarkdown, "w") as f:
        f.write("\n".join([location.__repr__() for location in gameMap]))


def abbr2full(abbr: str) -> str:
    # # check if it's abbr or full name
    if abbr not in ["n", "s", "e", "w", "ne", "nw", "se", "sw", "u", "d"]:
        return abbr

    # convert abbr to full name
    if abbr == "n":
        return "north"
    elif abbr == "s":
        return "south"
    elif abbr == "e":
        return "east"
    elif abbr == "w":
        return "west"
    # including combinations
    elif abbr == "ne":
        return "northeast"
    elif abbr == "nw":
        return "northwest"
    elif abbr == "se":
        return "southeast"
    elif abbr == "sw":
        return "southwest"
    # including vertical directions
    elif abbr == "u":
        return "up"
    elif abbr == "d":
        return "down"
    else:
        return None


# main test
if __name__ == "__main__":
    # location = addLocation()
    # # save to markdown
    # with open("map.md", "w") as f:
    #     f.write(location.__repr__())

    # gameMap = loadMap(mapMarkdown)
    # print(gameMap)

    # build map test
    # argparse to get map.md, it's a required argument
    parser = argparse.ArgumentParser()
    parser.add_argument("--map", help="map markdown file", default="../data/map.md")
    args = parser.parse_args()
    mapMarkdown = args.map
    print_color(f"map markdown file: {mapMarkdown}", "b")
    # prompt to confirm before continue

    confirm = input_color("Continue? (y/n) ", "b", inline=True)
    if confirm == "y":
        buildMap(mapMarkdown)
    else:
        print_color("Aborted!", "b")
        exit(1)
