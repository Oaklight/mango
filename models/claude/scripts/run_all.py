import os

maps_folder = 'maps_batch_1'
for game  in os.listdir(maps_folder):

    if game == 'zork1_old':
        continue
    
    python_cmd_lst = []
    python_cmd_lst.append('python scripts/pathgen_gpt.py --game {} --gpt-version {} --maps-dir {}'.format(game, 3, maps_folder))
    python_cmd_lst.append('python scripts/pathgen_gpt.py --game {} --gpt-version {} --maps-dir {}'.format(game, 4, maps_folder))
    python_cmd_lst.append('python scripts/stepnav_gpt.py --game {} --gpt-version {} --maps-dir {}'.format(game, 3, maps_folder))
    python_cmd_lst.append('python scripts/stepnav_gpt.py --game {} --gpt-version {} --maps-dir {}'.format(game, 4, maps_folder))
    
    for python_cmd in python_cmd_lst:
        print(python_cmd)
        os.system(python_cmd)