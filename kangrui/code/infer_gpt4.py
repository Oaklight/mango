import openai
from utils.gpt_prompt_utils import evaluate_game
import argparse
import os

map_dir='/share/data/mei-work/kangrui/github/mango/data'
api_key="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"
openai.api_key = api_key

def main(game_name,model_name, task_name,result_dir):
    evaluate_game(map_dir,result_dir,game_name,task_name,model_name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_name', default='gpt-4',choices=['gpt-3.5-turbo', 'gpt-4'], help='Model name')
    parser.add_argument('--result_dir', default='/share/data/mei-work/kangrui/github/mango/kangrui/data/gpt-games-results-clean-new-new',
                         help='result path')
    args = parser.parse_args()
    for game_name in os.listdir(args.result_dir):
    #     if game_name in ['planetfall','pentari','ludicorp','zork1','spellbrkr',
    # 'ballyhoo','murdac','zenon','zork2','zork3',
    # '905','anchor','awaken','adventureland','afflicted',
    # 'balances','curses','cutthroat','deephome','detective',
    # 'dragon','enchanter','enter','gold','hhgg',
    # 'hollywood','huntdark','infidel','inhumane','jewel',
    # 'karn','library','loose','lostpig','lurking',
    # 'moonlit','murdac','night','omniquest','partyfoul']:
    #         continue
        print(f"start evaluating {game_name}-{args.model_name}-pathgen")
        main(game_name,args.model_name, 'pathgen',args.result_dir)
        print(f"end evaluating {game_name}-{args.model_name}-pathgen")
        print('**********************************************************************')
        print(f"start evaluating {game_name}-{args.model_name}-stepnav")
        main(game_name,args.model_name, 'stepnav',args.result_dir)
        print(f"end evaluating {game_name}-{args.model_name}-stepnav")
        print('--------------------------------------------------------------------')