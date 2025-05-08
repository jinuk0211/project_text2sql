installation
-------------
```bash
pip install -r requirements.txt
bash download_demo_corpus.sh
```
implementation
--------------------
```python
python main.py --query '대구광역시 북구 산격3동 11 건물의 에너지 사용량이 뭐야'
--model_path 'llama-3.2-1b'
--gpt_api_key 'your api key'
--huggingface_api_key 'huggingface access token'
--db_path '설정한 db_path'
```
대구광역시 한정 데이터 사용시
---------------------
```python
filepath = '/content/mart_djy_03.txt'
try:
  if filepath.endswith(".txt"):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            print(f"\n파일: {filename}")
            # 대구가 포함된 라인만 저장할 리스트
            daegu_lines = []
            try:
              for line in f:
                  if "대구" in line:
                      new = line.split('|')
                      주소 = f"{new[5]} {new[6]} {new[7]}"
                      PNU = ''.join(new[8:13])
                      면적 = new[29]
                      result = f"주소: {주소}, PNU: {PNU}, 면적: {면적}"
                      daegu_lines.append(result)
            except IndexError:
              print(f"파일 {filename}에서 인덱스 오류 발생, 라인 무시: {line.strip()}")
              pass #pass the error

            #대구 라인 출력
            for line in daegu_lines:
                print(line)

            with open('/content/daegu.txt', 'w', encoding='utf-8') as outfile:
                outfile.write('\n'.join(daegu_lines))

    except UnicodeDecodeError:
        print(f"파일 {filename}을 UTF-8로 디코딩할 수 없습니다. 다른 인코딩을 시도해 보세요.")
    except Exception as e:
        print(f"파일 {filename}을 읽는 중 오류 발생: {e}")

except Exception as e:
    print(f"압축 해제 중 오류 발생: {e}")
```

example retrieve for prompt generation
------------------
```python
memory_storage = []
input_embedding(examples)

for item in memory_storage:
    truncated_item = item.copy()
    truncated_item['input_v'] = str(item['input_v'][:3]) + '...' 
    print(json.dumps(truncated_item, indent=2))
    print()
question = "Let me know the 10 customers who purchased the most"

response = boto3_client.invoke_model(
    modelId=embed_model,
    body=json.dumps({"inputText": question})
)
question_v = json.loads(response['body'].read())['embedding']

print(str(question_v[:5]) + '...')

top_k = 3
top_similar_samples = find_most_similar_samples(question_v, memory_storage, top_k)

samples = ""
for i, (similarity, doc) in enumerate(top_similar_samples, 1):
    samples += f"\n{i}. Score: {similarity:.4f}\n"
    samples += f"Input: {doc['input']}\n"
    samples += f"Query: {doc['query']}\n"

print(samples)    
```

CoT prompt
------------------------
```python
sys_prompt = [{
    "text": f"""You are a {dialect} expert.
Given an input question, first create a syntactically correct SQLite query to run.
Unless the user specifies in the question a specific number of examples to obtain, query for at most {top_k} results using the LIMIT clause as per SQLite. You can order the results to return the most informative data in the database.
Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in double quotes (") to denote them as delimited identifiers.
Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
Pay attention to use date(\'now\') function to get the current date, if the question involves "today" 
<schema>
{table_info}
</schema>
<examples>{example}</examples>
""" 
print(sys_prompt[0]["text"])

question = "Find the average invoice total for each country, but only for countries with more than 5 customers, ordered by the average total descending."
user_prompt = get_user_prompt(question)
print(user_prompt[0]["content"][0]["text"])

response = converse_with_bedrock(boto3_client, sys_prompt, user_prompt)
print(response)
    

thought_process = response.split('<thought_process>')[1].split('</thought_process>')[0].strip()
sql = response.split('<sql>')[1].split('</sql>')[0].strip()

print("Thought:\n", thought_process)
print("\nSQL:\n", sql)


sql_query = text(sql)
with Session(engine) as session:
    result = session.execute(sql_query)
    for row in result:
        print(row)
    
```
