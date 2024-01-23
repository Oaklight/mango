请检查这张[表格](https://docs.google.com/spreadsheets/d/1NRHMsjMrTWFl8vc14YGEd2rQ6MiExCjYCwwRMeJGs14/edit?usp=sharing)，确保每个人标注的都是不同的游戏，不要重复标注。

为了保持数据一致性，不要改变之前的标注，直接从71步开始。过程中如发现之前的标注有问题，请备注到表格中，并及时在群里讨论。

有五个游戏被标为红色，这些游戏的jericho engine在特定步骤会出现问题，导致无法正常运行。所以请暂时不要标注这些游戏，等方案讨论确定之后再开始。

# ============== 2024.01.06 更新 ==============

分配重新调整过了，https://docs.google.com/spreadsheets/d/1NRHMsjMrTWFl8vc14YGEd2rQ6MiExCjYCwwRMeJGs14/edit#gid=0
每个人的总游戏量是差不多的

这次我们focus在标注今天讨论的几种遗留问题上：

### Chain of Actions

- 比如下面这个例子：
planetfall
```
    ===========
    ==>STEP NUM: 109
    ==>ACT: southwest
    ==>OBSERVATION: Tower Core

    ===========
    ==>STEP NUM: 110
    ==>ACT: north
    ==>OBSERVATION: Upper Elevator

    ===========
    ==>STEP NUM: 111
    ==>ACT: press down button
    ==>OBSERVATION: The elevator door slides shut. After a moment, you feel a sensation of vertical movement.

    ===========
    ==>STEP NUM: 112
    ==>ACT: wait
    ==>OBSERVATION: Time passes...

    ===========
    ==>STEP NUM: 113
    ==>ACT: wait
    ==>OBSERVATION: Time passes...
    The elevator door slides open.

    ===========
    ==>STEP NUM: 114
    ==>ACT: south
    ==>OBSERVATION: Elevator Lobby
```

标注为：

| step num | location before | location after |
| --- | --- | --- |
| 109 | Common Room | Tower Core |
| 110 | Tower Core | Upper Elevator |
| 111 | | |
| 112 | | |
| 113 | | |
| 114 | Upper Elevator | Elevator Lobby |

- 对于car, cab, boat, ship, handcar, etc. 一类交通工具，如有主动enter, exit这一类动作，也做上述类似处理

允许同一个地点，通过同一个动作到达不同位置，比如这里的Upper Elevator --> south --> Elevator Lobby/Tower Core。

通常是lift, elevator, 或者ship, car, boat这一类的vehicle。

如果已经发生添加，会在检查程序中体现为，conflict或human only。请revert back

### answerable step
- zork 1例子
```
===========
==>STEP NUM: 14
==>ACT: east
==>OBSERVATION: Kitchen
A bottle is sitting on the table.
The glass bottle contains:
  A quantity of water
There is a brown sack here.
The brown sack contains:
  A lunch

===========
==>STEP NUM: 15
==>ACT: up
==>OBSERVATION: You have moved into a dark place.
It is pitch black. You are likely to be eaten by a grue.

===========
==>STEP NUM: 16
==>ACT: light lamp
==>OBSERVATION: The brass lantern is now on.

Attic
This is the attic. The only exit is a stairway leading down.
A large coil of rope is lying in the corner.
On a table is a nasty-looking knife.
```

| step num | location before | location after | Answerable |
| --- | --- | --- | --- |
| 14 |  | Kitchen | |
| 15 | Kitchen | Attic | 16 |
| 16 | | | |

添加一栏“answerable”信息。在上述例子里，step 15填写实际地点，但是由于Attic的位置是step 16才知道，于是answerable填16。其他普通情况默认可以空着。

### 同地点多名称
- lostpig例子 
```
===========
==>STEP NUM: 51
==>ACT: east
==>OBSERVATION: Closet
It dark. Grunk see lots of shadow. Grunk see doorway to east and west, too. But mostly shadow.

Chhhkkkrrcht! What that strange noise?

===========
==>STEP NUM: 52
==>ACT: examine shadow
==>OBSERVATION: Shadow just dark, but in lots of different shape and size.

Shkkrnnnnk!

===========
...
===========
==>STEP NUM: 61
==>ACT: look
==>OBSERVATION: Gnome Room
This look like room for little person. It have bed that too little for Grunk. It have trunk that too little for Grunk. It have desk that too little for Grunk. Desk have stool that too little for Grunk. Room have doorway to east and west too, but them not so little. That good, because if doorway too little for Grunk, not know how Grunk get back out of room.

Gnome sitting on stool looking at Grunk.

On top of shelf there ball (that make light).

Gnome open up desk drawer and take out strange helmet. Him take out little box, too. Then him put them both on desk.

===========
```
按照出现最多的次数的内容标注，closet改为gnome room，answerable为61。

| step num | location before | location after | Answerable |
| --- | --- | --- | --- |
| 51 | Table Room | Gnome Room | 61 |
| 52 |  |  |  |
| ... |  |  |  |
| 61 |  |  |  |


# ============== old content below ==============

## 安装环境

```bash
# 进入data-intermediate所在的目录，比如：
# cd /home/xxx/xxx/gamegpt_utils (旧repo名)
# cd /home/xxx/xxx/mango (新repo名)

conda create -n mango python=3.11 #python=3.8 also works
conda activate mango
pip install -r requirements.txt
pip install https://github.com/MarcCote/jericho/archive/refs/heads/fix_obj_num.zip
python3 -m spacy download en_core_web_sm

# 下载游戏包
wget https://github.com/BYU-PCCL/z-machine-games/archive/master.zip
unzip master.zip

# # 参考文件夹结构
# - z-machine-games
#     - ...
#     - jericho-game-suite # 后面需要定位到这个jericho game packages
#     - ... 
# - mango
#     - ...
#     - data-intermediate # 在这里面找要标注的文件
#     - ...
```
## key program to use

```bash
# 生成machine code
(gamegpt) cd/to/your/mango/root$ ./scripts/gen_moves/run_gen_move_machine_all.sh -j ../z-machine-games-master/jericho-game-suite/ -o ./data-intermediate/ -g night -s 90 -a

# 转换并校验human label
(gamegpt) cd/to/your/mango/root$ ./scripts/gen_moves/run_gen_move_human_to_final.sh -p ./data-intermediate/ -j ../z-machine-games-master/jericho-game-suite/ -g night -s 90 -a
```

请注意，新加入的“-a”参数，会强制使用仓库里缓存的walkthrough actions，以保证不同jericho版本变化时，action sequence不会改变。请默认使用这个参数。


## 以night为例

### 生成machine map

通过检查[night.walkthrough](./night/night.walkthrough)的内容，可以发现最多有90步，所以我们可以这样生成machine map：

```bash
(gamegpt) pding@pding-X1:~/projects/mango/mango$ ./scripts/gen_moves/run_gen_move_machine_all.sh -j ../z-machine-games-master/jericho-game-suite/ -o ./data-intermediate/ -g night -s 90
```

注意：有的游戏非常冗长，建议不要一次性生成所有的machine steps（比如spirit，有1000多步），而是**分批生成标注，比如每次处理100步**，这样**可以避免检查脚本丢给你太多的machine only steps导致没法阅读**。


### 标注valid moves

打开[night.walkthrough](./night/night.walkthrough)和[night.valid_moves.csv](./night/night.valid_moves.csv)，按照下面的格式标注：

| Step Num | Location Before                                | Location After                                 |
|----------|------------------------------------------------|------------------------------------------------|
| 1        | Computer Site                                  | Hall Outside Computer Site                     |
| 2        | Hall Outside Computer Site                     | Hall (3rd floor, middle of north/south hall) |
| 3        | Hall (3rd floor, middle of north/south hall) | Hall Outside Elevator (3rd floor)              |
| 4        |                                                |                                                |
| 5        |                                                |                                                |

原则是“从哪里到哪里”，当且仅当“位置”发生变化时才标注，比如上面的第4、5行，没有发生位置变化，所以不需要标注。

### 同名地点的标注

有一些位置名称可以直接从description找到，但是有的时候需要你手动补上特征信息，比如上面的Hall，否则无法体现出不同楼层之间的区别。**这些信息可能一开始不易察觉，但往后看到的内容越多你就会发现一些同名地点之间的区别，请即刻补上这些特征信息**

### 标注工具推荐

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

