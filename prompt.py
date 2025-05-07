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

#cot 버젼
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


example = """
<example>
<query>
Find the top 3 customers who have spent the most money in 2023, showing their names and total spending.
</query> 
<thought_process> 
1. We need to join the Customer and Invoice tables. 
2. We'll sum up the Total from Invoice for each customer. 
3. We'll filter for invoices from the year 2023. 
4. We'll order by the total spending in descending order. 
5. We'll limit the results to the top 3 customers. 
</thought_process> 
<sql> 
SELECT c.FirstName, c.LastName, SUM(i.Total) AS TotalSpending FROM Customer c JOIN Invoice i ON c.CustomerId = i.CustomerId WHERE YEAR(i.InvoiceDate) = 2023 GROUP BY c.CustomerId, c.FirstName, c.LastName ORDER BY TotalSpending DESC LIMIT 3; 
</sql> 
</example> 

<example> 
<query>
List all customers from the USA who have not made any purchases in the last 6 months.
</query> 
<thought_process> 
1. We need to use both the Customer and Invoice tables. 
2. We'll filter for customers from the USA. 
3. We'll use a LEFT JOIN to include customers with no invoices. 
4. We'll check for the absence of recent invoices (within the last 6 months). 
5. We'll return the customer's full name and email. 
</thought_process> 
<sql> 
SELECT c.FirstName, c.LastName, c.Email FROM Customer c LEFT JOIN Invoice i ON c.CustomerId = i.CustomerId AND i.InvoiceDate >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH) WHERE c.Country = 'USA' AND i.InvoiceId IS NULL; 
</sql> 
</example>
"""


examples = [
    {
        "input": "List all artists.", 
        "query": "SELECT * FROM Artist;"},
    {
        "input": "Find all albums for the artist 'AC/DC'.",
        "query": "SELECT * FROM Album WHERE ArtistId = (SELECT ArtistId FROM Artist WHERE Name = 'AC/DC');",
    },
    {
        "input": "List all tracks in the 'Rock' genre.",
        "query": "SELECT * FROM Track WHERE GenreId = (SELECT GenreId FROM Genre WHERE Name = 'Rock');",
    },
    {
        "input": "Find the total duration of all tracks.",
        "query": "SELECT SUM(Milliseconds) FROM Track;",
    },
    {
        "input": "List all customers from Canada.",
        "query": "SELECT * FROM Customer WHERE Country = 'Canada';",
    },
    {
        "input": "How many tracks are there in the album with ID 5?",
        "query": "SELECT COUNT(*) FROM Track WHERE AlbumId = 5;",
    },
    {
        "input": "Find the total number of invoices.",
        "query": "SELECT COUNT(*) FROM Invoice;",
    },
    {
        "input": "List all tracks that are longer than 5 minutes.",
        "query": "SELECT * FROM Track WHERE Milliseconds > 300000;",
    },
    {
        "input": "Who are the top 5 customers by total purchase?",
        "query": "SELECT CustomerId, SUM(Total) AS TotalPurchase FROM Invoice GROUP BY CustomerId ORDER BY TotalPurchase DESC LIMIT 5;",
    },
    {
        "input": "How many employees are there",
        "query": 'SELECT COUNT(*) FROM "Employee"',
    },
]


    