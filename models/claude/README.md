# gpt-zork
Play and eval GPT in the text games

# Install
Install `openai` and `tiktoken`
```
pip install openai tiktoken
```
and setup environment variable `OPENAI_API_KEY`.

# Usage
set `GAME` to be the game you would like to evaluate and select GPT version. (check out available games in `maps` folder)
## Evaluation locally
1. Path Generation Task
```
python scripts/pathgen_gpt.py --game GAME --gpt-version 3
python scripts/pathgen_gpt.py --game GAME --gpt-version 4
```
2. Step Navigation Task
```
python scripts/stepnav_gpt.py --game GAME --gpt-version 3
python scripts/stepnav_gpt.py --game GAME --gpt-version 4
```
## Evaluation on Slurm
1. Path Generation Task
```
python scripts/slurm_pathgen_gpt.py --game GAME --gpt-version 3
python scripts/slurm_pathgen_gpt.py --game GAME --gpt-version 4
```
2. Step Navigation Task
```
python scripts/slurm_stepnav_zork_gpt.py --game GAME --gpt-version 3
python scripts/slurm_stepnav_zork_gpt.py --game GAME --gpt-version 4
```

