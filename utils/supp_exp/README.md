# Supplementary Experiments

We conducted two supplementary experiments in an attempt to convert walkthroughs into maps directly and try to solve the route/path finding problem with classic searching methods. 

But you can see from our following experiments that it is hard to convert natural language walkthroughs into ideal maps, and thus it is hard to solve these problems with graph searching algorithms.

## Experiment 1

We extracted the corresponding locations individually for each step's observation. We used examples with golden locations for the first 5 steps of each game as the demonstrations:

### Prompt:

```
The following is an observation of a character in a game. Please determine the character's location based on the description. Here are some examples:

Example 1:
==>ACT: north
==>OBSERVATION: North of House
You are facing the north side of a white house. There is no door here, and all the windows are boarded up. To the north a narrow path winds through the trees.
==>LOCATION: North of House

Example 2:
…

Then, each step of the game was input sequentially, like the following example, and extract the predicted result:

> If you can identify the character's location from the text, please just reply with that location; otherwise, reply with 'None':

==>ACT: down
==>OBSERVATION: Egyptian Room
The solid-gold coffin used for the burial of Ramses II is here.
==>LOCATION:
```

### Results

We conducted experiments on six games: `Zork1` , `Night` , `Partyfoul` , `Plundered` , `Spirit` , and `Temple` . We found that the proportions of locations predicted using this method, which matched our manually labeled locations, were as follows for each game: `0.9` , `0.6` , `0.81` , `0.5` , `0.66` , and `0.76` , respectively. We provide examples of incorrect cases followed by error reason for each error step.

#### Zork1

```
==>ACT: drop egg
==>OBSERVATION: Dropped.
==>LOCATION: Up a Tree
(Golden: None)
Error reason: There is no change in location, but similar sentences in the demo have a change in location, so it predicts the change in location.

==>STEP NUM: 50
==>ACT: south
==>OBSERVATION: Altar
There is a sword here.
==>LOCATION: None
(Golden: Altar)
Error reason: did not identify the location.
```

#### Night

```
==>ACT: east
==>OBSERVATION: Hall Outside Elevator
You're in a short east-west hall off the main hall.  You can see an elevator here.  (They forgot the sign, but it's still out of order.)

There is a door on the south wall.
==>LOCATION: Hall (unknown floor, middle of north/south hall)
(Golden: Hall (1st floor, middle of north/south hall))
Error reason: Can't identify the specific floor

==>ACT: west
==>OBSERVATION: Hall
==>LOCATION: Hall (3rd floor, middle of north/south hall)
(Golden:  Hall (1st floor, middle of north/south hall))
Error reason: Can't identify the specific floor.
```

#### Partyfoul

```
==>OBSERVATION: Darkness
It is pitch dark, and you can't see a thing.

"Well, don't you think you might want to do something about this electrical problem?" you hear Abbey yell.

"I'm working on it now, dear, " you hear Ron shout from somewhere distant in the rest of the house.
==>LOCATION: Darkness
(golden: None)
Error reason: 'Darkness' can not be a location.
```

#### Plundered

```
==>ACT: get coffer
==>OBSERVATION: Taken.
   "Aaieeee!" echoes a scream, followed by several grunts and thumps.
==>LOCATION: Cabin
(golden: None)
Error reason: There is no change in location, but similar sentences in the demo have a change in location, so it predicts the change in location.

==>ACT: open cupboard
==>OBSERVATION: Opened. It is a dark messy bed, set entirely within and filling the large cupboard. A cabin boy must sleep here when Jamison isn't using it. Kicked into a far corner is a pile of clothes.
==>LOCATION: Cupboard
(golden: None)
Error reason: identified an object as a location.
```

#### Spirit

```
==>ACT: read note
==>OBSERVATION: The note, in a hastily written scrawl, reads:
"Please stop by the chapel as soon as you can.
-- Joseph"
==>LOCATION: The character's location is the Monastery.
(golden: None)
Error reason: There is no change in location, but similar sentences in the demo have a change in location, so it predicts the change in location.
The context is too long, resulting in the output being natural language rather than a concise location.

==>ACT: take pallet
==>OBSERVATION: Taken.
==>LOCATION: Your Quarters
(golden: None)
```

#### Temple

```
==>ACT: examine table
==>OBSERVATION: The base of the stone table is covered with carvings, each showing different kinds of creatures, or maybe Gods, standing on stone tables. Humans, who seem to be reciting prayers or spells, are standing in front of the creatures.

You spot something behind the table. Pushing the cobwebs aside, you reveal some writing, crudely painted on the stone wall with black paint.
==>LOCATION: Stone table
(golden: None)
Error reason: identified an object as a location.

==>ACT: west
==>OBSERVATION: Road
Wandering through the deserted city you stumble upon something unexpected. A large crack yawns darkly into the side of one of the ponderous elliptical buildings to the north. You wonder what monumental forces could have effected this rupture. The road extends to the east and west.

Charles comes walking behind you.
==>LOCATION: Road
(golden: Road (east/west))
Error reason: Can't identify the exact location.
```

## Experiment 2

In this experiment, we attempted to have GPT-3.5 directly articulate all the location changes first. We conducted experiments on the aforementioned six games: `Zork1` , `Night` , `Partyfoul` , `Plundered` , `Spirit` , and `Temple` . For convenience, we only requested the GPT-3.5 to output the location changes corresponding to the first 30 steps.

### Prompt

The instruction is in the following format:

```
!! Here is a walkthrough of a textgame:
==>STEP NUM: 0
==>ACT: Init
==>OBSERVATION: Copyright (c) 1981, 1982, 1983 Infocom, Inc. All rights reserved.
ZORK is a registered trademark of Infocom, Inc.
Revision 88 / Serial number 840726

West of House
You are standing in an open field west of a white house, with a boarded front door.
There is a small mailbox here.

==>STEP NUM: 1
==>ACT: north
==>OBSERVATION: North of House
You are facing the north side of a white house. There is no door here, and all the windows are boarded up. To the north a narrow path winds through the trees.

… 
!! Please identify the changes in the location of the character from this walkthrough. Output a list of dictionaries with keys 'location before, ' 'action, ' and 'location after.' Start your response with '['.
```

### Results

The following are the returns for each game from their respective walkthrough. We observed that there are mistakes in all games when translating walkthrough into global map. We select 3 shorter game to report the mistakes while the samilar error reasons persist for other games as well. The error reasons are listed below each error step.

#### Zork1

```
[
{'location before': 'West of House', 'action': 'north', 'location after': 'North of House'}, 
{'location before': 'North of House', 'action': 'north', 'location after': 'Forest Path'}, 
{'location before': 'Forest Path', 'action': 'up', 'location after': 'Up...
(Error reason: structure error.)
{'location before': 'Living Room', 'action': 'get sword', 'location after': 'Living Room'}, 
(Error reason: missing many location changes.
up a tree --> forest path
forest path --> north of house
north of house --> behind house
....)
{'location before': 'Living Room', 'action': 'move rug', 'location after': 'Living Room'}, 
{'location before': 'Living Room', 'action': 'open trapdoor', 'location after': 'Cellar'}, 
{'location before': 'Cellar', 'action': 'north', 'location after': 'The Troll Room'}, 
{'location before': 'The Troll Room', 'action': 'kill troll with sword', 'location after': 'The Troll Room'}
(error reason: location error.)
]
```

#### Partyfoul

```
[
{'location before': 'Living Room', 'action': 'look', 'location after': 'Living Room'}, 
(Error reason: not a transition.)
{'location before': 'Living Room', 'action': 'give drink to frank', 'location after': 'Living Room'}, 
{'location before': 'Living Room', 'action': 'look at frank', 'location after': 'Living Room'}, 
{'location before': 'Living Room', 'action': 'look at ron', 'location after': 'Living Room'}, 
(Error reason: are not location transition.)
{'location before': 'Living Room', 'action': 'west', 'location after': 'Guest Room'}, 
{'
```

#### Temple

```
[
{'location before': 'Void', 'action': 'examine me', 'location after': 'A cascade of red colour explodes below you.'}, 
{'location before': 'A cascade of red colour explodes below you.', 'action': 'examine shadow', 'location after': 'Suddenly there is a new... 
'action': 'unlock door with key', 'location after': 'Hall'}, 
(Error reason: structure error.)
{'location before': 'Hall', 'action': 'open door', 'location after': 'Before A Dark Tower'}, 
{'location before': 'Before A Dark Tower', 'action': 'south', 'location after': 'Charles comes walking behind you.'}
]
```
