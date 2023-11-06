import openai
from utils.gpt_prompt_utils import evaluate_game
import argparse

map_dir='/share/data/mei-work/kangrui/github/mango/data'
api_key="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"
openai.api_key = api_key

def main(game_name,model_name, task_name,result_dir):
    evaluate_game(map_dir,result_dir,game_name,task_name,model_name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--game_name', default='zork1', help='game name')
    parser.add_argument('--model_name', default='gpt-3.5-turbo',choices=['gpt-3.5-turbo', 'gpt-4'], help='Model name')
    parser.add_argument('--task_name', default='pathgen',choices=['pathgen', 'stepnav'], help='Task name')
    parser.add_argument('--result_dir', default='/share/data/mei-work/kangrui/github/mango/kangrui/data/gpt-games-results-clean-new',
                         help='result path')
    args = parser.parse_args()
    main(args.game_name,args.model_name, args.task_name,args.result_dir)


