# Inference Code


## Setup

For GPT models:
```bash
export OPENAI_API_KEY=<YOUR KEY>
```

For Claude models:
```bash
export ANTHROPIC_API_KEY=<YOUR KEY>
```

For Llama2:
> Refer to `https://github.com/meta-llama/llama` for downloading the models' checkpoints.    
> We used the 13B llama-2 base model for our experiments.

For RWKV:
> Refer to `https://github.com/BlinkDL/ChatRWKV` for downloading the models' checkpoints.    
> We used the model `RWKV-4-Pile-14B-20230313-ctx8192-test1050` with the tokenizer `20B_tokenizer.json`.

 ## Running Example

 ```bash
 # for llama2, you may need `CUDA_VISIBLE_DEVICES=0,1 torchrun --nproc_per_node 2`
CUDA_VISIBLE_DEVICES=0 python main.py --exp_tag debug --data_folder '.../data' --save_folder '.../results' --game_name '905' --task_type 'route_finding' --model_name 'claude-instant-1' --batch_size 1
 ```

Please check the `parse_args()` function in `main.py` for more information.

## Contact
> Peng Li: pengli [dot] ds [at] gmail [dot] com