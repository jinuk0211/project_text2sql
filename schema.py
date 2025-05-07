def get_schema_info(db_path):
    engine = create_engine(f'sqlite:///{db_path}')

    inspector = inspect(engine)
    schema_info = {}

    tables = inspector.get_table_names()
    for table_name in tables:
        columns = inspector.get_columns(table_name)

        table_info = f"Table: {table_name}\n"
        table_info += "\n".join(f"  - {col['name']} ({col['type']})" for col in columns)
        schema_info[table_name] = table_info

    return schema_info

schema = get_schema_info("../Chinook.db")
print(schema['Employee'])


     

dialect = "sqlite"
top_k = 10
table_info = schema['Customer']

sys_prompt = [{
    "text": f"""You are a {dialect} expert.
Given an input question, first create a syntactically correct SQLite query to run.
Unless the user specifies in the question a specific number of examples to obtain, query for at most {top_k} results using the LIMIT clause as per SQLite. You can order the results to return the most informative data in the database.
Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in double quotes (") to denote them as delimited identifiers.
Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
Pay attention to use date(\'now\') function to get the current date, if the question involves "today" 
    
Only use the following tables:
{table_info}
""" 
}]


def get_user_prompt(question):
    return [{
        "role": "user",
        "content": [{"text": f"Question:\n{question}]\n\nSkip the preamble and provide only the SQL."
        }]
    }]


     