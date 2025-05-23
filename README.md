installation
-------------
```bash
RAG - 53%
text2sql with poor schema - 12%
text2sql with proper schema - 72%
text2sql with query decomposition
```
## Text-to-SQL 방법별 성능 비교

| 방법                          | 설명                                                      | 정확도 |
|-----------------------------|-----------------------------------------------------------|--------|
| RAG                         | 검색 문서 기반 SQL 생성 (Context Retrieval 후 Prompt 작성)  | 53%    |
| Text2SQL (Poor Schema)      | 스키마 정보 부족 또는 부정확하게 제공된 경우               | 12%    |
| Text2SQL (Proper Schema)    | 스키마 구조 명확히 제공 (JSON 등으로)                     | 72%    |
| Query Decomposition         | 복잡한 질문을 서브질문으로 나누고 병합                    | (값 미제공) |

Text-to-SQL 성능을 높이기 위해 해야 할 일 

1. 스키마와 비즈니스 문맥을 명확히 제공하라

LLM은 테이블 구조, 열 이름, 데이터 의미를 알아야 정확한 SQL을 생성함

예시: "user_id"가 고객 ID인지 직원 ID인지 명확히 알려줘야 함


2. 사용자 의도를 명확히 파악하고 질문을 재구성하라

모호한 질문 → 명확하게 바꿔주는 후속 질문 생성

예시: “가장 많이 팔린 상품?” → “판매량 기준인가요? 수익 기준인가요?”


3. SQL 방언(다른 DB마다 문법 차이)에 맞춰 조정하라

PostgreSQL, MySQL, BigQuery 등마다 SQL 문법 다르므로 맞춤 대응 필요


4. 강력한 모델과 프롬프트 조합을 사용하라

Gemini 같은 고성능 LLM 사용 + 예제 기반 학습 (in-context learning)


5. 지속적인 자동화 평가 및 개선

LLM-as-a-judge로 자동 평가 → 새로운 프롬프트나 모델 성능 빠르게 비교 가


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
