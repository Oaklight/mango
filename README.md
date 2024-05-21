# MANGO

Repo for paper: *[MANGO: A Benchmark for Evaluating <u>Ma</u>pping and <u>N</u>avi<u>g</u>ati<u>o</u>n Abilities of Large Language Models](https://arxiv.org/abs/2403.19913)*

You can find more information at [mango.ttic.edu](https://mango.ttic.edu).

If you have any questions, please feel free to open an [issue](https://github.com/Oaklight/mango/issues).


## Abstract

Large language models such as ChatGPT and GPT-4 have recently achieved astonishing performance on a variety of natural language processing tasks.

In this paper, we propose MANGO, a benchmark to evaluate their capabilities to perform text-based mapping and navigation. Our benchmark includes 53 mazes taken from a suite of textgames: each maze is paired with a walkthrough that visits every location but does not cover all possible paths. The task is question-answering: for each maze, a large language model reads the walkthrough and answers hundreds of mapping and navigation questions such as "How should you go to Attic from West of House?" and "Where are we if we go north and east from Cellar?".

Although these questions are easy to humans, it turns out that even GPT-4, the best-to-date language model, performs poorly at answering them. Further, our experiments suggest that a strong mapping and navigation ability would benefit large language models in performing relevant downstream tasks, such as playing textgames.

Our MANGO benchmark will facilitate future research on methods that improve the mapping and navigation capabilities of language models. We host our leaderboard, data, code, and evaluation program here.

## Setup

```
git clone --depth 1 git@github.com:Oaklight/mango.git
cd mango
conda create -f environment.yml --name mango
conda activate mango
pip install -r requirements.txt
```
Please remember to add `--depth 1` when cloning the code.

## Dataset
Our data are hosted on [Huggingface](https://huggingface.co/mango-ttic). You can get more information from [this link](https://oaklight.github.io/mgwb/data/).

Here we demonstrate how to download the data of the first 70 moves for each game:
```
cd mango
wget https://huggingface.co/datasets/mango-ttic/data/resolve/main/data-70steps.tar.zst
zstd -d -c data-70steps.tar.zst | tar -xvf -
rm data-70steps.tar.zst
mv data-70steps data
```

## Inference
We put the inference codebase in the folder `mango/inference/`.
You can refer to the README file under this folder for more information of the codebase.


Here we show how to query the `gpt-3.5` model to perform inference:

```
export OPENAI_API_KEY=<YOUR KEY>

python mango/inference/main.py --exp_tag debug --data_folder ./data --save_folder ./results --game_name '905' --task_type 'route_finding' --model_name 'gpt-3.5' 
```

## Evaluation

Please refer to `mango/evaluation/eval_batch.py`.

## Citation
```bibtex
@misc{ding2024mango,
      title={MANGO: A Benchmark for Evaluating Mapping and Navigation Abilities of Large Language Models}, 
      author={Peng Ding and Jiading Fang and Peng Li and Kangrui Wang and Xiaochen Zhou and Mo Yu and Jing Li and Matthew R. Walter and Hongyuan Mei},
      year={2024},
      eprint={2403.19913},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
```