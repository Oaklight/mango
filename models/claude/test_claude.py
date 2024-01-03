import os
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

def main():
    user_input = "===========\n==>STEP NUM: 0\n==>ACT: Init\n==>OBSERVATION: The phone rings.\n\nOh, no - how long have you been asleep? Sure, it was a tough night, but... This is bad. This is very bad.\n\nThe phone rings.\n\n  -----\n9:05 by Adam Cadre\nv1.11 (2012.0724) / Original release 2000.0103\n  -----\n\nBedroom (in bed)\nThis bedroom is extremely spare, with dirty laundry scattered haphazardly all over the floor. Cleaner clothing can be found in the dresser. A bathroom lies to the south, while a door to the east leads to the living room.\n\nOn the end table are a telephone, a wallet and some keys.\n\nThe phone rings.\n\n===========\n==>STEP NUM: 1\n==>ACT: answer phone\n==>OBSERVATION: You pick up the phone. \"Hadley!\" a shrill voice cries. \"Hadley, haven't you even left yet?? You knew that our presentation was at nine o'clock sharp! First the thing with the printers, now this - there won't even be enough left of you for Bowman to fire once he's done with you. Now get the hell down here!!\"\n\nClick.\n\n===========\n==>STEP NUM: 2\n==>ACT: stand up\n==>OBSERVATION: You get out of bed.\n\nBedroom\nThis bedroom is extremely spare, with dirty laundry scattered haphazardly all over the floor. Cleaner clothing can be found in the dresser. A bathroom lies to the south, while a door to the east leads to the living room.\n\nOn the end table are a telephone, a wallet and some keys.\n\n===========\n==>STEP NUM: 3\n==>ACT: south\n==>OBSERVATION: Bathroom\nThis is a far from luxurious but still quite functional bathroom, with a sink, toilet and shower. The bedroom lies to the north.\n\n===========\n==>STEP NUM: 4\n==>ACT: remove watch\n==>OBSERVATION: You take off the gold watch.\n\n===========\n==>STEP NUM: 5\n==>ACT: remove clothes\n==>OBSERVATION: You take off the soiled clothing.\n\n===========\n==>STEP NUM: 6\n==>ACT: drop all\n==>OBSERVATION: soiled clothing: Dropped.\ngold watch: Dropped.\n\n===========\n==>STEP NUM: 7\n==>ACT: enter shower\n==>OBSERVATION: You step into the shower, turn on the water, and within a few moments you feel like a new man. But no time to dawdle - you hop back out again and dry off in record time.\n\n===========\n==>STEP NUM: 8\n==>ACT: take watch\n==>OBSERVATION: Taken.\n\n===========\n==>STEP NUM: 9\n==>ACT: wear watch\n==>OBSERVATION: You put on the gold watch.\n\n===========\n==>STEP NUM: 10\n==>ACT: north\n==>OBSERVATION: Bedroom\nThis bedroom is extremely spare, with dirty laundry scattered haphazardly all over the floor. Cleaner clothing can be found in the dresser. A bathroom lies to the south, while a door to the east leads to the living room.\n\nOn the end table are a telephone, a wallet and some keys.\n\n===========\n==>STEP NUM: 11\n==>ACT: get all from table\n==>OBSERVATION: wallet: Removed.\nkeys: Removed.\n\n===========\n==>STEP NUM: 12\n==>ACT: open dresser\n==>OBSERVATION: You open the dresser, revealing some clean clothing.\n\n===========\n==>STEP NUM: 13\n==>ACT: get clothes\n==>OBSERVATION: Taken.\n\n===========\n==>STEP NUM: 14\n==>ACT: wear clothes\n==>OBSERVATION: You put on the clean clothing.\n\n===========\n==>STEP NUM: 15\n==>ACT: east\n==>OBSERVATION: Living room\nThe furniture isn't as carefully arranged as one might like, and it's a bit lacking in the luxuries that might make this a more pleasant place to spend an evening - no stereo, no TV, no DVD, none of that - but this living room is still nicer than most of those in this neighborhood. A kitchenette lies to the east, the bedroom to the west and the front door to the south.\n\n===========\n==>STEP NUM: 16\n==>ACT: open front door\n==>OBSERVATION: You open the front door.\n\n===========\n==>STEP NUM: 17\n==>ACT: south\n==>OBSERVATION: Driveway\nThis is quite a seedy neighborhood, but there isn't really anywhere in the whole Las Mesas metro area that isn't at least a little rundown. Of course, the locals may complain about the ugliness and the crime, but the fact is that a starter home like this one would cost easily five times as much in someplace like Las Playas - and that's if you could find one.\n\nThe house lies to the north. A car is parked here in the driveway.\n\n===========\n==>STEP NUM: 18\n==>ACT: unlock car\n==>OBSERVATION: Unlocked.\n\n===========\n==>STEP NUM: 19\n==>ACT: enter car\n==>OBSERVATION: You climb inside and start up the engine.\n\nDriving\nAh, scenic Las Mesas. Man, this place is an absolute toilet. Soon you'll be able to afford to get the hell out of here - provided you can avoid making any more slip-ups on the job.\n\nAs you cruise down the road, you notice a freeway onramp approaching. Would you like to get on?\n\n===========\n==>STEP NUM: 20\n==>ACT: no\n==>OBSERVATION: It turns out that the ramp was blocked anyway - some sort of maintenance work. You keep driving.\n\nAs you cruise down the road, you see the familiar Loungent Technologies building approaching. Would you like to stop here?\n\n===========\n==>STEP NUM: 21\n==>ACT: no\n==>OBSERVATION: Soon the Loungent building is in your rear-view mirror. You keep driving.\n\nAs you cruise down the road, you notice another freeway onramp approaching. Would you like to get on?\n\n===========\n==>STEP NUM: 22\n==>ACT: yes\n==>OBSERVATION: You merge onto the freeway, crank up the radio, and vanish without a trace.\n\n\n    *** You have left Las Mesas ***\n\n\nWritten and programmed by Adam Cadre. Tested by Alexandra Hoffer. v1.00 tested by Liza Daly. Additional thanks to Elizabeth Sweeney, Jonathan Blask, and Jonatan Bleicher.\n\nWould you like to RESTART, RESTORE a saved game or QUIT\n\n===========" + '\n'
    user_input += "The allowed actions are: ['down', 'east', 'enter car', 'north', 'northeast', 'northwest', 'south', 'southeast', 'southwest', 'stand up', 'up', 'west']" + '\n'
    user_input += "The list of places are: ['Bathroom', 'Bedroom', 'Living room', 'Driveway', 'Inside of the Car']" + '\n'
    user_input += "Can you find a path from Bathroom to Inside of the Car, and format the output as a python list of python dictionary with keys'prev_node', 'node' and 'action'? \n    Start your response with '['\n"
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    print ("api_key: ", api_key)
    anthropic = Anthropic(api_key=api_key)
    completion = anthropic.completions.create(
        model="claude-2",
        max_tokens_to_sample=300,
        prompt=f"{HUMAN_PROMPT} {user_input}{AI_PROMPT}",
        temperature=0.0
    )
    print(completion.completion)

    # question: Can you find a path from Bedroom to Bathroom, and format the output as a python list of python dictionary with keys'prev_node', 'node' and 'action'? \n    Start your response with '['\n
    # res1:
    # Here is one possible path from the Bedroom to the Bathroom as a list of dictionaries with 'prev_node', 'node', and 'action' keys:
    # [
    #     {'prev_node': 'Bedroom', 'node': 'Bathroom', 'action': 'south'},
    # ]
    #
    # res2:
    # Here is a possible path from Bedroom to Bathroom as a list of dictionaries:
    # [{'prev_node': 'Bedroom', 'node': 'Bathroom', 'action': 'south'}]   

    # question: Can you find a path from Bathroom to Inside of the Car, and format the output as a python list of python dictionary with keys'prev_node', 'node' and 'action'? \n    Start your response with '['\n
    # res1:
    # Here is one possible path from Bathroom to Inside of the Car:
    # [
    # {'prev_node': 'Bathroom', 'node': 'Bedroom', 'action': 'north'},
    # {'prev_node': 'Bedroom', 'node': 'Living room', 'action': 'east'},  
    # {'prev_node': 'Living room', 'node': 'Driveway', 'action': 'south'},
    # {'prev_node': 'Driveway', 'node': 'Inside of the Car', 'action': 'enter car'}
    # ]

    # res2:
    # Here is one possible path from Bathroom to Inside the Car:
    # [
    #     {'prev_node': 'Bathroom', 'node': 'Bedroom', 'action': 'north'},
    #     {'prev_node': 'Bedroom', 'node': 'Living room', 'action': 'east'}, 
    #     {'prev_node': 'Living room', 'node': 'Driveway', 'action': 'south'},
    #     {'prev_node': 'Driveway', 'node': 'Inside the Car', 'action': 'enter car'}
    # ]


if __name__ == '__main__':
    main()