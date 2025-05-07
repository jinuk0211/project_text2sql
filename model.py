
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


boto3_client = init_boto3_client(region_name)


     

test_sys_prompt = [{
    "text": "You are a cool assistant."
}]

test_user_prompt = [{
    "role": "user",
    "content": [{"text": "Hi! What's your name?"}]
}]

response = converse_with_bedrock(boto3_client, test_sys_prompt, test_user_prompt)
print(response)