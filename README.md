# gamegpt_utils

gamegpt graph utils

## depandency
- networkx: `pip install networkx`
- openai: `pip install openai`
- matplotlib: `pip install matplotlib`

## major functions

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
## examples
1. shortest path btw any two nodes: [test_shortest_path.py](./src/test_shortest_path.py)
2. all paths btw any two nodes, sorted by path length: [test_all_paths.py](./src/test_all_paths.py)
3. verify path btw any two nodes: [test_verify_path.py](./src/test_verify_path.py)
```bash
python run test_*.py
```


## data format

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
