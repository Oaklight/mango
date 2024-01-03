import os, json, tqdm, datetime, random, argparse

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
parser.add_argument('--gpt-version', type=str, choices=['3', '4'], required=True)
parser.add_argument('--maps-dir', type=str, default='maps')
args = parser.parse_args()

game = args.game
gpt_version = args.gpt_version
maps_dir = args.maps_dir
print('game: {}'.format(game))
print('gpt_version: {}'.format(gpt_version))
print('maps_dir: {}'.format(maps_dir))

# code to anno  dictionary
code2anno_path = '{}/{}/{}.code2anno.json'.format(maps_dir,game, game)
code2anno_dict = read_json(code2anno_path)

# all_pairs dictionary
all_pairs_path = '{}/{}/{}.all_pairs.json'.format(maps_dir, game, game)
all_pairs = read_json(all_pairs_path)

# setup config
gpt_config_path = 'gpt_configs/{}/{}.gpt{}.json'.format(game, game, gpt_version)
gpt_config = read_json(gpt_config_path)

# setup test data
all2all = read_json('{}/{}/{}.all2all.json'.format(maps_dir, game, game))

# run path generation
for traj in tqdm.tqdm(all_pairs):
    machine_src_node = traj['src_node']
    machine_dst_node = traj['dst_node']
    src_node = code2anno_dict[machine_src_node]
    dst_node = code2anno_dict[machine_dst_node]

    # look for the same traj in all2ll
    for traj2 in all2all:
        if traj2['src_node'] == machine_src_node and traj2['dst_node'] == machine_dst_node:
            path_gt = traj2['path_details']
            break
    # path_gt = traj['path_details']

    # create task config
    unique_stamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + '_' + str(random.randint(0,1e3)).zfill(3)
    task_config_folder = 'task_configs/{}'.format(game)
    if not os.path.exists(task_config_folder):
        os.makedirs(task_config_folder)
    task_config_path = os.path.join(task_config_folder, '{}.pathgen_{}.json'.format(game, unique_stamp))
    task_config = {'task': 'pathgen', 'src_node': src_node, 'dst_node': dst_node, 'path_gt': path_gt}
    
    # check if the experiment alreay exists
    exp_save_path = os.path.join(gpt_config['save_path'], '{}-{}'.format(task_config['task'], gpt_config['model']))
    if check_exp_exists(exp_save_path, task_config):
        print('exp {} exists, skip'.format(task_config))
        # print('exp exists, skip')
        continue

    with open(task_config_path, 'w') as f:
        json.dump(task_config, f, indent=4)

    # python_cmd = """python path_generation.py --gpt-config-path {} --src-node "{}" --dst-node "{}" """.format(gpt_config_path, src_node, dst_node)
    python_cmd = 'python path_generation.py --gpt-config-path {} --task-config-path {}'.format(gpt_config_path, task_config_path)
    print('python_cmd: {}'.format(python_cmd))
    os.system(python_cmd)
