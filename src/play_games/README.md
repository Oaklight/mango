# play games


## results
### 2023/09/03 (max steps: 120)
|          | gpt3.5 scores (ctx: 4k) | gpt4 scores (ctx: 8k)|
|----------|-------------------------|----------------------|
| zork1.z5 |   -5 (die, max: 5)      | 30 (die, max: 40)        |
| balances.z5 |   10 (out-of-ctx, max: 10)  |  10 (exceed max steps, max:10)            |
| ludicorp.z5 |   10 (out-of-ctx, max: 10)  |   10 (exceed max steps, max:10)                 |
| pentari.z5  |  try1: 30 (die, max: 30) / try2: 5 (RetryError, max:5)   |  try1: 5 (die, max: 5) / try2: 5 (exceed max steps, max:5)    |


### 2023/09/04 (max steps: 120)
added 1-step map: 
prompt: "-hints: if you go **, you will get to **; if you go **, you will get to ** ..."
|          | gpt3.5 scores (ctx: 4k) | gpt4 scores (ctx: 8k)|
|----------|-------------------------|----------------------|
| zork1.z5 |   35 (exceed max steps, max:35)      |   0 (exceed max steps, max:0)    |
| balances.z5 |  5 (RetryError, max: 5)           |    10 (exceed max steps, max:10)    |
| ludicorp.z5 |  2 (exceed max steps, max:2)      |   10 (exceed max steps, max:10)                      |
| pentari.z5  |   5 (exceed max steps, max:5)     |   5 (exceed max steps, max:5)                       |

ps: "extra info: ", gpt3.5 scores, pentari.z5: 5 (RetryError, max:5)

### 09-06 meeting
- [ ] walkthrough --> #revisited steps/#all steps --> rank all the games 
- [ ] baseline CoT
- [ ] goal-based CoT? How to design

Research Topics: 
- Goal Alignment
- Game Goal Alignment
- Graph into Prompt

- rank all steps:
[game name, # revisited steps, # all steps, # full walkthrough actions, revisited steps ratio]
['gold', 94, 115, 346, 0.8173913043478261]
['adventureland', 71, 89, 171, 0.797752808988764]
['cutthroat', 141, 177, 337, 0.7966101694915254]
['night', 39, 49, 91, 0.7959183673469388]
['karn', 97, 125, 363, 0.776]
['ballyhoo', 161, 220, 417, 0.7318181818181818]
['deephome', 122, 173, 328, 0.7052023121387283]
['zork1', 158, 228, 397, 0.6929824561403509]
['tryst205', 128, 190, 519, 0.6736842105263158]
['zork3', 87, 132, 274, 0.6590909090909091]
['afflicted', 32, 49, 99, 0.6530612244897959]
['ludicorp', 144, 222, 365, 0.6486486486486487]
['hollywood', 141, 219, 398, 0.6438356164383562]
['enchanter', 80, 127, 266, 0.6299212598425197]
['yomomma', 17, 27, 99, 0.6296296296296297]
['planetfall', 111, 179, 400, 0.6201117318435754]
['spirit', 341, 550, 1265, 0.62]
['temple', 42, 68, 182, 0.6176470588235294]
['lurking', 81, 134, 295, 0.6044776119402985]
['zork2', 88, 146, 297, 0.6027397260273972]
['trinity', 137, 229, 611, 0.5982532751091703]
['curses', 206, 345, 817, 0.5971014492753624]
['advent', 89, 158, 278, 0.5632911392405063]
['ztuu', 17, 31, 85, 0.5483870967741935]
['pentari', 14, 26, 50, 0.5384615384615384]
['hhgg', 22, 41, 362, 0.5365853658536586]
['seastalker', 47, 88, 205, 0.5340909090909091]
['enter', 22, 42, 103, 0.5238095238095238]
['dragon', 27, 52, 102, 0.5192307692307693]
['murdac', 103, 203, 305, 0.5073891625615764]
['jewel', 33, 66, 224, 0.5]
['snacktime', 4, 8, 35, 0.5]
['balances', 8, 16, 123, 0.5]
['infidel', 48, 98, 251, 0.4897959183673469]
['anchor', 114, 241, 532, 0.4730290456431535]
['partyfoul', 7, 15, 57, 0.4666666666666667]
['sorcerer', 59, 128, 255, 0.4609375]
['detective', 19, 42, 52, 0.4523809523809524]
['reverb', 14, 33, 75, 0.42424242424242425]
['awaken', 11, 27, 58, 0.4074074074074074]
['library', 6, 15, 53, 0.4]
['zenon', 10, 26, 84, 0.38461538461538464]
['spellbrkr', 30, 78, 413, 0.38461538461538464]
['inhumane', 27, 71, 123, 0.38028169014084506]
['wishbringer', 28, 75, 185, 0.37333333333333335]
['plundered', 30, 82, 190, 0.36585365853658536]
['sherlock', 39, 109, 340, 0.3577981651376147]
['omniquest', 15, 43, 79, 0.3488372093023256]
['lostpig', 8, 24, 147, 0.3333333333333333]
['loose', 5, 20, 51, 0.25]
['moonlit', 2, 12, 60, 0.16666666666666666]
['huntdark', 0, 5, 68, 0.0]
['905', 0, 4, 23, 0.0]


### 09-08 experiments
- max steps: 120
- add CoT
|          | gpt3.5 scores (ctx: 4k) | gpt4 scores (ctx: 8k)|
|----------|-------------------------|----------------------|
| zork1.z5 |      0 (exceed max steps, max:0)                    |                          |
| afflicted.z8 |      "examine the door"               |                         |
| ludicorp.z5 |                      |                         |
| karn.z5  |                         |                         |
| detective.z5  |     30 (die, max:30)                      |                         |

- added 1-step map:
prompt: "-extra info: if you go **, you will get to **; if you go **, you will get to ** ..."

|          | gpt3.5 scores (ctx: 4k) | gpt4 scores (ctx: 8k)|
|----------|-------------------------|----------------------|
| zork1.z5 |     0 (exceed max steps, max:0)                     |                      |
| afflicted.z8 |                     |                      |
| ludicorp.z5 |                      |                      |
| karn.z5  |                         |                         |
| detective.z5  |   30 (die, max:30)                 |                         |


notes: 
- Add CoT baseline: 
    - self-reinforcement question. --> error --> get stuck
    - You need to continuously explore the environment, overcome hardships encountered along the way, in order to find an exit.  --> south, north
- rank first 30 steps:
['night', 11, 19, 29, 0.5789473684210527]  √ --> Maze, Hall
['cutthroat', 5, 9, 29, 0.5555555555555556]
['zenon', 4, 8, 29, 0.5]
['gold', 8, 16, 29, 0.5]
['detective', 10, 20, 29, 0.5]  √ --> easy to die
['inhumane', 8, 18, 29, 0.4444444444444444] √ --> In the Desert
['sorcerer', 4, 9, 29, 0.4444444444444444]
['zork1', 6, 14, 29, 0.42857142857142855] √ --> hard, sparse map
['omniquest', 6, 16, 29, 0.375] √ --> get stuck, "west", "east"
['pentari', 7, 19, 29, 0.3684210526315789] √
['ztuu', 4, 11, 29, 0.36363636363636365] √
['spirit', 5, 14, 29, 0.35714285714285715]
['ballyhoo', 7, 20, 29, 0.35] √
['jewel', 4, 12, 29, 0.3333333333333333]
['karn', 3, 9, 29, 0.3333333333333333]
['partyfoul', 3, 9, 29, 0.3333333333333333]
['snacktime', 2, 6, 29, 0.3333333333333333]
['dragon', 6, 18, 29, 0.3333333333333333] √
['curses', 3, 10, 29, 0.3]
['deephome', 3, 10, 29, 0.3]
['adventureland', 3, 10, 29, 0.3]
['zork2', 5, 17, 29, 0.29411764705882354]
['seastalker', 3, 11, 29, 0.2727272727272727]
['sherlock', 3, 11, 29, 0.2727272727272727]
['yomomma', 2, 8, 29, 0.25]
['infidel', 3, 12, 29, 0.25]
['lurking', 1, 4, 29, 0.25]
['zork3', 4, 17, 29, 0.23529411764705882]
['spellbrkr', 1, 5, 29, 0.2]
['tryst205', 1, 5, 29, 0.2]
['balances', 1, 5, 29, 0.2]
['ludicorp', 2, 11, 29, 0.18181818181818182]
['afflicted', 2, 12, 29, 0.16666666666666666]
['library', 1, 6, 29, 0.16666666666666666]
['enter', 1, 6, 29, 0.16666666666666666]
['anchor', 3, 19, 29, 0.15789473684210525]
['awaken', 2, 13, 29, 0.15384615384615385]
['temple', 1, 7, 29, 0.14285714285714285]
['loose', 1, 10, 29, 0.1]
['enchanter', 1, 13, 29, 0.07692307692307693]
['advent', 1, 17, 29, 0.058823529411764705]
['murdac', 1, 18, 29, 0.05555555555555555]
['wishbringer', 1, 19, 29, 0.05263157894736842]
['plundered', 0, 2, 29, 0.0]
['huntdark', 0, 2, 29, 0.0]
['planetfall', 0, 4, 29, 0.0]
['trinity', 0, 4, 29, 0.0]
['905', 0, 4, 23, 0.0]
['moonlit', 0, 2, 29, 0.0]
['hollywood', 0, 4, 29, 0.0]
['reverb', 0, 11, 29, 0.0]
['hhgg', 0, 2, 29, 0.0]
['lostpig', 0, 3, 29, 0.0]


### 09-08 hongyuan mei
- stripe subtasks
- rank first 70 steps:
['pentari', 13, 25, 49, 0.52, [12, 19, 20, 21, 27, 28, 30, 31, 32, 33, 36, 40, 44]]
['curses', 16, 31, 71, 0.5161290322580645, [25, 28, 29, 30, 41, 46, 47, 50, 57, 58, 59, 61, 65, 68, 69, 70]]
['ztuu', 13, 26, 70, 0.5, [12, 17, 21, 27, 38, 39, 40, 42, 44, 52, 57, 63, 64]]
['afflicted', 16, 32, 71, 0.5, [18, 27, 31, 32, 33, 36, 42, 43, 47, 49, 51, 52, 53, 54, 64, 65]]
['gold', 12, 28, 71, 0.42857142857142855, [9, 16, 17, 25, 26, 27, 28, 63, 64, 66, 67, 68]]
['zork1', 16, 39, 71, 0.41025641025641024, [6, 14, 21, 44, 49, 50, 53, 54, 55, 56, 64, 65, 66, 67, 68, 69]]
['spirit', 15, 37, 71, 0.40540540540540543, [21, 22, 23, 24, 25, 33, 34, 37, 46, 47, 48, 49, 59, 65, 70]]
['night', 12, 30, 63, 0.4, [7, 8, 14, 18, 19, 21, 49, 50, 52, 60, 62, 63]]
['deephome', 12, 34, 70, 0.35294117647058826, [23, 27, 28, 35, 36, 37, 38, 49, 51, 53, 58, 69]]
['ludicorp', 12, 36, 71, 0.3333333333333333, [12, 23, 33, 34, 35, 46, 47, 48, 52, 55, 56, 57]]
['dragon', 12, 37, 71, 0.32432432432432434, [8, 17, 18, 19, 20, 36, 37, 39, 59, 65, 66, 69]]
['omniquest', 11, 38, 70, 0.2894736842105263, [12, 13, 18, 19, 26, 38, 39, 52, 65, 66, 70]]



|          | gpt3.5 acc (without map) | gpt3.5 acc (with map)|
|----------|-------------------------|----------------------|
| pentari |       2/13           |         3/13                 |
| curses |     1/10          |     4/10                    |
| ztuu |       0/9           |       2/9            |
| afflicted  |       2/12             |         3/12          |
| gold  |        1/7      |       1/7     |
| zork1  |      1/16           |        5/16            |
| night  |        0/12             |         1/12           |
| spirit  |      3/13             |        6/13           |
| deephome  |     2/11              |        4/11           |
| ludicorp  |     0/12               |      4/12             |
| dragon  |       1/5              |         0/5           |
| omniquest  |     0/11               |     2/11              |



|          | gpt4 acc (without map) | gpt4 acc (with map)|
|----------|-------------------------|----------------------|
| pentari |         3/13          |           9/13          |
| curses |    7/16       |            12/16       |  (16?)
| ztuu |      6/13           |        11/13          |
| afflicted  |        4/16              |          12/16         |
| gold  |       3/12          |        6/12        |
| zork1  |      7/16            |        11/16           |
| night  |       4/12             |        9/12            |
| spirit  |      10/15              |       14/15             |
| deephome  |      9/12              |      12/12              |
| ludicorp  |    8/12               |         10/12           |
| dragon  |      5/12               |        7/12         |
| omniquest  |      3/11              |         9/11         |
