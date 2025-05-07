
engine = create_engine('sqlite:///../Chinook.db')

# table names
inspector = inspect(engine)
table_names = inspector.get_table_names()
print("table_names:\n", table_names)

# simple query
# with Session(engine) as session:
#     result = session.execute(text("SELECT * FROM Artist LIMIT 10"))
#     print("\nrows:")
#     for row in result:
#         print(row)
# INSERT 구문 작성 및 실행
with engine.connect() as conn:
    stmt = insert(artists).values(Name="New Artist Name")
    conn.execute(stmt)
    conn.commit()
