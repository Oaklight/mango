import matplotlib.pyplot as plt


vertex = {}
current_vertex = None  # tuple (x, y)
vertex_visited = {}  # {(x, y): [step_visited, ...]}
vertex_names = {}  # {(x, y): vertex_name, ...}
vertex_sequence = []  # [(x, y),...]
special_vertices = []  # [(x, y),...]
action_sequence = []  # [(direction, dist, step_num[, special]), ...]

plt.ion()  # Turn on interactive mode
fig, ax = plt.subplots()


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
    is_start = vertex == "A"
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
    global vertex, current_vertex, vertex_visited, vertex_names, vertex_sequence

    init_step = input("Enter the initial step number: ")
    current_vertex = (0, 0)
    vertex_sequence.append(current_vertex)
    vertex_names[current_vertex] = str(init_step)
    vertex_visited[current_vertex] = [init_step]
    
    plot_graph()
    print(f"======== [{init_step}] done ========")


def move(direction, distance, step_num, special=False):
    global vertex, current_vertex, vertex_visited, vertex_names, vertex_sequence

    (x, y) = vertex_names[current_vertex]

    if direction == "north" or direction == "n":
        y += distance
    if direction == "south" or direction == "s":
        y -= distance
    if direction == "east" or direction == "e":
        x += distance
    if direction == "west" or direction == "w":
        x -= distance

    current_vertex = step_num
    vertex_names[current_vertex] = (x, y)
    vertex_sequence.append(current_vertex)
    if special:
        special_vertices.append(current_vertex)

    if (x, y) not in vertex_visited:
        vertex_visited[(x, y)] = [step_num]
    else:
        vertex_visited[(x, y)].append(step_num)

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
        x, y = vertex_names[vertex]
        shape, color = get_shape_color(vertex)
        # draw the vertex on the graph with the given shape and color, and label it with the vertex name
        ax.plot(
            x,
            y,
            marker=shape,
            color=color,
            label=vertex,
            markeredgewidth=1,
            markeredgecolor="black",
            markersize=10,
        )
        ax.annotate(vertex, (x, y), color="black")

        # draw the edge between the previous vertex and the current vertex
        ax.plot([prev_x, x], [prev_y, y], color="black")
        prev_x, prev_y = x, y

    ax.grid(True)

    ax.figure.canvas.draw()
    plt.pause(0.001)
    ax.figure.canvas.flush_events()


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

    print("State saved!")


if __name__ == "__main__":
    init_map()
    while True:
        instruction = safe_input("Enter next step: ").replace(",", " ")
        if instruction == "quit":
            break
        if instruction == "save":
            save_local()
            continue

        elements = [e.strip() for e in instruction.split()]
        print(elements)

        direction, distance, step_num = elements[:3]
        special = False
        if len(elements) == 4:
            special = True
        move(direction, int(distance), int(step_num), special)

    save_local()

# # Example usage:
# initial_step = int(input("Enter the initial step number: "))
# graph_drawer = GraphDrawer(initial_step)

# # Draw the initial point as a blue square
# graph_drawer.draw_vertex("A", marker="s", color="blue")

# print(
#     "\nEnter instructions in the format 'direction, distance, steps' (e.g., 'west, 20, 189')"
# )
# print("For special locations, use '!'. Example: 'west, 20, 300, !'\n")

# while True:
#     instruction = input("Enter next step: ")

#     if not instruction:
#         break

#     parts = instruction.split(", ")
#     direction, distance, steps = parts[:3]

#     distance = int(distance)
#     steps = int(steps)

#     if len(parts) == 4 and parts[3] == "!":
#         graph_drawer.move(direction, distance, steps, mark=True)
#     else:
#         graph_drawer.move(direction, distance, steps)

# # Plot the final graph
# graph_drawer.plot_graph()

# plt.ioff()  # Turn off interactive mode
# plt.show()  # Keep the final plot open until closed by the user
