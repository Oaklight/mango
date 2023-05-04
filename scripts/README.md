# How to use

## Install

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## Download Game Environment

```bash
wget https://github.com/BYU-PCCL/z-machine-games/archive/master.zip
unzip master.zip
```

记住这个z-machine-games-master的路径，后面会用到。

我的文件夹结构是这样的， 供你参考

```bash
- gamegpt_utils
    - data/maps
        - game1
        - game2
        - ...
    - data_old
    - scripts
        - gen_moves
    - src
        - gen_moves
        - gen_paths
- z-machine-games-master
```

## Run

### 生成一个游戏的 game.map.human, game.anno2code.json, game.anno2code.json

```bash
cd gamegpt_utils
./scripts/gen_moves/run_gen_move_human_to_all.sh -p <path> -g <game> -j <jericho_path>
```

，包括：

- path: 一般情况是指`data/maps`，具体folder取决于在哪里运行这个脚本
- game: 具体folder的名字
- jericho_path: jericho游戏的位置，比如：`z-machine-games-master/jericho-game-suite`

生成的结果在`data/maps/<game>`下面

### 生成所有游戏的 game.map.human, game.anno2code.json, game.anno2code.json

如果想要生成所有的游戏，可以运行：

```bash
cd gamegpt_utils

# 先生成 game.map.human，仅对存在 game.valid_moves.csv 的文件夹操作
./scripts/gen_moves/run_gen_move_human_all.sh -p <path> -j <jericho_path>

# 再此基础上生成 game.anno2code.json, game.anno2code.json， 仅对 game.map.human 存在的文件夹操作
./scripts/gen_moves/run_gen_move_final_all.sh -p <path> -j <jericho_path>
```
