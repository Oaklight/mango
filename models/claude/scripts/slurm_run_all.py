import os
import time

maps_folder = '/home-nfs/pengli/workspace/projects/mango/data'
for game  in os.listdir(maps_folder):
    python_cmd_lst = []
    python_cmd_lst.append('python scripts/slurm_pathgen_claude.py --game {} --claude-version {} --maps-dir {}'.format(game, "claude2", maps_folder))
    python_cmd_lst.append('python scripts/slurm_stepnav_claude.py --game {} --claude-version {} --maps-dir {}'.format(game, "claude2", maps_folder))
    python_cmd_lst.append('python scripts/slurm_pathgen_claude.py --game {} --claude-version {} --maps-dir {}'.format(game, "claude_instant_1", maps_folder))
    python_cmd_lst.append('python scripts/slurm_stepnav_claude.py --game {} --claude-version {} --maps-dir {}'.format(game, "claude_instant_1", maps_folder))

    start = time.time()
    for python_cmd in python_cmd_lst:
        print(python_cmd)
        os.system(python_cmd)
    end = time.time()
    print('game {} took {} seconds'.format(game, end - start))
