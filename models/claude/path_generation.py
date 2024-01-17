import os
import json
import datetime
import random
import traceback
from tenacity import retry, stop_after_attempt, wait_fixed, wait_random_exponential

import claude_dialogue


def save_json(save_path, save_object, prefix=''):
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    now = datetime.datetime.now()
    now_str = now.strftime("%Y-%m-%d-%H-%M-%S")
    json_path = os.path.join(save_path, prefix + now_str + '_' + str(random.randint(0,1e3)).zfill(3) + '.json')
    json_object = json.dumps(save_object, indent=4)
    with open(json_path, 'w') as f:
        f.write(json_object)
    return json_path

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def call_claude_with_retry(dialogue, question):
    return dialogue.call_claude(question)

if __name__=='__main__':

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--claude-config-path', type=str, help='path to gpt config json file')
    parser.add_argument('--src-node', type=str, help='source node for the path generation task')
    parser.add_argument('--dst-node', type=str, help='destination node for the path generation task')
    parser.add_argument('--task-config-path', type=str, help='path to task config json file. Overrides src_node and dst_node if present')
    args = parser.parse_args()

    # initialize dialogue model
    with open(args.claude_config_path, 'r') as f:
        config = json.load(f)
    dialogue = claude_dialogue.Dialogue(**config)
    pretext = dialogue.get_pretext()

    # set up question
    if args.task_config_path is not None:
        with open(args.task_config_path, 'r') as f:
            task_config = json.load(f)
        src_node = task_config['src_node']
        dst_node = task_config['dst_node']
    else:
        src_node = args.src_node
        dst_node = args.dst_node

    question = """
    Can you find a path from {} to {}, and format the output as a python list of python dictionary with keys 'prev_node', 'node' and 'action'? Start your response with '['
    """.format(src_node, dst_node)
    results = {
        'config': config,
        'pretext': pretext,
        'task': task_config['task'] if args.task_config_path is not None else 'pathgen',
        'src_node': src_node,
        'dst_node': dst_node,
        'path_gt': task_config['path_gt'] if args.task_config_path is not None else None,
        'question': question,
    }

    completion = call_claude_with_retry(dialogue, question)
    print('question: {}'.format(question))
    print('completion: {}'.format(completion))

    try:
        path_str = '[' + completion.split('[')[1].split(']')[0] + ']'
        path_lst = eval(path_str)
        for step in path_lst:
            assert isinstance(step, dict), 'Each step in the path should be a dictionary.'
        results['path'] = path_lst
        results['raw_response'] = completion
        
    except Exception:
        print('Response is not properly structured.')
        results['error_message'] = traceback.format_exc()

    save_path = os.path.join(config['save_path'], '{}-{}'.format(results['task'], config['model']))
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    json_path = save_json(save_path, results, prefix='results_')
    print('results saved to {}'.format(json_path))