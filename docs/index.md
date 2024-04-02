# Welcome to MANGO!

## What's MANGO?

**MANGO**: A Benchmark for Evaluating **Ma**pping and **N**avi**g**ati**o**n Abilities of Large Language Models

Large language models such as ChatGPT and GPT-4 have recently achieved astonishing performance on a variety of natural language processing tasks. 

In this paper, we propose MANGO, a benchmark to evaluate their capabilities to perform text-based mapping and navigation. Our benchmark includes 53 mazes taken from a suite of textgames: each maze is paired with a walkthrough that visits every location but does not cover all possible paths. The task is question-answering: for each maze, a large language model reads the walkthrough and answers hundreds of mapping and navigation questions such as "How should you go to Attic from West of House?" and "Where are we if we go north and east from Cellar?". 

Although these questions are easy to humans, it turns out that even GPT-4, the best-to-date language model, performs poorly at answering them. Further, our experiments suggest that a strong mapping and navigation ability would benefit large language models in performing relevant downstream tasks, such as playing textgames. 

Our MANGO benchmark will facilitate future research on methods that improve the mapping and navigation capabilities of language models. We host our leaderboard, data, code, and evaluation program here.

## Cite Us

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
