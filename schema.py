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


     





     