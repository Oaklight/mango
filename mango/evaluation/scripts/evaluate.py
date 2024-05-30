import os
import json
from multiprocessing import Pool, cpu_count
from mango.evaluation.map_evaluator import MapEvaluator, TaskType
import fire
def evaluate_map(map_rst_dir, map_dir, map_name, output_dir,task_type):
    map_name=str(map_name)
    """
    Evaluates the map destination finding results and saves the summary.

    Args:
        rst_dir (str): Directory with result files.
        map_dir (str): Directory with map files.
        map_name (str): Name of the map to evaluate.
        output_dir (str): Directory to save the evaluation summary.
    """
    os.makedirs(output_dir, exist_ok=True)
    evaluator = MapEvaluator(map_dir, map_name)
    rst = evaluator.evaluate_map(map_rst_dir, task_type=task_type)
    all_info=rst['all_info']
    rst_summary = rst['summary']
    
    summary_file = os.path.join(output_dir, f'{map_name}_summary.json')
    with open(summary_file, 'w') as f:
        json.dump(rst_summary, f, indent=4)
    with open(summary_file.replace('_summary.json','_all_info.json'), 'w') as f:
        json.dump(all_info, f, indent=4)

def evaluate_model(rst_dir, map_dir, output_dir,task_type):
    """
    Evaluates multiple maps using multiprocessing and saves the combined summary.

    Args:
        rst_dir (str): Directory with result files.
        map_dir (str): Directory with map files.
        output_dir (str): Directory to save the evaluation summaries.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    map_names = os.listdir(map_dir)
    args = [(os.path.join(rst_dir,map_name), map_dir, map_name, output_dir,task_type) for map_name in map_names if map_name in os.listdir(rst_dir)]
    
    with Pool(cpu_count()) as p:
        p.starmap(evaluate_map, args)
    
    # Wait until all processes are finished
    all_summaries = {}
    for map_name in map_names:
        summary_file = os.path.join(output_dir, f'{map_name}_summary.json')
        if os.path.exists(summary_file):
            with open(summary_file, 'r') as f:
                all_summaries[map_name] = json.load(f)
    
    
    
    easy_all=[v["easy"] for k,v in all_summaries.items()]
    hard_all=[v["hard"] for k,v in all_summaries.items()]
    total_all=[v["all"] for k,v in all_summaries.items()]
    final_summary={
        "easy":get_final_summary(easy_all),
        "hard":get_final_summary(hard_all),
        "all":get_final_summary(total_all)
    }
    combined_summary = {
        'summary': final_summary,
        **all_summaries
    }
    combined_summary_file = os.path.join(output_dir, 'all_summary.json')
    with open(combined_summary_file, 'w') as f:
        json.dump(combined_summary, f, indent=4)

    
def get_final_summary(list_of_dict):
    """
    Calculate the average, weighted average, and weighted average by valid tasks summaries.

    Args:
        all_summaries (dict): Dictionary containing summaries for all maps.

    Returns:
        tuple: (average_summary, weighted_average_summary, weighted_avg_valid_summary)
    """
    final_summary = {}
    for k,v in list_of_dict[0].items():
        final_summary[k]=0
    
    sum_up_key=[k for k,v in list_of_dict[0].items() if not k.endswith('average')]
    avg_by_total_keys=[k for k,v in list_of_dict[0].items() if 'error' in k and not k in sum_up_key]
    avg_by_valid_keys=[k for k,v in list_of_dict[0].items() if k not in sum_up_key and k not in avg_by_total_keys]

    for info in list_of_dict:
        for k,v in info.items():
            if k in sum_up_key:
                final_summary[k]+=v
            if k in avg_by_total_keys:
                final_summary[k]+=v*info['total_task']
            if k in avg_by_valid_keys:
                final_summary[k]+=v*info['valid_task']
    for k,v in final_summary.items():
        if k in avg_by_total_keys:
            final_summary[k]=v/final_summary['total_task'] if final_summary['total_task']!=0 else 0
        if k in avg_by_valid_keys:
            final_summary[k]=v/final_summary['valid_task'] if final_summary['valid_task']!=0 else 0
    return final_summary
    
            
        
        


    

    


def evaluate_map_dest_finding(map_rst_dir, map_dir, map_name, output_dir):
    task_type = TaskType.DestFinding
    evaluate_map(map_rst_dir, map_dir, map_name, output_dir,task_type)

def evaluate_model_dest_finding(rst_dir, map_dir, output_dir):
    task_type = TaskType.DestFinding
    evaluate_model(rst_dir, map_dir, output_dir,task_type)

def evaluate_map_route_finding(map_rst_dir, map_dir, map_name, output_dir):
    task_type = TaskType.RouteFinding
    evaluate_map(map_rst_dir, map_dir, map_name, output_dir,task_type)

def evaluate_model_route_finding(rst_dir, map_dir, output_dir):
    task_type = TaskType.RouteFinding
    evaluate_model(rst_dir, map_dir, output_dir,task_type)

if __name__ == "__main__":
    fire.Fire({
        'evaluate_map_dest_finding': evaluate_map_dest_finding,
        'evaluate_model_dest_finding': evaluate_model_dest_finding,
        'evaluate_map_route_finding': evaluate_map_route_finding,
        'evaluate_model_route_finding': evaluate_model_route_finding
    })
