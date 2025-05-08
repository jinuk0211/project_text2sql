from database import import_buildings_from_file
from schema import get_schema_info
from prompt import get_user_prompt
from model import load_vLLM_model, generate_with_vLLM_model
from huggingface_hub import login

import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        description="Process inputs for model inference with OpenAI and Hugging Face APIs"
    )
    # 모델 이름 (예: "gpt-3.5-turbo", "llama-3.2")
    parser.add_argument(
        "--model_name",
        type=str,
        required=True,
        default="meta-llama/Llama-3.2-1B-Instruct"
        help="Name of the model to use (e.g., 'gpt-3.5-turbo')"
    )
    # 사용자 query
    parser.add_argument(
        "--query",
        type=str,
        required=True,
        help="The input query string to send to the model"
    )
    # OpenAI GPT API 키
    parser.add_argument(
        "--gpt_api_key",
        type=str,
        required=True,
        help="Your OpenAI API key (e.g., 'sk-...')"
    )
    # Hugging Face API 키
    parser.add_argument(
        "--huggingface_api_key",
        type=str,
        help="Your Hugging Face API key"
    )

    parser.add_argument(
        "--huggingface",
        type=bool,
        default = True
        help="허깅페이스 모델일 경우"
    )

    parser.add_argument(
        "--db_path",
        type=str,
        required=True,
        help="Path to the SQLite database file (e.g., 'energy_map.db')"
    )


    return parser.parse_args()

def main(args):
    if args.huggingface:
        login(args.huggingface_api_key)
    tokenizer, llm = load_vLLM_model(args.model_name,42)
    import_buildings_from_file(db_path="/content/building.db",txt_path="/content/daegu.txt",limit=10)
    schema = get_schema_info(args.db_path)
    user_prompt = get_user_prompt(args.query)
    
    top_k = 3
    table_info = schema['building']
    sys_prompt =  [{"text": f"""You are a sqlite expert.
    Given an input question, first create a syntactically correct SQLite query to run.
    Unless the user specifies in the question a specific number of examples to obtain, query for at most {top_k} results using the LIMIT clause as per SQLite. You can order the results to return the most informative data in the database.
    Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in double quotes (") to denote them as delimited identifiers.
    Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
    Pay attention to use date(\'now\') function to get the current date, if the question involves "today" 
        
    Only use the following tables:
    {table_info}""" }]

    input = sys_prompt + user_prompt
    response = generate_with_vLLM_model(llm,input)

    with Session(engine) as session:
    result = session.execute(sql_query)
    for row in result:
        print(f'면적:{row}')

if __name__ =='__main__':
    args = parse_args()
    main(args)

    
