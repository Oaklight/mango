# Leaderboard

We hold a leaderboard for evaluating model performance on our MANGO benchmark. We measure the success rate on Destination Finding (DF) questions and Route Finding (RF) problems, both with easy and hard settings. The evaluation is performed on all 53 mazes with average accuracy reported.

## Submission

We welcome new submissions to our MANGO benchmark. To submit a new result, please email `[dingpeng]@@uchicago.edu` with the paper of your method. We will then update the leaderboard and link your paper accordingly.

## 🏆 Benchmark 🏆

| Rank | Model                                                                       | DF (easy) | DF (hard) | RF (easy) | RF (hard) |
|------|-----------------------------------------------------------------------------|-------|-------|-------|-------|
| 1 🥇 | [o1-preview*](https://openai.com/index/introducing-openai-o1-preview/)       | 1.0   | 1.0   | 0.97 | 0.97   |
| 2 🥈 | [o1-mini*](https://openai.com/index/introducing-openai-o1-preview/)          | 1.0   | 1.0   | 0.44  | 0.80  |
| 3 🥉 | [GPT-4-0613](https://platform.openai.com/docs/models/gpt-4-and-gpt-4-turbo) | 0.83  | 0.58  | 0.55  | 0.45  |
| 4    | [Claude-2](https://www.anthropic.com/news/claude-2)                         | 0.81  | 0.45  | 0.47  | 0.19  |
| 5    | [Clause-1](https://www.anthropic.com/news/100k-context-windows)             | 0.72  | 0.36  | 0.33  | 0.11  |
| 6    | [GPT-3.5-turbo-0613](https://platform.openai.com/docs/models/gpt-3-5-turbo) | 0.57  | 0.32  | 0.15  | 0.03  |
| 7    | [Llama-2](https://arxiv.org/abs/2307.09288)                                 | 0.41  | 0.24  | 0.03  | 0.00  |
| 8    | [RWKV](https://arxiv.org/abs/2305.13048)                                    | 0.19  | 0.20  | 0.01  | 0.00  |

*Updated on: 2024-09-24*

*: o1-preview and o1-mini models are tested on a randomly sampled 3-game subset. Note that o1 models do not allow structured outputs and forbid strong formatting prompt, so we have to remove "start your answer with '['" in the original prompt, which makes the ratio of format-valid outputs relatively low, roughly 0.16 for DF questions and 0.47 for RF questions. The reported results are only from format-valid outputs.


