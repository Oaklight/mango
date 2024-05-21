import fire
import os
import multiprocessing
from mango.evaluation.utils.map_utils import get_game_info_with_G_eval
from mango.evaluation.utils.metric_utils import TaskType, EvalMetric
from mango.evaluation.utils.llm_eval_utils import eval_file_per_game, get_csv
import json
import pandas as pd

def eval_game(rst_dir,map_dir,game_name,eval_metric,task_type,average_by_len):
    print(f'handling {game_name}')
    G_eval,G,actions,locations,all2all,all_pairs,walkthrough=get_game_info_with_G_eval(map_dir,game_name)
    all_path_or_pair=all_pairs if task_type==TaskType.PathGen else all2all
    rst=eval_file_per_game(rst_dir,game_name,G_eval,all_path_or_pair,eval_metric,task_type,average_by_len=average_by_len)
    json.dump(rst,open(os.path.join(rst_dir,game_name,'eval_result.json'),'w'))
    print(f'{game_name} finished')


def main(rst_dir:str,map_dir:str,save_path:str,task_type,eval_metric:EvalMetric=EvalMetric.Loose,average_by_len:bool=False):
    """
    Args:
    rst_dir: str, path to the directory containing the inference results
    map_dir: str, path to the directory containing the game maps 
    save_path: str, path to the directory to save the evaluation results
    task_type: TaskType, task type: PathGen or PathPred
    eval_metric: EvalMetric, evaluation metric: Loose or Strict
    average_by_len: bool, whether to average by length
    """
    game_names=[]
    for idx,game_name in enumerate(os.listdir(rst_dir)):
        game_names.append(game_name)

    processes=[]
    for game_name in game_names:
        p=multiprocessing.Process(target=eval_game,args=(rst_dir,map_dir,game_name,eval_metric,task_type,average_by_len))
        p.start()
        processes.append(p)
    for p in processes:
        p.join()

    eval_rst={}
    for game_name in game_names:
        rst=json.load(open(os.path.join(rst_dir,game_name,'eval_result.json'),'r'))
        eval_rst[game_name]=rst['eval_rst']

        
    if not os.path.exists(save_path):
        os.makedirs(save_path)
        
    
    target_name=os.path.join(save_path,f'{eval_metric}_{task_type}_{average_by_len}.csv')


    get_csv(eval_rst,target_name)

    df = pd.read_csv(target_name)
    df = df.sort_values('name')
    average = df.mean()
    
    # Convert first column to object type
    df[df.columns[0]] = df[df.columns[0]].astype(object)

    # Append the average row and set the value of the first column to 'average'
    df.loc[len(df)] = ['average'] + list(average.values)

    # Replace all NA/NaN in df with 'NA'
    df.fillna('NA', inplace=True)
    
    
#     print(average.values)
    weighted_average=[]
    
    weighted_average.append(average.values[6]/average.values[8])
    weighted_average.append(average.values[7]/average.values[8])
    
    weighted_average.append(average.values[12]/average.values[14])
    weighted_average.append(average.values[9]/average.values[11])
    
    weighted_average.append(average.values[13]/average.values[14])
    weighted_average.append(average.values[10]/average.values[11])
    
    for i in range(len(list(average.values))-len(weighted_average)):
        weighted_average.append(0.0)


    df.loc[len(df)] = ['weighted_average'] + weighted_average
    
    df.to_csv(f"{os.path.join(save_path,f'{eval_metric}_{task_type}_{average_by_len}.csv')}", index=False)
    if os.path.join.isfile(target_name):
        os.remove(target_name)
        

if __name__ == '__main__':
    fire.Fire(main)