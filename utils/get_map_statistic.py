import json
import os
import fire

def get_map_statistic(map_dir,game_name,step_num=500):
    game_name=str(game_name)
    map_statistic={
        "num_locations":0,
        "num_edges":0,
        "avg_len_path":0,
        "num_steps":0,
        "df_hard":0,
        "df_easy":0,
        "rf_hard":0,
        "rf_easy":0,
    }
    # get edges
    with open(os.path.join(map_dir,game_name,f"{game_name}.edges.json"), 'r') as f:
        map_statistic["num_edges"] = len(json.load(f))

    # get locations
    with open(os.path.join(map_dir,game_name,f"{game_name}.locations.json"), 'r') as f:
        map_statistic["num_locations"] = len(json.load(f))
    
    # get walkthrough
    with open(os.path.join(map_dir,game_name,f"{game_name}.walkthrough"), 'r') as f:
        map_statistic["num_steps"] = len(f.read().split("==>STEP NUM:"))-2

    # get all_pairs
    with open(os.path.join(map_dir,game_name,f"{game_name}.all_pairs.jsonl"), 'r') as f:
        for line in f:
            data=json.loads(line)
            if data["min_step_forward_answerable"]<=step_num:
                map_statistic["rf_easy"]+=1
            elif data["min_step_total_answerable"]<=step_num:
                map_statistic["rf_hard"]+=1
    
    # get all2all
    total_path_len=0
    with open(os.path.join(map_dir,game_name,f"{game_name}.all2all.jsonl"), 'r') as f:
        for line in f:
            data=json.loads(line)
            if data["min_step_total_answerable"]<=step_num:
                total_path_len+=len(data["path_details"])
                if data["min_step_forward_answerable"]<=step_num:
                    map_statistic["df_easy"]+=1
                else:
                    map_statistic["df_hard"]+=1
    map_statistic["avg_len_path"]=total_path_len/(map_statistic["df_easy"]+map_statistic["df_hard"]) if (map_statistic["df_easy"]+map_statistic["df_hard"])!=0 else 0


    return map_statistic

def main(map_dir,game_name,step_num=500):
    print(get_map_statistic(map_dir,game_name,step_num))

if __name__ == "__main__":
    fire.Fire(main)

    
