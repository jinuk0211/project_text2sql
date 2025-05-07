import json

uri = "sqlite:///../Chinook.db"

def get_table_info():
    with open('../db_metadata/chinook_schema.json', 'r') as file:
        schema_data = json.load(file)

    tables_dict = {}
    for table_info in schema_data:
        for table_name, table_data in table_info.items():
            tables_dict[table_name] = table_data['table_desc']

    return tables_dict

# Test
table_info = get_table_info()
for table_name, table_desc in table_info.items():
    print(f"Table: {table_name}")
    print(f"Description: {table_desc}")
    print()
    
def get_table_columns(tables=None):
    with open('../db_metadata/chinook_schema.json', 'r') as file:
        schema_data = json.load(file)

    table_columns = {}

    for table_info in schema_data:
        for table_name, table_data in table_info.items():
            if tables is None or table_name in tables:
                column_info = {}
                for col in table_data['cols']:
                    column_info[col['col']] = col['col_desc']
                table_columns[table_name] = column_info

    return table_columns

# Test
tables = ["Album", "Customer"]
get_table_columns(tables)