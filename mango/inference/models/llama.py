"""
https://github.com/meta-llama/llama
"""
import os
from llama import Llama

class LlamaModel:
    def __init__(self, model_name, temperature, ckpt_dir, tokenizer_path, max_batch_size, 
                 max_seq_len=4096, max_tokens_to_sample=512, top_p=0.95) -> None:
        self.model = Llama.build(
            ckpt_dir=ckpt_dir,
            tokenizer_path=tokenizer_path,
            max_seq_len=max_seq_len,
            max_batch_size=max_batch_size,
        )
        self.tokenizer = self.model.tokenizer

        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens_to_sample = max_tokens_to_sample
        self.top_p = top_p

    def query_model(self, prompt_list):
        # TODO: Inference Time Pruning
        responses = self.model.text_completion(
            prompt_list, 
            max_gen_len=self.max_tokens_to_sample, 
            temperature=self.temperature, 
            top_p = self.top_p
        )  
        return responses

    def cutoff_input(self, text, max_token_num, max_step_num):
        cut_off_step_num = float('inf')

        enc = self.tokenizer.encode(text, bos=True, eos=False)
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

            sample['question'] ="""!!! Can you find a path from "{}" to "{}"?\nFormat the output as a python list of python dictionary with keys 'location_before', 'action' and 'location_after'. \n\n""".format(src_node, dst_node) + "Answer: [{'location_before':"
            model_input = f"{prefix_walkthrough}\n\n{action_space_prompt}\n{location_space_prompt}\n{sample['question']}"
            input_list.append(model_input)

        try:
            raw_outputs = self.query_model(input_list)
            # postprocess
            answers = ["[{'location_before':" + output["generation"].strip() for output in raw_outputs]
        except Exception as e:
            answers = [f"Error: {e}"]

        return samples, answers

    def desti_finding(self, samples):
        input_list = []
        for sample in samples:
            src_node = sample['src_node']
            path_gt = sample['path_details']
            action_list = [step['action'] for step in path_gt]

            walkthrough_text = sample['walkthrough_text']
            prefix_walkthrough = '!!! Here is a walkthrough of a text game:\n' + walkthrough_text
            
            action_space_list = sample['action_space_list']
            action_space_prompt = "The allowed actions are: {}.".format(action_space_list)

            location_space_list = sample['location_space_list']
            location_space_prompt = "The list of locations are: {}.".format(location_space_list)

            sample['question'] ="""!!! Starting from location "{}", perform a list of action {}, where are you now?\nDescribe the trajectory in a python list of python dictionary with keys 'location_before', 'action' and 'location_after'. \n\n""".format(src_node, action_list) + "Answer: [{'location_before':"
            model_input = f"{prefix_walkthrough}\n\n{action_space_prompt}\n{location_space_prompt}\n{sample['question']}"
            input_list.append(model_input)


        try:
            raw_outputs = self.query_model(input_list)
            # postprocess
            answers = ["[{'location_before':" + output["generation"].strip() for output in raw_outputs]
        except Exception as e:
            answers = [f"Error: {e}"]

        return samples, answers