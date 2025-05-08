from vllm import LLM, SamplingParams
from transformers import AutoTokenizer

def load_vLLM_model(model_ckpt, seed, tensor_parallel_size=1, half_precision=True, max_num_seqs=256):
    import os
    os.environ['VLLM_USE_V1'] = '0'
    tokenizer = AutoTokenizer.from_pretrained(model_ckpt)
    llm = LLM(
        model=model_ckpt,
        tensor_parallel_size=tensor_parallel_size,
        seed=seed,
        dtype="float16",
        trust_remote_code=True,
        max_num_seqs=max_num_seqs,
        swap_space=8,
    )

    return tokenizer, llm


def generate_with_vLLM_model(
    model,
    input,
    temperature=0.8,
    top_p=0.95,
    top_k=40,
    repetition_penalty=1.1,
    n=1,
    max_tokens=256,
    logprobs=1,
    stop=[],
):
    sampling_params = SamplingParams(
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
        repetition_penalty=repetition_penalty,
        n=n,
        logprobs=logprobs,
        max_tokens=max_tokens,
        stop=stop,
    )

    output = model.generate(input, sampling_params, use_tqdm=False)
    return output

import boto3
from botocore.config import Config

boto_session = boto3.Session()
region_name = boto_session.region_name
llm_model = "anthropic.claude-3-5-haiku-20241022-v1:0"

def init_boto3_client(region: str):
    retry_config = Config(
        region_name=region,
        retries={"max_attempts": 10, "mode": "standard"}
    )
    return boto3.client("bedrock-runtime", region_name=region, config=retry_config)

def converse_with_bedrock(boto3_client, sys_prompt, usr_prompt):    
    temperature = 0.0
    top_p = 0.1
    inference_config = {"temperature": temperature, "topP": top_p}
    
    response = boto3_client.converse(
        modelId=llm_model, 
        messages=usr_prompt, 
        system=sys_prompt,
        inferenceConfig=inference_config
    )

    return response['output']['message']['content'][0]['text']


# test 
# boto3_client = init_boto3_client(region_name)
# test_sys_prompt = [{
#     "text": "You are a cool assistant."
# }]

# test_user_prompt = [{
#     "role": "user",
#     "content": [{"text": "Hi! What's your name?"}]
# }]

# response = converse_with_bedrock(boto3_client, test_sys_prompt, test_user_prompt)
# print(response)