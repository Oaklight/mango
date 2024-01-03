import os
import json
import datetime
import os
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
api_key = os.environ.get("ANTHROPIC_API_KEY")
print ("api_key: ", api_key)

class Dialogue:
    def __init__(self, model='claude-2', temperature=0, max_tokens_to_sample=500, load_path=None, save_path='chats'):
        self.model = model
        self.temperature = temperature
        self.max_tokens_to_sample = max_tokens_to_sample
        self.save_path = save_path
        if load_path is not None:
            self.load_pretext(load_path)
        else:
            self.pretext = [{"role": "system", "content": self.system_message}]

    def load_pretext(self, load_path):

        def load_json(load_path):
            with open(load_path) as json_file:
                return json.load(json_file)
            
        self.pretext = []
        if isinstance(load_path, list):
            for path in load_path:
                self.pretext += load_json(path)
        elif isinstance(load_path, str):
            self.pretext = load_json(load_path)
        else:
            raise Exception('load_path must be a list of strings or a string')

    def get_pretext(self):
        return self.pretext

    def save_pretext(self, save_path, timestamp):
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        json_path = os.path.join(save_path, 'dialogue_' + timestamp + '.json')
        json_object = json.dumps(self.get_pretext(), indent=4)
        with open(json_path, 'w') as f:
            f.write(json_object)

    def call_claude(self, user_prompt, stop=None):
        user_prompt = user_prompt.strip()
        user_prompt = {"role": "user", "content": user_prompt}
        self.pretext = self.pretext + [user_prompt]
        user_input = '\n'.join([tmp_dict['content'] for tmp_dict in self.pretext])
        anthropic = Anthropic(api_key=api_key)
        completion = anthropic.completions.create(
            model=self.model,
            max_tokens_to_sample=self.max_tokens_to_sample,
            prompt=f"{HUMAN_PROMPT} {user_input}{AI_PROMPT}",
            temperature=self.temperature
        ).completion
        self.pretext = self.pretext + [user_prompt] + [{"role": "assistant", "content": completion}]
        return completion

if __name__ == '__main__':
    pass
    config = {
        'model': 'claude-2',
        'temperature': 0,
        'load_path': ['chats/zork_70.json', 'chats/action_space.json', 'chats/place_names.json'],
        'save_path': 'chats',
    }

    dialogue = Dialogue(**config)
    print('===Config===')
    print(config)
    print('===Config===')
    print('Type "exit" to exit the dialogue')
    print('Type "reset" to reset the dialogue')
    print('Type "pretext" to see the current dialogue history')
    print('Type "save" to save the current dialogue history')
    print('====GPT Dialogue Initialized, start asking your questions====')

    while True:
        user_prompt = input('You: ')
        if user_prompt == 'exit':
            break
        elif user_prompt == 'reset':
            dialogue = Dialogue(**config)
            print('====GPT Dialogue Initialized, start asking your questions====')
            continue
        elif user_prompt == 'pretext':
            print('===Pretext===')
            for message in dialogue.get_pretext():
                print(message)
            print('===Pretext===')
            continue
        elif user_prompt == 'save':
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            dialogue.save_pretext(config['save_path'], timestamp)
            print('Pretext saved to', os.path.join(
                config['save_path'], 'dialogue_' + timestamp + '.json'))
            continue
        else:
            completion = dialogue.call_openai(user_prompt)
            response = completion.choices[0].message['content']
            print('Bot:', response)
