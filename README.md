# gamegpt_utils

gamegpt graph utils

<!-- TOC -->

- [gamegpt_utils](#gamegpt_utils)
    - [1. Games & Files](#1-games--files)
    - [2. Code specs](#2-code-specs)
        - [2.1. Depandencies](#21-depandencies)
        - [2.2. Major functions](#22-major-functions)
    - [3. How to run?](#3-how-to-run)
    - [4. Data format](#4-data-format)
        - [4.1. *.map](#41-map)
        - [4.2. *.actions](#42-actions)
        - [4.3. *.verify](#43-verify)
        - [4.4. *.map.reversed generated](#44-mapreversed-generated)
        - [4.5. *.all2all_paths.md generated](#45-all2all_pathsmd-generated)
        - [4.6. *.all2all_shortest_paths.md generated](#46-all2all_shortest_pathsmd-generated)

<!-- /TOC -->

## Games & Files

<!-- - zork1
  - map: [zork1.map](./data/zork1.map)
  - map.reversed: [zork1.map.reversed](./data/zork1.map.reversed)
  - actions: [zork1.actions](./data/zork1.actions)
  - all2all paths: [zork1.all2all_paths.md](./data/zork1.all2all_paths.md)
  - all2all shortest paths: [zork1.all2all_shortest_paths.md](./data/zork1.all2all_shortest_paths.md)
- omniquest
  - map: [omniquest.map](./data/omniquest.map)
  - map.reversed: [omniquest.map.reversed](./data/omniquest.map.reversed)
  - actions: [omniquest.actions](./data/omniquest.actions)
  - all2all paths: [omniquest.all2all_paths.md](./data/omniquest.all2all_paths.md)
  - all2all shortest paths: [omniquest.all2all_shortest_paths.md](./data/omniquest.all2all_shortest_paths.md)
 -->
<!-- make above into a table -->
| game | map | map.reversed | actions | all2all paths | all2all shortest paths |
| --- | --- | --- | --- | --- | --- |
| zork1 | [zork1.map](./data/zork1.map) | [zork1.map.reversed](./data/zork1.map.reversed) | [zork1.actions](./data/zork1.actions) | [zork1.all2all_paths.md](./data/zork1.all2all_paths.md) | [zork1.all2all_shortest_paths.md](./data/zork1.all2all_shortest_paths.md) |
| omniquest | [omniquest.map](./data/omniquest.map) | [omniquest.map.reversed](./data/omniquest.map.reversed) | [omniquest.actions](./data/omniquest.actions) | [omniquest.all2all_paths.md](./data/omniquest.all2all_paths.md) | [omniquest.all2all_shortest_paths.md](./data/omniquest.all2all_shortest_paths.md) |

## Code specs

### Depandencies

- networkx: `pip install networkx`
- openai: `pip install openai`
- matplotlib: `pip install matplotlib`

### Major functions

- [`digraph.py`](./src/digraph.py)
  - graph utils:
    - `build_graph_from_file(pathFile: str = "data/gameName.map" actionFile: str = "data/gameName.actions", verbose: bool = True)`
    - `get_opposite_direction(direction: str)`
    - `plot_graph(g: object)`
    - `get_edge_direction(G, n1, n2)`
    - ~~`query_chatgpt(prompt, message)`~~ (deprecated)
    - `load_valid_actions(actionFile)`
  - shortest path related
    - `get_shortest_path(g: object, src: str, dst: str)`
    - `print_path(g: object, path: list, verbose: bool = True)`
  - all paths related
    - `get_all_paths(g: object, src: str, dst: str)`
    - `print_all_paths(g: object, all_paths: list, verbose: bool = True)`
  - verify path related
    - `verify_path(g: object, srcNode, dstNode, paths2verify: list)`
    - `parse_path(pathFile: str = "data/path2.verify")`
    - `same_direction_test(given_direction: str, proposed_direction: str)`

- [`map_builder.py`](./src/map_builder.py): build game map from a list of paths interactively, dump as markdown.
  > this module is in beta testing
  - sample of zork1 map: [map.md](./data/map.md)

- [`utils.py`](./src/utils.py): common util functions

## How to run?

1. shortest path btw any two nodes: [test_shortest_path.py](./src/test_shortest_path.py)
2. all paths btw any two nodes, sorted by path length: [test_all_paths.py](./src/test_all_paths.py)
3. verify path btw any two nodes: [test_verify_path.py](./src/test_verify_path.py)

```bash
python run test_*.py
```

## Data format

### *.map

it's used for building the game map, each line is a path with format: `srcNode --> direction --> dstNode`

For example: [zork1.map](./data/zork1.map)

```
West of House --> S --> South of House
South of House --> E --> Behind House
Behind House --> W --> Kitchen
Kitchen --> W --> Living Room
Living Room --> D --> Cellar
```

> note: another markdown syntax is in development: [map.md](./data/map.md)

### *.actions

The cache file for valid actions, with "Direction:" and "Non Direction:" sections. For example: [zork1.actions](./data/zork1.actions)

```
Direction:

N -- S
E -- W
SE -- NW
NE -- SW
U -- D


Non direction:

Get egg -- Drop egg
Open window
Open sack
Get garlic -- Drop garlic
Get lamp
Light lamp -- Douse lamp
```

~~for simplicity, each opposite direction is proposed by query gpt-3.5-turbo (by function [`get_opposite_direction`](https://github.com/Oaklight/gamegpt_utils/blob/f7a16d686a279bb3281dd5f412e0b96ade474d25/src/digraph.py#L65)
), and then manually checked and modified.~~

### *.verify

A list of paths to verify, with the following format:

```
srcNode, dstNode
action1
action2
...
actionN
```

For example:

```
kitchen, cellar
d
s
w
n
```

When verify path direction, program will first seek an **exact match**. ~~If not available, it will resort to query gpt for similar directional sentence check (by function [`same_direction_test`](https://github.com/Oaklight/gamegpt_utils/blob/8624faa807f1ee5438214f37a4adc36181072e42/src/digraph.py#L232) )~~

### *.map.reversed (generated)

it's used for path test, each line is a path with format: `dstNode --> direction --> srcNode`

For example: [zork1.map.reversed](./data/zork1.map.reversed)

```
south of house --> north --> west of house
behind house --> west --> south of house
kitchen --> east --> behind house
living room --> east --> kitchen
cellar --> up --> living room
```

### *.all2all_paths.md (generated)

it's used for path test

diff_shortest is the difference btw shortest path and current path, if diff_shortest == 0, it's the shortest path.

`diff_shortest = len(actions) - len(shortest_path)`

- markdown

  ```markdown
  # srcNode --> dstNode || diff_shortest: *
  action1
  action2
  ...
  ```

- json (not available yet)

  ```json
  {
    "srcNode": "srcNode",
    "dstNode": "dstNode",
    "diff_shortest": diff_shortest,
    "actions": [
      "action1",
      "action2",
      ...
    ]
  }
  ```

For example: [zork1.all2all_paths.md](./data/zork1.all2all_paths.md)

### *.all2all_shortest_paths.md (generated)

it's used for path test, similar format as *.all2all_paths.md, but only contains shortest paths. thus diff_shortest is not included

For example: [zork1.all2all_shortest_paths.md](./data/zork1.all2all_shortest_paths.md)
