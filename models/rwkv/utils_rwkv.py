import os, copy, types, gc, sys
import numpy as np
np.set_printoptions(precision=4, suppress=True, linewidth=200)
import torch
torch.backends.cudnn.benchmark = True
torch.backends.cudnn.allow_tf32 = True
torch.backends.cuda.matmul.allow_tf32 = True

import time

# Tune these below (test True/False for all of them) to find the fastest setting:
# torch._C._jit_set_profiling_executor(True)
# torch._C._jit_set_profiling_mode(True)
# torch._C._jit_override_can_fuse_on_cpu(True)
# torch._C._jit_override_can_fuse_on_gpu(True)
# torch._C._jit_set_texpr_fuser_enabled(False)
# torch._C._jit_set_nvfuser_enabled(False)

########################################################################################################

def init_model(rwkv_dir, model_path, device_id):
    sys.path.append(rwkv_dir)
    from src.model_run import RWKV_RNN
    from src.utils import TOKENIZER

    args = types.SimpleNamespace()

    args.RUN_DEVICE = "cuda"  # cuda // cpu
    # fp16 (good for GPU, does NOT support CPU) // fp32 (good for CPU) // bf16 (worse accuracy, supports CPU)
    args.FLOAT_MODE = "fp16"

    os.environ["RWKV_JIT_ON"] = '1' # '1' or '0', please use torch 1.13+ and benchmark speed
    args.MODEL_NAME = model_path
    args.ctx_len = 100000
    os.environ["RWKV_RUN_DEVICE"] = args.RUN_DEVICE

    args.vocab_size = 50277
    args.head_qk = 0
    args.pre_ffn = 0
    args.grad_cp = 0
    args.my_pos_emb = 0

    model = RWKV_RNN(args).to('cuda:{}'.format(device_id))
    tokenizer = TOKENIZER(rwkv_dir + "/20B_tokenizer.json").to('cuda:{}'.format(device_id))
    print ("model and tokenizer loaded!!!")
    return model, tokenizer

model_tokens = []
model_state = None

def run_rnn(model, tokens, chunk_len = 512):
    global model_tokens, model_state

    tokens = [int(x) for x in tokens]
    model_tokens += tokens

    while len(tokens) > 0:
        out, model_state = model.forward(tokens[:chunk_len], model_state)
        tokens = tokens[chunk_len:]
    out[0] = -999999999  # disable <|endoftext|>
    return out

def rwkv_infer(model, tokenizer, context, stop_token='', temperature = 1.0, top_p=0.95, ctx_len = 100000, 
               pred_length = 512, chunk_len= 512):
    global model_tokens, model_state
    model_tokens = []
    model_state = None

    time_slot = {}
    time_ref = time.time_ns()
    def record_time(name):
        if name not in time_slot:
            time_slot[name] = 1e20
        tt = (time.time_ns() - time_ref) / 1e9
        if tt < time_slot[name]:
            time_slot[name] = tt

    context_ids = tokenizer.encode(context)
    out = run_rnn(model, context_ids, chunk_len = chunk_len)
    gc.collect()
    torch.cuda.empty_cache()
    record_time('preprocess')

    begin = len(model_tokens) # context ids
    out_last = begin
    outputs = []
    for i in range(begin, begin + pred_length):
        token = tokenizer.sample_logits(
            out,
            model_tokens, # not use
            ctx_len, # not use
            temperature=temperature,
            top_p=top_p,
        )
        out = run_rnn(model, [token], chunk_len = chunk_len)
        
        xxx = tokenizer.decode(model_tokens[out_last:])
        # print ("*" * 20)
        # print ("decoded id: ", model_tokens[out_last:])
        # print ("decoded output token: ", xxx)
        outputs.append(xxx)
        if stop_token != '' and stop_token in xxx:
            break
        if '\ufffd' not in xxx: # avoid utf-8 display issues
            # print(xxx, end='', flush=True)
            out_last = i + 1

    record_time('total')
    print(
        f"\n\n--- preprocess {round(time_slot['preprocess'], 2)}s, generation {round(time_slot['total']-time_slot['preprocess'], 2)}s ", end = ''
    )

    return context + ''.join(outputs)

if __name__ == '__main__':
    # model, tokenizer = init_model('/remote-home/pli/RWKV-LM/ckpts/rwkv-4-raven/RWKV-4-Raven-14B-v12-Eng98%-Other2%-20230523-ctx8192')
    model, tokenizer = init_model('/remote-home/pli/RWKV-LM/ckpts/rwkv-4-pile-14b/RWKV-4-Pile-14B-20230313-ctx8192-test1050')
    context = """!!! Here is a walkthrough of a text game:\n\n==>STEP NUM: 0\n==>ACT: Init\n==>OBSERVATION: The phone rings.\n\nOh, no - how long have you been asleep? Sure, it was a tough night, but... This is bad. This is very bad.\n\nThe phone rings.\n\n  -----\n9:05 by Adam Cadre\nv1.11 (2012.0724) / Original release 2000.0103\n  -----\n\nBedroom (in bed)\nThis bedroom is extremely spare, with dirty laundry scattered haphazardly all over the floor. Cleaner clothing can be found in the dresser. A bathroom lies to the south, while a door to the east leads to the living room.\n\nOn the end table are a telephone, a wallet and some keys.\n\nThe phone rings.\n\n\n==>STEP NUM: 1\n==>ACT: answer phone\n==>OBSERVATION: You pick up the phone. \"Hadley!\" a shrill voice cries. \"Hadley, haven't you even left yet?? You knew that our presentation was at nine o'clock sharp! First the thing with the printers, now this - there won't even be enough left of you for Bowman to fire once he's done with you. Now get the hell down here!!\"\n\nClick.\n\n\n==>STEP NUM: 2\n==>ACT: stand up\n==>OBSERVATION: You get out of bed.\n\nBedroom\nThis bedroom is extremely spare, with dirty laundry scattered haphazardly all over the floor. Cleaner clothing can be found in the dresser. A bathroom lies to the south, while a door to the east leads to the living room.\n\nOn the end table are a telephone, a wallet and some keys.\n\n\n==>STEP NUM: 3\n==>ACT: south\n==>OBSERVATION: Bathroom\nThis is a far from luxurious but still quite functional bathroom, with a sink, toilet and shower. The bedroom lies to the north.\n\n\n==>STEP NUM: 4\n==>ACT: remove watch\n==>OBSERVATION: You take off the gold watch.\n\n\n==>STEP NUM: 5\n==>ACT: remove clothes\n==>OBSERVATION: You take off the soiled clothing.\n\n\n==>STEP NUM: 6\n==>ACT: drop all\n==>OBSERVATION: soiled clothing: Dropped.\ngold watch: Dropped.\n\n\n==>STEP NUM: 7\n==>ACT: enter shower\n==>OBSERVATION: You step into the shower, turn on the water, and within a few moments you feel like a new man. But no time to dawdle - you hop back out again and dry off in record time.\n\n\n==>STEP NUM: 8\n==>ACT: take watch\n==>OBSERVATION: Taken.\n\n\n==>STEP NUM: 9\n==>ACT: wear watch\n==>OBSERVATION: You put on the gold watch.\n\n\n==>STEP NUM: 10\n==>ACT: north\n==>OBSERVATION: Bedroom\nThis bedroom is extremely spare, with dirty laundry scattered haphazardly all over the floor. Cleaner clothing can be found in the dresser. A bathroom lies to the south, while a door to the east leads to the living room.\n\nOn the end table are a telephone, a wallet and some keys.\n\n\n==>STEP NUM: 11\n==>ACT: get all from table\n==>OBSERVATION: wallet: Removed.\nkeys: Removed.\n\n\n==>STEP NUM: 12\n==>ACT: open dresser\n==>OBSERVATION: You open the dresser, revealing some clean clothing.\n\n\n==>STEP NUM: 13\n==>ACT: get clothes\n==>OBSERVATION: Taken.\n\n\n==>STEP NUM: 14\n==>ACT: wear clothes\n==>OBSERVATION: You put on the clean clothing.\n\n\n==>STEP NUM: 15\n==>ACT: east\n==>OBSERVATION: Living room\nThe furniture isn't as carefully arranged as one might like, and it's a bit lacking in the luxuries that might make this a more pleasant place to spend an evening - no stereo, no TV, no DVD, none of that - but this living room is still nicer than most of those in this neighborhood. A kitchenette lies to the east, the bedroom to the west and the front door to the south.\n\n\n==>STEP NUM: 16\n==>ACT: open front door\n==>OBSERVATION: You open the front door.\n\n\n==>STEP NUM: 17\n==>ACT: south\n==>OBSERVATION: Driveway\nThis is quite a seedy neighborhood, but there isn't really anywhere in the whole Las Mesas metro area that isn't at least a little rundown. Of course, the locals may complain about the ugliness and the crime, but the fact is that a starter home like this one would cost easily five times as much in someplace like Las Playas - and that's if you could find one.\n\nThe house lies to the north. A car is parked here in the driveway.\n\n\n==>STEP NUM: 18\n==>ACT: unlock car\n==>OBSERVATION: Unlocked.\n\n\n==>STEP NUM: 19\n==>ACT: enter car\n==>OBSERVATION: You climb inside and start up the engine.\n\nDriving\nAh, scenic Las Mesas. Man, this place is an absolute toilet. Soon you'll be able to afford to get the hell out of here - provided you can avoid making any more slip-ups on the job.\n\nAs you cruise down the road, you notice a freeway onramp approaching. Would you like to get on?\n\n\n!!! Starting from location 'Bathroom', perform a list of action ['north', 'east', 'south'], where are you now?\nDescribe the trajectory in a python list of python dictionary with keys 'location_before', 'action' and 'location_after'.\nThe allowed actions are: ['down', 'east', 'enter car', 'north', 'northeast', 'northwest', 'south', 'southeast', 'southwest', 'stand up', 'up', 'west'].\nThe list of locations are: ['Bathroom', 'Bedroom', 'Living room', 'Driveway', 'Inside of the Car'].\n\nAnswer: [{'location_before': 'Bathroom', 'action': 'north', 'location_after': """
    res = rwkv_infer(model, tokenizer, context, stop_token=']', chunk_len=12)
    print (res)
    print ("good job!")