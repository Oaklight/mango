# Mango

repo for paper: *MANGO: A Benchmark for Evaluating <u>Ma</u>pping and <u>N</u>avi<u>g</u>ati<u>o</u>n Abilities of Large Language Models*

<!-- TOC -->

- [Mango](#mango)
    - [1. Data: game maps](#1-data-game-maps)
        - [1.1. game folder structure](#11-game-folder-structure)
    - [2. Code specs](#2-code-specs)
        - [2.1. Depandencies](#21-depandencies)
        - [2.2. src & scripts](#22-src--scripts)
    - [3. How to run?](#3-how-to-run)
    - [4. Data format](#4-data-format)
        - [4.1. *.map.machine and *.map.human](#41-mapmachine-and-maphuman)
        - [4.2. *.map.reversed generated](#42-mapreversed-generated)
        - [4.3. *.all2all.json generated](#43-all2alljson-generated)

<!-- /TOC -->

## data-intermediate

Because some json files are huge, we use tar.zst to package the data.

1. to compress the data

```bash
tar -I 'zstd' -cvf data-intermediate.tar.zst --exclude='*.md' data-intermediate/ # exclude README.md and challenging_parsing.md
```

2. to decompress the data to `your_folder/`

first you should make sure `your_folder/` exist. If not, create it.

silently
```bash
tar -I 'zstd -d' -xf data-intermediate.tar.zst -C your_folder/
```
or, with progress verbose
```bash
zstd -d -c data-intermediate.tar.zst | tar -xvf - -C your_folder/
```

## ===================== OLD CONTENT =====================

## Data: game maps

There are 3 major subfolders under "data" directory:

- [maps](./data/maps): all files generated during entire development process of this project.
- [maps-diff-fjd](./data/maps-diff-fjd): there were some paths introduced in release before a bug fix, and they were used in GPT family inference. We fixed the bug and identified those paths that should be dropped, and new paths should be included. Only games appeared in this folder had this issue.
- [maps-release](./data/maps-release): all files necessary for inference. Files included may be revised for change.

### game folder structure

Each game should have these files during the lifetime of this project:

1. `<game>.walkthrough:` the game walkthrough file, read by human and LLM.
2. `<game>.map.machine`: machine generated forward map, used for path verification during human annotation. Actions resulted in location_id change in jericho are included. This was from the same walkthrough steps in generating 1.
3. `<game>.moves`: all actions appeared in the first 70 steps, accompanied with commonly used directional actions.
4. `<game>.valid_moves.csv`: human annotation files, after reading the walkthrough.
5. `<game>.map.human`: human annotated forward map. Reformatted from 4. Same format.
6. `<game>.code2anno.json`: machine code to human annotation mapping. By cross comparing 2 and 5.
7. `<game>.anno2code.json`: human annotation to machine code mapping. By cross comparing 2 and 5.
8. `<game>.node_step.json`: human annotation and its first appearance step mapping. Extracted from 4.
9. `<game>.map.reversed`: machine generated backward map. Attemption to naively reverse walk each forward step.
10. `<game>.all_pairs.json`: all possible pairs of two nodes in graph built by 5 and 9. Including the possible path number between them.
11. `<game>.all2all.json`: all simple paths between any pair of two nodes (documented in 10) in graph built by 5 and 9.

## Code specs

### Depandencies

see details in [requirement.txt](./requirements.txt)

`pip install -r requirements.txt`

**`python 3.6` and above is required.** Tested stable with `python 3.8` and `python 3.11`.

Recommend to use conda environment or pip virtual env.

### src & scripts

- [src](./src/): source codes for different utils, generally categorized in folders by purpose.
- [scripts](./scripts/): scripts for running different tasks, generally categorized in folders by purpose.

## How to run?

1. generate all2all & all_pairs:
```bash
# activate your virtual env or conda env
# cd to project root dir

./scripts/gen_paths/run_gen_all2all.sh # read the help message prompted

./scripts/gen_paths/run_gen_all2all.sh -p ./data/maps # generate for all games

./scripts/gen_paths/run_gen_all2all.sh -p ./data/maps -g zork1 # generate for zork1 only

# go to ./data/maps/zork1 and ./data/maps-release/zork1 to check the generated files
```

## Data format

### `*.map.machine` and `*.map.human`

it's used for building the game map, each line is a path with format: `src_node --> direction --> dst_node`. Same format for both `*.map.machine` and `*.map.human`.

For example: [zork1.map.human](./data/maps/zork1/zork1.map.human)

```txt
west house (obj180) --> north --> north house (obj81), step 1
north house (obj81) --> north --> forest path (obj75), step 2
forest path (obj75) --> up --> up a tree (obj88), step 3
up a tree (obj88) --> down --> forest path (obj75), step 5
forest path (obj75) --> south --> north house (obj81), step 6
```

### *.map.reversed (generated)

it's used for path test, each line is a path with format: `dst_node --> direction --> src_node, step #, desc: ...`

For example: [zork1.map.reversed](./data/maps/zork1/zork1.map.reversed)

```txt
north house (obj81) --> south --> west house (obj180), step 1, desc: North of House || You are facing the north side of a white house. There is no door here, and all the windows are boarded up. To the north a narrow path winds through the trees.
forest path (obj75) --> south --> north house (obj81), step 2, desc: None
up a tree (obj88) --> down --> forest path (obj75), step 3, desc: None
forest path (obj75) --> up --> up a tree (obj88), step 5, desc: None
north house (obj81) --> north --> forest path (obj75), step 6, desc: None
```

when `desc: None`, it means the path is good to go. Examples see above steps 2-6.
when `desc: ...`, it means the path is not good to go, and the observation after taking the "direction" is appended in `desc`. Example see above step 1.

### *.all2all.json (generated)

it's used for path test

diff_shortest is the difference btw shortest path and current path, if diff_shortest == 0, it's the shortest path.

`diff_shortest = len(actions) - len(shortest_path)`

  ```json
  [
    {
        "src_node": "altar (obj212)",
        "dst_node": "egypti (obj175)",
        "diff_shortest": 0,
        "path_details": [
            {
                "prev_node": "altar (obj212)",
                "node": "temple (obj220)",
                "action": "north",
                "seen_in_forward": true,
                "step_min_cutoff": 39
            },
            {
                "prev_node": "temple (obj220)",
                "node": "egypti (obj175)",
                "action": "east",
                "seen_in_forward": true,
                "step_min_cutoff": 46
            }
        ],
        "step_count": 2,
        "path_min_cutoff": 46,
        "all_steps_seen_in_forward": true
    },
    ...
  ]
  ```

  For example: [zork1.all2all.json](./data/maps/zork1/zork1.all2all.json)
