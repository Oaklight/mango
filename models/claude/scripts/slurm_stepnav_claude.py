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
        if exp_result['task'] == task_config['task'] and exp_result['src_node'] == task_config['src_node'] and exp_result['dst_node'] == task_config['dst_node'] and exp_result['path_gt'] == task_config['path_gt']:
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

# setup config
claude_config_path = 'claude_configs/{}/{}.{}.json'.format(game, game, claude_version)
claude_config = read_json(claude_config_path)
# print('gpt_config: {}'.format(gpt_config))

# setup test data
all2all = read_json('{}/{}/{}.all2all.json'.format(maps_dir, game, game))

# filter out experiments that have already been run
task = 'stepnav'
exp_save_path = os.path.join(claude_config['save_path'], '{}-{}'.format(task, claude_config['model']))
print('exp_save_path: ', exp_save_path)
unfinished_all2all = []
for traj in all2all:
    task_config = {
        'task': task,
        'src_node': traj['src_node'],
        'dst_node': traj['dst_node'],
        'path_gt': traj['path_details']
    }
    if not check_exp_exists(exp_save_path, task_config):
        unfinished_all2all.append(traj)
print('unfinished_all2all: ', unfinished_all2all)
print('len(unfinished_all2all): ', len(unfinished_all2all))

time_of_wait = 10
for traj in unfinished_all2all:
    src_node = traj['src_node']
    dst_node = traj['dst_node']
    path_gt = traj['path_details']

    # create task config
    unique_stamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + '_' + str(random.randint(0,1e3)).zfill(3)
    task_config_folder = 'task_configs/{}'.format(game)
    if not os.path.exists(task_config_folder):
        os.makedirs(task_config_folder)
    task_config_path = os.path.join(task_config_folder, '{}.stepnav_{}.json'.format(game, unique_stamp))
    task_config = {'task': 'stepnav', 'src_node': src_node, 'dst_node': dst_node, 'path_gt': path_gt, 'save_path': claude_config['save_path']}
    with open(task_config_path, 'w') as f:
        json.dump(task_config, f, indent=4)

    python_cmd = 'OPENAI_API_KEY={} python step_navigation.py --claude-config-path {} --task-config-path {}'.format(os.getenv("OPENAI_API_KEY"), claude_config_path, task_config_path)
    print('python_cmd: {}'.format(python_cmd))
    slurm_save_path = os.path.join(task_config['save_path'].replace('results', 'slurm'), '{}-{}'.format(task_config['task'], claude_config['model']))
    if not os.path.exists(slurm_save_path):
        os.makedirs(slurm_save_path)
    os.system('sbatch --wrap="{}" --output {}/slurm-%4j.out'.format(python_cmd, slurm_save_path))

    print('Sleeping for {} seconds to avoid hitting OpenAI API rate limit'.format(time_of_wait))
    time.sleep(time_of_wait)
        
