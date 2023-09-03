# play games


## results
- 2023/09/03
- max steps: 120
|          | gpt3.5 scores (ctx: 4k) | gpt4 scores (ctx: 8k)|
|----------|-------------------------|----------------------|
| zork1.z5 |   -5 (die, max: 5)      | 30 (die, max: 40)        |
| balances.z5 |   10 (out-of-ctx, max: 10)  |  10 (exceed max steps, max:10)            |
| ludicorp.z5 |   10 (out-of-ctx, max: 10)  |   10 (exceed max steps, max:10)                 |
| pentari.z5  |  try1: 30 (die, max: 30) / try2: 5 (RetryError, max:5)   |  try1: 5 (die, max: 5) / try2: 5 (exceed max steps, max:5)    |