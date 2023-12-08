import logging

import networkx as nx
from matplotlib import pyplot as plt

# Create an empty multidigraph
G = nx.MultiDiGraph()
fig = None  # for visualization
ax = None  # for visualization

# Initialize game state
# a "location" is a node in the graph, and an "action" is a directed edge from one location to another
# a location is determined by a start location and sequence of actions
# a location is labeled using unique id, and alias_dict[location_id] = [alias1, alias2,...]
# alias1, alias2,... are aliases of the location
# edge (location_id1, location_id2) has attribute "action". we can access it by G[location_id1][location_id2]["action"]

alias_dict = {}
revert_alias_dict = {}
step_dict = {}
current_id = 0
current_loc = ""


def safe_input(prompt):
    input_str = input(prompt).strip()
    while input_str == "":
        input_str = input(prompt).strip()

    return input_str.lower()


def get_reverse_action(action):
    if action == "east":
        return "west"
    elif action == "west":
        return "east"
    elif action == "north":
        return "south"
    elif action == "south":
        return "north"
    elif action == "northeast":
        return "southwest"
    elif action == "northwest":
        return "southeast"
    elif action == "up":
        return "down"
    elif action == "down":
        return "up"
    elif action == "in":
        return "out"
    elif action == "out":
        return "in"


#  get a dict of this above mapping
action_dict = {}
for action in [
    "east",
    "west",
    "north",
    "south",
    "northeast",
    "northwest",
    "up",
    "down",
    "in",
    "out",
]:
    action_dict[action] = get_reverse_action(action)


def revert_alias_dict_update():
    global alias_dict
    global revert_alias_dict

    for key, value in alias_dict.items():
        for alias in value:
            revert_alias_dict[alias] = key


def update_alias_dict(next_id, next_loc):
    global alias_dict
    global revert_alias_dict

    if next_id not in alias_dict:
        alias_dict[next_id] = set([next_loc])
    else:
        alias_dict[next_id].add(next_loc)

    revert_alias_dict_update()


def update_G(next_loc, action, step_num):
    global G
    global current_id
    global current_loc
    global revert_alias_dict
    global alias_dict
    global step_dict

    is_updated = False  # whether G is updated with this new location

    # next_loc may be:
    # 1. an alias of existing location, find and return the id of the location
    neighbors = list(G.neighbors(current_id))
    neighbors_acts = [G[current_id][n][0]["action"] for n in neighbors]

    # action leads us to existing location
    if action in neighbors_acts:
        next_id = neighbors[neighbors_acts.index(action)]

    # action never encountered, might be new location or alias of existing location (loop!)
    elif next_loc in revert_alias_dict:
        next_id = revert_alias_dict[next_loc]

    # 2. a new location, create a new location and return the id of the location
    else:
        is_updated = True
        next_id = len(alias_dict)
        G.add_node(next_id)
        G.add_edge(current_id, next_id, action=action)
        # add reverse edge
        G.add_edge(next_id, current_id, action=get_reverse_action(action))

    update_alias_dict(next_id, next_loc)

    # update step_dict
    step_dict[step_num] = (current_loc, next_loc, action)

    # update current location
    current_loc = next_loc
    current_id = next_id

    # print where you are
    print(f"You are now at [STEP {step_num}](id {next_id})[{next_loc}]")
    # print alias of current location
    print(alias_dict[current_id])
    print()

    return is_updated


# def merge_path():
#     global G
#     global current_id
#     global current_loc
#     global revert_alias_dict
#     global alias_dict
#     global step_dict

#     if


def init_G(init_loc):
    global G
    global current_id
    global current_loc
    global revert_alias_dict

    next_id = 0

    current_loc = init_loc
    update_alias_dict(next_id, init_loc)
    G.add_node(next_id)
    current_id = next_id

    print(f"You are now at ({next_id})[{init_loc}]")
    print()


def plot_graph():
    global G
    global ax, fig

    ax.clear()

    # Draw the graph
    pos = nx.spring_layout(G)
    nx.draw(
        G,
        pos,
        # with_labels=True,
        node_size=1000,
        node_color="skyblue",
        font_size=8,
        connectionstyle="arc3,rad=0.2",
        ax=ax,
    )

    # Get the edge labels as a dictionary
    edge_labels = {
        (u, v): f"({u}->{v})\n{d['action']}" for u, v, d in G.edges(data=True)
    }

    # Draw the edge labels
    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=edge_labels,
        font_color="red",
        label_pos=0.75,
        rotate=False,
        ax=ax,
    )

    node_labels = {n: f"{n}[{list(alias_dict[n])[0]}]" for n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=10, ax=ax)

    fig.canvas.draw()
    fig.canvas.flush_events()


# Initialize game if it's the first time playing
def initialize_game():
    global G
    global ax
    global fig

    if G.number_of_nodes() == 0:
        print("Welcome to the game! Please provide your current location.")
        current_loc = safe_input("Your current location: ")
        init_G(current_loc)

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.axis("off")
    plt.ion()
    plt.show()

    plot_graph()


def end_game():
    print("Thank you for playing!")
    print("Your game history is:")
    with open("game_history.txt", "w") as f:
        for step_k, step_v in step_dict.items():
            hist_str = f"{step_k} ({step_v[0]}, {step_v[1]} || {step_v[2]})\n"
            print(hist_str)
            f.write(hist_str)

    # dump alias dict
    with open("alias_dict.txt", "w") as f:
        for key, value in alias_dict.items():
            f.write(f"{key}: {value}\n")
    with open("revert_alias_dict.txt", "w") as f:
        for key, value in revert_alias_dict.items():
            f.write(f"{key}: {value}\n")


if __name__ == "__main__":
    # Start the game
    initialize_game()
    while True:
        step_num = safe_input("[which step?] ")
        # guard against invalid input
        while not step_num.isdigit():
            step_num = safe_input("[which step?] ")

        action = safe_input("[next action?] ")
        # guard against invalid input
        double_input = False
        while action not in action_dict.keys() and not double_input:
            again_action = safe_input("[next action?] ")
            if again_action == action:
                double_input = True
                action = again_action

        if (
            action.lower() == "quit"
            or action.lower() == "exit"
            or action.lower() == "done"
        ):
            break
        else:
            is_updated = update_G(safe_input("[next location?] "), action, step_num)

        print(f"=============== [{step_num}] done ===============")
        if is_updated:
            plot_graph()

    end_game()
