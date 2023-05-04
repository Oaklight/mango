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

## Run

```bash
python run_gen_move_human_to_all.sh -p <path> -g <game> -j <jericho_env>
```
，包括：
- path: data/maps，具体folder的名字取决于在哪里运行这个脚本
- game: 具体folder的名字
- jericho_env: jericho的环境变量，比如：z-machine-games-master/jericho-game-suite

生成的结果在data/maps/<game>下面