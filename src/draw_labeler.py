import argparse

import matplotlib.pyplot as plt


vertex = {}
current_vertex = None  # current coordinates, (x, y)
vertex_sequence = []  # sequence of vertices for plotting, [(x, y),...]
vertex_names = {}  # dict of first visit name, for display {(x, y): vertex_name, ...}
vertex_visited = {}  # dict of visited steps per vertex, {(x, y): [step_visited, ...]}
special_vertices = []  # list of special vertices, [(x, y),...]
action_sequence = (
    []
)  # sequence of actions, [(direction, dist, step_num[, special]), ...]

plt.ion()  # Turn on interactive mode
fig, ax = None, None

HELP_MSG = """
Interactively label a maze-like map. A maze-like map is a grid of vertices
with a start vertex and a goal vertex. The start vertex is marked with a
blue sqaure, the goal vertex is marked with a purple diamond, and all other vertices are
marked with a circle. The current vertex is marked as a green plus.

The user can move the current vertex to a new location by specifying the
direction and distance to move. The direction can be one of the four
cardinal directions (north, south, east, west), or the special direction
"save" to save the current map, "quit" or "done" to quit the program.


Available instructions:
    # you can use space or comma to separate the instruction elements
    # normal instructions
        - north/n distance step_idx
        - south/s distance step_idx
        - east/e distance step_idx
        - west/w distance step_idx
    # special instruction
    - save
    - quit
    - done

Examples:
    - n 10 191
    - south 1 203
    - save
    - quit
    - done
    
"""

ACTIONS = [
    "north",
    "n",
    "south",
    "s",
    "east",
    "e",
    "west",
    "w",
]


def safe_input(prompt):
    input_str = input(prompt).strip()
    while input_str == "":
        input_str = input(prompt).strip()

    return input_str.lower()


# update safe_input to ignore interrupt


# https://matplotlib.org/stable/api/markers_api.html
SHAPES = {
    "normal": "o",  # circle
    "start": "s",  # square
    "special": "d",  # thin diamond
    "current": "P",  # plus (filled)
}

# https://matplotlib.org/stable/gallery/color/named_colors.html#sphx-glr-gallery-color-named-colors-py
COLORS = {
    "normal": "navajowhite",
    "start": "dodgerblue",
    "current": "lime",
    "special": "magenta",
}


def _get_shape(which):
    if which == "normal":
        return SHAPES["normal"]
    elif which == "start":
        return SHAPES["start"]
    elif which == "special":
        return SHAPES["special"]
    elif which == "current":
        return SHAPES["current"]
    else:
        raise Exception("Invalid shape")


def _get_color(which):
    if which == "normal":
        return COLORS["normal"]
    elif which == "start":
        return COLORS["start"]
    elif which == "current":
        return COLORS["current"]
    elif which == "special":
        return COLORS["special"]
    else:
        raise Exception("Invalid color")


def get_shape_color(vertex):
    is_special = vertex in special_vertices
    is_current = vertex == current_vertex
    is_start = vertex == (0, 0)
    if is_special:
        color = _get_color("special")
        shape = _get_shape("special")
    elif is_current:
        color = _get_color("current")
        shape = _get_shape("current")
    elif is_start:
        color = _get_color("start")
        shape = _get_shape("start")
    else:
        color = _get_color("normal")
        shape = _get_shape("normal")

    return shape, color


def init_map():
    global current_vertex, vertex_sequence, vertex_names, vertex_visited, special_vertices, fig, ax

    init_step = input("Enter the initial step number: ")
    current_vertex = (0, 0)
    vertex_sequence.append(current_vertex)  # for plotting
    vertex_names[current_vertex] = str(init_step)  # for display
    vertex_visited[current_vertex] = [init_step]  # for visit record

    fig, ax = plt.subplots()
    plot_graph()
    print(f"======== [{init_step}] done ========")


def move(direction, distance, step_num, special=False):
    global current_vertex, vertex_sequence, vertex_names, vertex_visited, special_vertices, action_sequence

    (x, y) = current_vertex

    if direction == "north" or direction == "n":
        y += distance
    if direction == "south" or direction == "s":
        y -= distance
    if direction == "east" or direction == "e":
        x += distance
    if direction == "west" or direction == "w":
        x -= distance

    current_vertex = (x, y)
    vertex_sequence.append(current_vertex)  # for plotting
    vertex_names[current_vertex] = str(step_num)  # for display
    if special:
        special_vertices.append(current_vertex)
    action_sequence.append((direction, distance, step_num, special))

    if current_vertex not in vertex_visited:
        vertex_visited[current_vertex] = [step_num]
    else:
        vertex_visited[current_vertex].append(step_num)

    plot_graph()
    print(f"======== [{step_num}] done ========")


def plot_graph():
    # for start, end in zip(vertices.values(), list(vertices.values())[1:]):
    #     ax.plot([start[0], end[0]], [start[1], end[1]], color='black')

    # clear the graph
    ax.cla()

    # always draw the start vertex
    ax.plot(0, 0, marker="s", color="blue", label="A")

    prev_x, prev_y = 0, 0
    for vertex in vertex_sequence:
        x, y = vertex
        shape, color = get_shape_color(vertex)
        # draw the vertex on the graph with the given shape and color, and label it with the vertex name
        ax.plot(
            x,
            y,
            marker=shape,
            color=color,
            label=vertex_names[vertex],
            markeredgewidth=1,
            markeredgecolor="black",
            markersize=10,
        )
        ax.annotate(vertex_names[vertex], (x, y), color="black")

        # draw the edge between the previous vertex and the current vertex
        ax.plot([prev_x, x], [prev_y, y], color="black")
        prev_x, prev_y = x, y

    ax.grid(True)

    ax.figure.canvas.draw()
    plt.pause(0.001)
    ax.figure.canvas.flush_events()


def get_args():
    parser = argparse.ArgumentParser(description=HELP_MSG)
    return parser.parse_args()


def save_local():
    # save the graph
    plt.savefig("graph.png")
    # save visited vertices
    with open("vertex_visited.txt", "w") as f:
        for vertex in vertex_visited.keys():
            f.write(f"{vertex},{vertex_visited[vertex]}\n")

    # save special vertices
    with open("special_vertices.txt", "w") as f:
        for vertex in special_vertices:
            f.write(f"{vertex}\n")

    # save action sequence
    with open("action_sequence.txt", "w") as f:
        for action in action_sequence:
            line = ", ".join([str(e) for e in action])
            f.write(line + "\n")

    print("State saved!")


if __name__ == "__main__":
    get_args()

    init_map()
    while True:
        instruction = safe_input("Enter next step: ").replace(",", " ")
        if instruction == "quit" or instruction == "done":
            break
        if instruction == "save":
            save_local()
            continue

        elements = [e.strip() for e in instruction.split()]
        if elements[0] not in ACTIONS:
            print("Invalid action")
            continue
        if elements[1].isdigit() is False:
            print("Invalid distance")
            continue
        if elements[2].isdigit() is False:
            print("Invalid step number")
            continue
        print(elements)

        direction, distance, step_num = elements[:3]
        special = False
        if len(elements) == 4:
            special = True
        move(direction, int(distance), int(step_num), special)

    save_local()
