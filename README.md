CoT prompt
------------------------
```python
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