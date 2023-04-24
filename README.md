# gamegpt_utils

gamegpt graph utils

## depandency
- networkx: `pip install networkx`
- openai: `pip install openai`
- matplotlib: `pip install matplotlib`

## major functions

[digraph.py](./src/digraph.py)

- common utils: 
  - `build_graph_from_file(pathFile: str = "data/paths.txt", oppositeFile: str = "data/opposite.txt")`
  - `get_opposite_direction(direction: str)`
  - `plot_graph(g: object)`
  - `get_edge_direction(G, n1, n2)`
  - `query_chatgpt(prompt, message)`
  - `load_opposite_direcions(directionFile)`
- shortest path related
  - `get_shortest_path(g: object, src: str, dst: str)`
  - `print_path(g: object, path: list)`
- all paths related
  - `get_all_paths(g: object, src: str, dst: str)`
  - `print_all_paths(g: object, all_paths: list)`
- verify path related
  - `verify_path(g: object, srcNode, dstNode, paths2verify: list)`
  - `parse_path(pathFile: str = "data/paths2verify.txt")`
  - `same_direction_test(given_direction: str, proposed_direction: str)`

## examples
1. shortest path btw any two nodes: [test_shortest_path.py](./src/test_shortest_path.py)


2. all paths btw any two nodes, sorted by path length: [test_all_paths.py](./src/test_all_paths.py)


3. verify path btw any two nodes: [test_verify_path.py](./src/test_verify_path.py)


## data format

### *_locations.txt
it's used for building the game map, each line is a path with format:
```
srcNode --> direction --> dstNode
```
For example:
```
Living Room --> go down --> Cellar
Cellar --> go south --> East of Chasm
East of Chasm --> go east --> Gallery
Gallery --> go north --> Studio
Studio --> go up chimney --> Kitchen
Kitchen --> go up --> Attic
Attic --> go down --> Kitchen
Kitchen --> go west --> Living Room
```

### *_opposite_directions.txt
The cache file for opposite directions, each line is a pair of opposite directions, for example:
```
go east --> go west
go west --> go east
enter house --> exit house
exit house --> enter house
go down --> go up
go up --> go down
go up chimney --> climb down chimney
climb down chimney --> go up chimney
go southeast --> northwest
```

for simplicity, each opposite direction is proposed by query gpt-3.5-turbo (by function [`get_opposite_direction`](https://github.com/Oaklight/gamegpt_utils/blob/f7a16d686a279bb3281dd5f412e0b96ade474d25/src/digraph.py#L65)
), and then manually checked and modified.


### *_paths2verify.txt
A list of paths to verify, with the following format:
```
srcNode, dstNode
srcNode --> direction --> midNode1
midNode1 --> direction --> midNode2
...
midNodeN --> direction --> dstNode
```
For example:
```
kitchen, cellar
kitchen --> go down the floor --> studio
studio --> go south --> gallery
gallery --> go west --> east of chasm
east of chasm --> go north --> cellar
```
When verify path direction, program will first seek an exact match. If not available, it will resort to query gpt for similar directional sentence check (by function [`same_direction_test`](https://github.com/Oaklight/gamegpt_utils/blob/8624faa807f1ee5438214f37a4adc36181072e42/src/digraph.py#L232) )
