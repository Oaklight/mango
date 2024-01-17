import os, json, time, datetime, random, argparse
import tqdm
from itertools import islice

# function to read json file
def read_json(json_path):
    with open(json_path, 'r') as f:
        json_object = json.load(f)
    return json_object

def check_exp_exists(exp_dir, task_config):
    if not os.path.exists(exp_dir):
        return False
    for exp_filename in os.listdir(exp_dir):
        exp_path = os.path.join(exp_dir, exp_filename)
        with open(exp_path, 'r') as f:
            exp_result = json.load(f)
        if exp_result['task'] == task_config['task'] and exp_result['src_node'] == task_config['src_node'] and exp_result['dst_node'] == task_config['dst_node']:
            return True
    return False

parser = argparse.ArgumentParser()
parser.add_argument('--game', type=str, required=True)
parser.add_argument('--claude-version', type=str, choices=['claude2', 'claude_instant_1'], required=True)
parser.add_argument('--maps-dir', type=str, default='/home-nfs/pengli/workspace/projects/mango/data')
args = parser.parse_args()

game = args.game
claude_version = args.claude_version
maps_dir = args.maps_dir
print('game: {}'.format(game))
print('claude_version: {}'.format(claude_version))
print('maps_dir: {}'.format(maps_dir))

# all_pairs dictionary
all_pairs_path = '{}/{}/{}.all_pairs.json'.format(maps_dir, game, game)
all_pairs = read_json(all_pairs_path)

# setup config
claude_config_path = 'claude_configs/{}/{}.{}.json'.format(game, game, claude_version)
claude_config = read_json(claude_config_path)
# print('gpt_config: {}'.format(gpt_config))

# setup test data
all2all = read_json('{}/{}/{}.all2all.json'.format(maps_dir, game, game))

# filter out experiments that have already been run
task = 'pathgen'
exp_save_path = os.path.join(claude_config['save_path'], '{}-{}'.format(task, claude_config['model']))
print('exp_save_path: ', exp_save_path)
unfinished_all_pairs = []
for traj in all_pairs:
    task_config = {
        'task': task,
        'src_node': traj['src_node'],
        'dst_node': traj['dst_node'],
    }
    if not check_exp_exists(exp_save_path, task_config):
        unfinished_all_pairs.append(traj)
print('unfinished_all_pairs: ', unfinished_all_pairs)

time_of_wait = 10

for traj in unfinished_all_pairs:
    src_node = traj['src_node']
    dst_node = traj['dst_node']
    
    # look for the same traj in all2ll
    for traj2 in all2all:
        if traj2['src_node'] == src_node and traj2['dst_node'] == dst_node:
            path_gt = traj2['path_details']
            break
    
    # create task config
    unique_stamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + '_' + str(random.randint(0,1e3)).zfill(3)
    task_config_folder = 'task_configs/{}'.format(game)
    if not os.path.exists(task_config_folder):
        os.makedirs(task_config_folder)
    task_config_path = os.path.join(task_config_folder, '{}.pathgen_{}.json'.format(game, unique_stamp))
    task_config = {'task': 'pathgen', 'src_node': src_node, 'dst_node': dst_node, 'path_gt': path_gt}
    with open(task_config_path, 'w') as f:
        json.dump(task_config, f, indent=4)

    python_cmd = 'ANTHROPIC_API_KEY={} python path_generation.py --claude-config-path {} --task-config-path {}'.format(os.getenv("ANTHROPIC_API_KEY"), claude_config_path, task_config_path)
    print('python_cmd: {}'.format(python_cmd))
    # slurm_save_path = 'slurm/gen3/pathgen-gpt3'
    slurm_save_path = os.path.join(claude_config['save_path'].replace('results', 'slurm'), '{}-{}'.format(task_config['task'], claude_config['model']))
    if not os.path.exists(slurm_save_path):
        os.makedirs(slurm_save_path)
    slurm_cmd = "sbatch --wrap='{}' --output {}/slurm-%4j.out".format(python_cmd, slurm_save_path)
    print('slurm_cmd: {}'.format(slurm_cmd))
    os.system(slurm_cmd)

    print('Sleeping for {} seconds to avoid hitting OpenAI API rate limit'.format(time_of_wait))
    time.sleep(time_of_wait)

