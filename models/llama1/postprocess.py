import os
import json
import re
from tqdm import tqdm

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as fin:
        res_json = json.load(fin)
    return res_json

def write2file(file_path, json_file):
    with open(file_path,'w+', encoding='utf-8') as fout:
        json.dump(json_file, fout, ensure_ascii=False, indent=4)
    

def gather_folder(input_folder):
    folder_list = []

    contents = os.listdir(input_folder)

    files = []
    folders = []

    for item in contents:
        item_path = os.path.join(input_folder, item)
        if os.path.isfile(item_path):
            files.append(item)
        elif os.path.isdir(item_path):
            folders.append(item)

    if len(folders) == 0:
        if sum([f.endswith('marker.txt') for f in files]) != 0:
            folder_list.append(input_folder)
        else:
            pass
    elif len(files) == 0:
        for folder in folders:
            folder_path = os.path.join(input_folder, folder)
            folder_list.extend(gather_folder(folder_path))
    else:
        print(f"Folder with mixed content: {input_folder}")
        return

    return folder_list

def calc_cutoff_step(str_in):
    pattern = r"==>STEP NUM: (.+?)\n"
    result_list = re.findall(string=str_in, pattern=pattern)
    return result_list[-1]

def main():
    llama_folder = '/remote-home/pli/gamegpt_utils/data_backup/llama_results'
    output_folder_processed = '/remote-home/pli/gamegpt_utils/data_backup/results_processed'
    if not os.path.exists(output_folder_processed):
        os.makedirs(output_folder_processed)

    game_list = os.listdir(llama_folder)
    print ("game list: {}".format(game_list))
    print ("#game: {}".format(len(game_list)))

    for game_name in tqdm(sorted(game_list)):
        print ("processing {} ...".format(game_name))
        llama_30b_path = os.path.join(llama_folder, game_name, '30B') # /remote-home/pli/gamegpt_utils/inhouse_llms/llama_results/905/30B

        pathgen_output_path = os.path.join(output_folder_processed, game_name, 'results', 'path_gen_llama')
        stepnav_output_path = os.path.join(output_folder_processed, game_name, 'results', 'stepnav_llama')
        pathgen_output_path_anno = os.path.join(output_folder_processed, game_name, 'results', 'path_gen_llama_anno')
        stepnav_output_path_anno = os.path.join(output_folder_processed, game_name, 'results', 'stepnav_llama_anno') 
        if not os.path.exists(pathgen_output_path):
            os.makedirs(pathgen_output_path)
        if not os.path.exists(stepnav_output_path):
            os.makedirs(stepnav_output_path)
        if not os.path.exists(pathgen_output_path_anno):
            os.makedirs(pathgen_output_path_anno)
        if not os.path.exists(stepnav_output_path_anno):
            os.makedirs(stepnav_output_path_anno)

        result_folder_list = gather_folder(llama_30b_path)
        print ("# all2all list: {}".format(len(result_folder_list)))

        for result_folder in result_folder_list: # result_folder: /remote-home/pli/gamegpt_utils/inhouse_llms/llama_results/905/30B/llama-from-Bedroom-to-Bathroom-sample-id-0
            all2all_id = int(result_folder.split('-')[-1])
            # print ("tmp all2all idx: {}".format(all2all_id))

            config = {
                "game_name": game_name,
                "model": "llama",
                "temperature": 0,
                "all2all_idx": all2all_id
            }

            folder_file = sorted(os.listdir(result_folder))

            if len(folder_file) == 2: 
                file_path = os.path.join(result_folder, folder_file[-1])
                file_content = load_json(file_path)
                assert 'anno_update' in file_content.keys()

            elif len(folder_file) > 2:
                try:
                    origin_file_path = os.path.join(result_folder, [f for f in folder_file if f.startswith('results_2023')][0])
                    fixed_file_path = os.path.join(result_folder, [f for f in folder_file if f.startswith('results_fixed')][0])
                    origin_file_content = load_json(origin_file_path)
                    fixed_file_content = load_json(fixed_file_path)
                    for key in origin_file_content.keys():
                        if key in ['anno_update', 'save_path']:
                            continue
                        if key in ['raw_response_step_navi', 'raw_response_path_gen', 'response_step_navi', 'response_path_gen']:
                            assert origin_file_content[key] == fixed_file_content[key]
                    assert 'anno_update' in fixed_file_content.keys()
                except:
                    # print ("debug: ", sorted(folder_file))
                    origin_file_path = os.path.join(result_folder, [f for f in folder_file if f.startswith('results_2023')][-2])
                    fixed_file_path = os.path.join(result_folder, [f for f in folder_file if f.startswith('results_2023')][-1])
                    fixed_file_content = load_json(fixed_file_path)
                    assert 'anno_update' in fixed_file_content.keys(), '{} error, {}, {}'.format(game_name, result_folder, folder_file)
                file_content = fixed_file_content
            else:
                print ("folder_file: ", folder_file)
                exit(0)

            action_list = [step['action'] for step in file_content['path_gt']]

            try:
                path_gen_path = eval(file_content['response_path_gen']) if file_content['response_path_gen'] != "" else ""
            except:
                path_gen_path = ''

            try:
                step_navi_path = eval(file_content['response_step_navi']) if file_content['response_step_navi'] != "" else ""
            except:
                step_navi_path = ''

            try:
                path_gen_path_anno = eval(file_content['response_path_gen_anno']) if file_content['response_path_gen_anno'] != "" else ""
            except:
                path_gen_path_anno = ''

            try:
                step_navi_path_anno = eval(file_content['response_step_navi_anno']) if file_content['response_step_navi_anno'] != "" else ""
            except:
                step_navi_path_anno = ''


            pathgen_sample_info = {
                "config": config,
                "task": "pathgen",
                "src_node": file_content['src_node'],
                "dst_node": file_content['dst_node'],
                "path_gt": file_content['path_gt'],
                "pretext": file_content['prefix_walkthrough'],
                "question": file_content['question_path_gen'],
                "cut_off_num": calc_cutoff_step(file_content['prefix_walkthrough']),
                "path": path_gen_path,
                "raw_response": file_content['raw_response_path_gen']
                }
            
            stepnav_sample_info = {
                "config": config,
                "task": "stepnav",
                "src_node": file_content['src_node'],
                "dst_node": file_content['dst_node'],
                "path_gt": file_content['path_gt'],
                "action_list": action_list,
                "pretext": file_content['prefix_walkthrough'],
                "question": file_content['question_step_navi'],
                "cut_off_num": calc_cutoff_step(file_content['prefix_walkthrough']),
                "path": step_navi_path,
                "raw_response": file_content['raw_response_step_navi']
                }
            
            pathgen_anno_sample_info = {
                "config": config,
                "task": "pathgen",
                "src_node": file_content['src_node'],
                "dst_node": file_content['dst_node'],
                "path_gt": file_content['path_gt'],
                "pretext": file_content['prefix_walkthrough_anno'],
                "question": file_content['question_path_gen'],
                "cut_off_num": calc_cutoff_step(file_content['prefix_walkthrough_anno']),
                "path": path_gen_path_anno,
                "raw_response": file_content['raw_response_path_gen_anno']
                }
            
            stepnav_anno_sample_info = {
                "config": config,
                "task": "stepnav",
                "src_node": file_content['src_node'],
                "dst_node": file_content['dst_node'],
                "path_gt": file_content['path_gt'],
                "action_list": action_list,
                "pretext": file_content['prefix_walkthrough_anno'],
                "question": file_content['question_step_navi'],
                "cut_off_num": calc_cutoff_step(file_content['prefix_walkthrough_anno']),
                "path": step_navi_path_anno,
                "raw_response": file_content['raw_response_step_navi_anno']
                }
            write2file(os.path.join(pathgen_output_path, 'pathgen_results_{}.json'.format(pathgen_sample_info['config']['all2all_idx'])), pathgen_sample_info)
            write2file(os.path.join(stepnav_output_path, 'stepnav_results_{}.json'.format(stepnav_sample_info['config']['all2all_idx'])), stepnav_sample_info)
            write2file(os.path.join(pathgen_output_path_anno, 'pathgen_anno_results_{}.json'.format(pathgen_anno_sample_info['config']['all2all_idx'])), pathgen_anno_sample_info)
            write2file(os.path.join(stepnav_output_path_anno, 'stepnav_anno_results_{}.json'.format(stepnav_anno_sample_info['config']['all2all_idx'])), stepnav_anno_sample_info)

        print ("Good Job!!!")



if __name__ == '__main__':
    main()