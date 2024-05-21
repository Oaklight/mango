import os
import openai
import tiktoken

# https://github.com/openai/openai-cookbook/blob/main/examples/How_to_handle_rate_limits.ipynb
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff

class GPTModel:
    def __init__(self, model_name, temperature, max_tokens_to_sample=512) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = api_key

        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens_to_sample = max_tokens_to_sample

        self.tokenizer = tiktoken.encoding_for_model('gpt-4-0314')

    retry(wait=wait_random_exponential(min=5, max=60), stop=stop_after_attempt(6))
    def query_model(self, prompt_list):
        # TODO: Inference Time Pruning
        assert len(prompt_list) == 1, "gpt models currently only supprt querying one sample at a time."
        prompt = prompt_list[0]
        
        response = openai.ChatCompletion.create(
            model=self.model_name,
            messages=[{"role": "system","content": "You are a helpful assistant."}, {"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=self.max_tokens_to_sample
        ).choices[0].message

        return [response]

    def cutoff_input(self, text, max_token_num, max_step_num):
        cut_off_step_num = float('inf')
        
        enc = self.tokenizer.encode(text)
        if len(enc) > max_token_num:
            cut_off_text = self.tokenizer.decode(enc[:max_token_num])
            cut_off_step_num = int(cut_off_text.split('NUM: ')[-2].split('\n')[0])
        if cut_off_step_num > max_step_num:
            cut_off_step_num = max_step_num
        cut_off_text = text.split('NUM: {}'.format(cut_off_step_num + 1))[0]
        cut_off_text = '\n'.join(cut_off_text.split('\n')[:-1])
        return cut_off_text, cut_off_step_num

    def process(self, samples, task_type):
        if task_type == "route_finding":
            return self.route_finding(samples)
        elif task_type == "desti_finding":
            return self.desti_finding(samples)

    def route_finding(self, samples):
        input_list = []
        for sample in samples:
            src_node = sample['src_node']
            dst_node = sample['dst_node']

            walkthrough_text = sample['walkthrough_text']
            prefix_walkthrough = '!!! Here is a walkthrough of a text game:\n' + walkthrough_text
            
            action_space_list = sample['action_space_list']
            action_space_prompt = "The allowed actions are: {}.".format(action_space_list)

            location_space_list = sample['location_space_list']
            location_space_prompt = "The list of locations are: {}.".format(location_space_list)

            sample['question'] ="""!!! Can you find a path from "{}" to "{}", and format the output as a python list of python dictionary with keys 'location_before', 'action' and 'location_after'? Start your response with '['.""".format(src_node, dst_node)
            model_input = f"{prefix_walkthrough}\n\n{action_space_prompt}\n{location_space_prompt}\n{sample['question']}"
            input_list.append(model_input)

        try:
            raw_outputs = self.query_model(input_list)
        except Exception as e:
            raw_outputs = [f"Error: {e}"]

        # postprocess
        answers = raw_outputs
        return samples, answers

    def desti_finding(self, samples):
        input_list = []
        for sample in samples:
            src_node = sample['src_node']
            action_list = sample['action_list']

            walkthrough_text = sample['walkthrough_text']
            prefix_walkthrough = '!!! Here is a walkthrough of a text game:\n' + walkthrough_text
            
            action_space_list = sample['action_space_list']
            action_space_prompt = "The allowed actions are: {}.".format(action_space_list)

            location_space_list = sample['location_space_list']
            location_space_prompt = "The list of locations are: {}.".format(location_space_list)

            sample['question'] ="""!!! Starting from place "{}", perform a list of action {}, where are you now? Describe the trajectory in a python list of python dictionary with keys 'location_before', 'action' and 'location_after'. Start your response with '['.""".format(src_node, action_list)
            model_input = f"{prefix_walkthrough}\n\n{action_space_prompt}\n{location_space_prompt}\n{sample['question']}"
            input_list.append(model_input)

        try:
            raw_outputs = self.query_model(input_list)
        except Exception as e:
            raw_outputs = [f"Error: {e}"]

        # postprocess
        answers = raw_outputs
        return samples, answers