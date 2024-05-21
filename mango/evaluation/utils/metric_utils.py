from collections import deque
import time
from enum import IntEnum

class EvalMetric(IntEnum):
    Strict = 0
    Loose = 1

class TaskType(IntEnum):
    PathGen = 0
    StepNav = 1

# edit distance score
def score_result(s1, s2, eval_metric=EvalMetric.Strict):
    if eval_metric == EvalMetric.Strict:
        return 1 if s1.lower() == s2.lower() else 0
    elif eval_metric == EvalMetric.Loose:
        s1 = s1.lower()
        s2 = s2.lower()
        
        m = len(s1) + 1
        n = len(s2) + 1

        dp = [[0] * n for _ in range(m)]

        for i in range(m):
            dp[i][0] = i

        for j in range(n):
            dp[0][j] = j

        for i in range(1, m):
            for j in range(1, n):
                if s1[i - 1] == s2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = min(
                        dp[i - 1][j] + 1,  
                        dp[i][j - 1] + 1,  
                        dp[i - 1][j - 1] + 1  
                    )
        
        # Compute the normalized score
        max_len = max(len(s1), len(s2))
        score = 1 - dp[m - 1][n - 1] / max_len if max_len != 0 else 0
        return score


# specific eval for dest finding
def get_multi_destnode(G,src_node,actions):
    # return all the nodes that can be reached given G,source_node and action list
    def bfs_get_multi_des(G,src_node,actions):
        dest_nodes=[]
        queue = deque([(src_node, 0)])

        while queue:
            current_node, step = queue.popleft()

            # If we've finished all actions
            if step == len(actions):
                dest_nodes.append(current_node)

            # If we haven't finished all actions yet
            if step < len(actions):
                for (_, next_node, attr) in G.out_edges(current_node, data=True):
                    if attr['action'].lower() == actions[step].lower(): 
                        queue.append((next_node, step + 1))

        return dest_nodes
   
    return bfs_get_multi_des(G,src_node,actions)



# new eval function sets, for both route_finding and dest_finding
def nice_eval(G, path, src_node, dst_node, eval_metric=EvalMetric.Loose):
    assert eval_metric in EvalMetric

    # Get unique action list from the graph
    actions_gt = list({attr.get('action').lower() for (_, _, attr) in G.edges(data=True)})
    
    # get action list of the path
    path_actions=[]
    for node_info in path:
        if "action" in node_info.keys() and isinstance(node_info["action"],str):
            node_action=node_info["action"].lower()
            action=max(actions_gt, key=lambda v: score_result(node_action, v, eval_metric))
            path_actions.append(action)
    
    def bfs_route_finding(G,src_node,dst_node,actions):
        start_time=time.time()
        queue = deque([(src_node, 0)])
        # visited = set([src_node])

        while queue:
            if time.time()-start_time>60:
                raise "maxloop limit exceeds"
            current_node, step = queue.popleft()

            # If we've arrived at the destination and finished all actions
            if current_node == dst_node and step == len(actions):
                return True

            # If we haven't finished all actions yet
            if step < len(actions):
                for (_, next_node, attr) in G.out_edges(current_node, data=True):
                    if attr['action'].lower() == actions[step].lower(): #and next_node not in visited:
                        # visited.add(next_node)
                        queue.append((next_node, step + 1))

        return False
    
    return bfs_route_finding(G,src_node,dst_node,path_actions)


def harsh_eval(G, path, start_node, end_node,src_node_key='prev_node',dst_node_key='node'):
    if path[0][src_node_key]!= start_node or path[-1][dst_node_key] != end_node:
        return 0

    for edge in path:
        if not G.has_edge(edge[src_node_key], edge[dst_node_key]):
            return 0

        # support both DiGraph and MultiDiGraph
        edge_data = G.get_edge_data(edge[src_node_key], edge[dst_node_key])
        action_list=[]
        if 'action' in edge_data.keys():
            action_list.append(edge_data['action'])
        for k,v in edge_data.items():
            if isinstance(v,dict) and 'action' in v.keys():
                action_list.append(v['action'])

        if not edge["action"] in action_list:
            return 0
    return 1

def success_rate(G, path,src_node,dst_node,eval_metric,task_type,actions=None):
    assert task_type in TaskType
    assert eval_metric in EvalMetric

    if task_type==TaskType.PathGen:
        return nice_eval(G, path, src_node, dst_node,eval_metric)
    
    elif task_type==TaskType.StepNav:
        dst_nodes=get_multi_destnode(G,src_node,actions)
        lower_dst_nodes=[node.lower() for node in dst_nodes]
        assert dst_node.lower() in lower_dst_nodes
        return max([score_result(path[-1]['node'].lower(), v) for v in lower_dst_nodes])

def reasoning_acc(G, path,src_node,dst_node,actions,task_type):
    assert task_type in TaskType
    if task_type==TaskType.PathGen:
        return harsh_eval(G, path, src_node, dst_node)
    elif task_type==TaskType.StepNav:
        if len(path)!=len(actions):
            return False
        for idx,edge in enumerate(path):
            if edge['action']!=actions[idx]:
                return False
        return harsh_eval(G, path, src_node, path[-1]['node'])