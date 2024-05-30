from mango.evaluation.utils.map_utils import get_game_info_with_G_eval
from enum import IntEnum
from mango.evaluation.utils import edit_distance,parse_raw_output
import json
import time
from collections import deque
from typing import Optional
import os
from mango.evaluation.config import KEY_MAPPING
from collections import defaultdict
class EvalMetric(IntEnum):
    Strict = 0
    Loose = 1

class TaskType(IntEnum):
    RouteFinding = 0
    DestFinding = 1

class MapEvaluator:
    def __init__(self, map_dir:str,map_name:str,key_mapping:Optional[dict]=None):
        self.G_eval,\
        self.G,\
        self.actions,\
        self.locations,\
        self.all2all,\
        self.all_pairs,\
        self.walkthrough=get_game_info_with_G_eval(map_dir,map_name)
        self.key_mapping=KEY_MAPPING
        if key_mapping is not None:
            self.key_mapping=key_mapping


    def matching_score(self,s1:str,s2:str,metric):
        if metric == EvalMetric.Strict:
            return 1 if s1.lower() == s2.lower() else 0
        elif metric == EvalMetric.Loose:
            return edit_distance(s1,s2)
    
    def parse_llm_raw_output(self,raw_output,func_parser=None):
        if func_parser is not None:
            return func_parser(raw_output)
        else:
            return parse_raw_output(raw_output,self.key_mapping)
    
    def bfs_get_multi_des(self,src_node,actions,time_limit=60):
        dest_nodes=[]
        queue = deque([(src_node, 0)])
        #start_time=time.time()
        while queue:
            # if time.time()-start_time>time_limit:
              
            #     return dest_nodes
            current_node, step = queue.popleft()
            #print(current_node,step)
            # If we've finished all actions
            if step == len(actions):
                dest_nodes.append(current_node)

            # If we haven't finished all actions yet
            if step < len(actions):
                for (_, next_node, attr) in self.G_eval.out_edges(current_node, data=True):
                    if attr['action'].lower() == actions[step].lower(): 
                        queue.append((next_node, step + 1))
        #print(dest_nodes)
        return dest_nodes
    
    def eval_actions(self,path, src_node, dst_node,metric):
        actions_gt = list({attr.get('action').lower() for (_, _, attr) in self.G_eval.edges(data=True)})
        path_actions=[]
        for node_info in path:
            if "action" in node_info.keys() and isinstance(node_info["action"],str):
                node_action=node_info["action"].lower()
                action=max(actions_gt, key=lambda v: self.matching_score(node_action, v, metric))
                path_actions.append(action)
        #print(path_actions)
        dest_nodes=self.bfs_get_multi_des(src_node,path_actions)
        #print(metric.name,dest_nodes)
        return max([self.matching_score(dst_node,node,metric) for node in dest_nodes]) if dest_nodes else 0

    def eval_full_path(self,path, src_node, dst_node):
        key_mapping=self.key_mapping
        location_before_key=key_mapping['location_before']
        location_after_key=key_mapping['location_after']
        action_key=key_mapping['action']
        if path[0][location_before_key]!= src_node or path[-1][location_after_key]!= dst_node:             
            return 0
        for edge in path:
            location_before=edge[location_before_key].strip()
            location_after=edge[location_after_key].strip()
            action=edge[action_key].strip()
            if not self.G_eval.has_edge(location_before, location_after):
                
                return 0
            if not any(action == data.get(action_key) for _, _, data in self.G_eval.edges(location_before, data=True) if _ == location_after):
                
                return 0
        for i in range(len(path) - 1):
            if path[i][location_after_key] != path[i + 1][location_before_key]:
                
                return 0
        return 1
            
            


    def eval_route_finding(self,file_path):
        key_mapping=self.key_mapping
        return_rst={
                'loose_score':0,
                'strict_score':0,
                'reasoning_score':0,
                'path_len':0,
                'parsing_error':0,
                'id_error':0,
                'step_num_error':0,
                'is_easy':0,
                'is_hard':0,
            }
        with open(file_path,'r') as f:
            try:
                infer_rst = json.load(f)
            except Exception as e:
                return_rst["parsing_error"]=1
                print(file_path)
                return return_rst

        sample_id=infer_rst[key_mapping['sample_id']]
        game_name=infer_rst[key_mapping['game_name']]
        src_node=infer_rst[key_mapping['src_node']]
        dst_node=infer_rst[key_mapping['dst_node']]
        model_cutoff_num=infer_rst[key_mapping['model_cutoff_num']]
        min_step_total_answerable=infer_rst[key_mapping['min_step_total_answerable']]
        answerable=infer_rst[key_mapping['answerable']]
        response=infer_rst[key_mapping['response']]
        parsed_response=self.parse_llm_raw_output(response)

        if '[' in response and ']' in response:
                if parsed_response is None:
                    print(file_path)
        if sample_id not in self.all_pairs.keys():
            return_rst['id_error']=1
            return return_rst
        
        if min_step_total_answerable>model_cutoff_num:
            return_rst['step_num_error']=1
            return return_rst
        
        if parsed_response is None:
            return_rst['parsing_error']=1
            return return_rst
        
        return_rst['path_len']=1
        ############### maybe comment the following code if using full data ##############################
        for path in self.all2all.values():
            if src_node==path['src_node'] and dst_node==path['dst_node'] and path["diff_shortest"]==0:
                return_rst['path_len']=len(path["path_details"])
                break
        ################################################################################################
        min_step_forward_answerable=self.all_pairs[sample_id]['min_step_forward_answerable']
        if min_step_forward_answerable>model_cutoff_num:
            return_rst['is_hard']=1
        else:
            return_rst['is_easy']=1

        return_rst['loose_score']=self.eval_actions(parsed_response,src_node,dst_node,EvalMetric.Loose)
        return_rst['strict_score']=self.eval_actions(parsed_response,src_node,dst_node,EvalMetric.Strict)
        return_rst['reasoning_score']=self.eval_full_path(parsed_response,src_node,dst_node)

        return return_rst
    
    def eval_dest_finding(self,file_path):
        key_mapping=self.key_mapping
        return_rst={
                'loose_score':0,
                'strict_score':0,
                'reasoning_score':0,
                'path_len':0,
                'parsing_error':0,
                'id_error':0,
                'step_num_error':0,
                'is_easy':0,
                'is_hard':0,
            }
        with open(file_path,'r') as f:
            try:
                infer_rst = json.load(f)
            except Exception as e:
                print(file_path)
                return_rst["parsing_error"]=1
                return return_rst
        sample_id=infer_rst[key_mapping['sample_id']]
        game_name=infer_rst[key_mapping['game_name']]
        src_node=infer_rst[key_mapping['src_node']]
        dst_node=infer_rst[key_mapping['dst_node']]
        model_cutoff_num=infer_rst[key_mapping['model_cutoff_num']]
        min_step_total_answerable=infer_rst[key_mapping['min_step_total_answerable']]
        answerable=infer_rst[key_mapping['answerable']]
        response=infer_rst[key_mapping['response']]
        action_list=infer_rst[key_mapping["action_list"]]
        parsed_response=self.parse_llm_raw_output(response)
        # if '[' in response and ']' in response:
        #     if parsed_response is None:
        #         print(file_path)
        
        if sample_id not in self.all2all.keys():
            return_rst['id_error']=1
            return return_rst
        
        if min_step_total_answerable>model_cutoff_num:
            return_rst['step_num_error']=1
            return return_rst
        
        if parsed_response is None:
            return_rst['parsing_error']=1
            return return_rst
        

        
        return_rst['path_len']=len(self.all2all[sample_id]['path_details'])
        min_step_forward_answerable=self.all2all[sample_id]['min_step_forward_answerable']
        if min_step_forward_answerable>model_cutoff_num:
            return_rst['is_hard']=1
        else:
            return_rst['is_easy']=1

        dst_nodes=self.bfs_get_multi_des(src_node, action_list)
        print(dst_nodes)
        return_rst['loose_score']=max([self.matching_score(dst_node,dst_node,EvalMetric.Loose) for dst_node in dst_nodes] ) if len(dst_nodes)>0 else 0
        return_rst['strict_score']=max([self.matching_score(dst_node,dst_node,EvalMetric.Strict) for dst_node in dst_nodes] ) if len(dst_nodes)>0 else 0
        return_rst['reasoning_score']=max(self.eval_full_path(parsed_response,src_node,dst_node) for dst_node in dst_nodes) if len(dst_nodes)>0 else 0
        return return_rst
    


    def evaluate_map(self,map_rst_dir,task_type:TaskType):
        eval_function={
            TaskType.RouteFinding:self.eval_route_finding,
            TaskType.DestFinding:self.eval_dest_finding,
        }
        all_info=[]
        summary_keys=["loose_score", "strict_score", "reasoning_score", "path_len", "parsing_error", "id_error", "step_num_error"]
        result_summary={}
        for k in ["all","easy","hard"]:
            result_summary[k]={}
            result_summary[k]["total_task"]=0
            result_summary[k]["valid_task"]=0
            for key in summary_keys:
                result_summary[k][key]=0
        for file in os.listdir(map_rst_dir):
            if file.endswith('.json'):
                rst=eval_function[task_type](os.path.join(map_rst_dir,file))
                all_info.append({
                    "file":file,
                    "rst":rst
                })
        def summary(rst_sum,rst):
            rst_sum["total_task"]+=1
            if rst["parsing_error"]==0 and rst["id_error"]==0 and rst["step_num_error"]==0:
                rst_sum["valid_task"]+=1
            for key in summary_keys:
                rst_sum[key]+=rst[key]
        for info in all_info:
            rst=info["rst"]
            summary(result_summary["all"],rst)
            if rst["is_easy"]==1:
                summary(result_summary["easy"],rst)
            if rst["is_hard"]==1:
                summary(result_summary["hard"],rst)
        
        
        for k in ["all","easy","hard"]:
            for key in ["loose_score", "strict_score", "reasoning_score", "path_len", "parsing_error", "id_error", "step_num_error",]:
                if key in ["loose_score", "strict_score", "reasoning_score", "path_len"]:
                    result_summary[k][key+'_average']=result_summary[k][key]/result_summary[k]["valid_task"] if result_summary[k]["valid_task"]>0 else 0
                if key in ["parsing_error", "id_error", "step_num_error"]:
                    result_summary[k][key+'_average']=result_summary[k][key]/result_summary[k]["total_task"] if result_summary[k]["total_task"]>0 else 0
                       
        return {
            "all_info":all_info,
            "summary":result_summary
        }

            



        
        
        