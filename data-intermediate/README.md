请检查这张[表格](https://docs.google.com/spreadsheets/d/1NRHMsjMrTWFl8vc14YGEd2rQ6MiExCjYCwwRMeJGs14/edit?usp=sharing)，确保每个人标注的都是不同的游戏，不要重复标注。


## 安装环境

```bash
# 进入data-intermediate所在的目录，比如：
# cd /home/xxx/xxx/gamegpt_utils (旧repo名)
# cd /home/xxx/xxx/mango (新repo名)

conda create -n mango python=3.11
conda activate mango
pip install -r requirements.txt
```


## 以night为例

有的游戏非常冗长，建议不要一次性生成所有的machine steps（比如spirit，有1000多步），而是**分批生成标注，比如每次处理100步**，这样**可以避免检查脚本丢给你太多的machine only steps导致没法阅读**。

```bash

### 标注valid moves

打开[night.walkthrough](./night/night.walkthrough)和[night.valid_moves.csv](./night/night.valid_moves.csv)，按照下面的格式标注：

| Step Num | Location Before                                | Location After                                 |
|----------|------------------------------------------------|------------------------------------------------|
| 1        | Computer Site                                  | Hall Outside Computer Site                     |
| 2        | Hall Outside Computer Site                     | "Hall (3rd floor, middle of north/south hall)" |
| 3        | "Hall (3rd floor, middle of north/south hall)" | Hall Outside Elevator (3rd floor)              |
| 4        |                                                |                                                |
| 5        |                                                |                                                |

原则是“从哪里到哪里”，当且仅当“位置”发生变化时才标注，比如上面的第4、5行，没有发生位置变化，所以不需要标注。

推荐使用visual studio code的“edit csv”[插件](https://marketplace.visualstudio.com/items?itemName=janisdd.vscode-edit-csv)，或使用excel打开csv文件。但请注意excel的保存格式，确保写回csv文件时不会改变原有的格式或引入乱码。

### 用脚本检查并生成初步文件

```bash
# 进入data-intermediate所在的目录，比如：
# cd /home/xxx/xxx/gamegpt_utils (旧repo名)
# cd /home/xxx/xxx/mango (新repo名)
conda activate mango # conda activate gamegpt (旧)
./scripts/gen_moves/run_gen_move_human_to_final.sh  -p data-intermediate -j ../z-machine-games-master/jericho-game-suite/ -g night
```

如果标注一切顺利，应该看到如下输出：

```bash
(gamegpt) pding@pding-X1:~/projects/mango/mango$ ./scripts/gen_moves/run_gen_move_human_to_final.sh -p ./data-intermediate/ -j ../z-machine-games-master/jericho-game-suite/ -g night -s 90
Generating for night...
Generating for night...
Reading file ./data-intermediate//night/night.valid_moves.csv ing ...
Done.
Game: night, Max steps: 90
90
Saved to ./data-intermediate//night/night.map.human
Good Job!
game data dir: ./data-intermediate//night
Processing night...
General Stats:
- [num: 62] common steps
- [num: 0] machine only steps: []
- [num: 0] human only steps: []
- [num: 0] conflict annotations on common steps: {}
No difference found, exiting...
Reload both maps after resolution
Done processing!

56
============= extracting node-step map ===============
processing night
Done for night!
```

### 一些错误处理样例

1.如果有重名位置（但实际不同）的标注，你可能会看到类似如下的输出：

```bash
(gamegpt) pding@pding-X1:~/projects/mango/mango$ ./scripts/gen_moves/run_gen_move_human_to_final.sh -p ./data-intermediate/ -j ../z-machine-games-master/jericho-game-suite/ -g night -s 90
Generating for night...
Generating for night...
Reading file ./data-intermediate//night/night.valid_moves.csv ing ...
Done.
Game: night, Max steps: 90
90
Saved to ./data-intermediate//night/night.map.human
Good Job!
game data dir: ./data-intermediate//night
Processing night...
General Stats:
- [num: 62] common steps
- [num: 0] machine only steps: []
- [num: 0] human only steps: []
- [num: 5] conflict annotations on common steps: {'hall (obj53)': [('Hall', [(84, 'dst'), (85, 'src')]), ('Hall (2nd floor, middle of north/south hall)', [(24, 'dst'), (29, 'src'), (48, 'dst'), (49, 'src'), (63, 'dst'), (64, 'src')])], 'maze of twisty passages (obj94)': [('Maze of Twisty Passages (stop 3)', [(33, 'dst'), (34, 'src'), (45, 'dst'), (46, 'src'), (81, 'dst'), (82, 'src')]), ('Mase of Twisty Passages (stop 3)', [(71, 'dst'), (72, 'src')])], 'maze of twisty passages (obj95)': [('Maze of Twisty Passages (stop 4)', [(34, 'dst'), (35, 'src'), (44, 'dst'), (45, 'src'), (80, 'dst'), (81, 'src')]), ('Mase of Twisty Passages (stop 4)', [(72, 'dst'), (73, 'src')])], 'maze of twisty passages (obj96)': [('Mase of Twisty Passages (stop 5)', [(73, 'dst'), (74, 'src')]), ('Maze of Twisty Passages (stop 5)', [(35, 'dst'), (36, 'src'), (43, 'dst'), (44, 'src'), (79, 'dst'), (80, 'src')])], 'maze of twisty passages (obj98)': [('Mase of Twisty Passages (stop 6)', [(74, 'dst'), (75, 'src')]), ('Maze of Twisty Passages (stop 6)', [(36, 'dst'), (37, 'src'), (42, 'dst'), (43, 'src'), (78, 'dst'), (79, 'src')])]}
Continue? [y/n]
```

此时建议选择`n`，然后手动解决冲突。

2.对于出现machine only和human only的情况，推荐的处理方式是：

- 选择`n`，先检查本地标注是否存在typo或者遗漏;
- 如果仍然存在，请在最近的一次讨论会上和大家一起讨论，如果大家都认为是正确的标注，可以选择`y`继续。

比如下面这个例子：

```bash
(gamegpt) pding@pding-X1:~/projects/mango/mango$ ./scripts/gen_moves/run_gen_move_human_to_final.sh -p ./data-intermediate/ -j ../z-machine-games-master/jericho-game-suite/ -g night -s 90
Generating for night...
Generating for night...
Reading file ./data-intermediate//night/night.valid_moves.csv ing ...
Done.
Game: night, Max steps: 90
90
Saved to ./data-intermediate//night/night.map.human
Good Job!
game data dir: ./data-intermediate//night
Processing night...
General Stats:
- [num: 45] common steps
- [num: 0] machine only steps: []
- [num: 17] human only steps: [71, 72, 73, 74, 75, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89]
- [num: 0] conflict annotations on common steps: {}
Continue? [y/n]
```

可以看到从71到89都是human only steps，这种情况下，很有可能是machine map没有被更新到最完整的版本，检查后发现确实如此，所以重新生成night.map.machine

```bash
(gamegpt) pding@pding-X1:~/projects/mango/mango$ ./scripts/gen_moves/run_gen_move_machine_all.sh -j ../z-machine-games-master/jericho-game-suite/ -o ./data-intermediate/ -g night -s 90
Generating for night...
Args: Namespace(game_name='night', jericho_path='../z-machine-games-master/jericho-game-suite/', max_steps=90, output_dir='./data-intermediate/', walk_md=False)
Game: night, Max steps: 90
Saved to ./data-intermediate//night/night.map.machine
```

