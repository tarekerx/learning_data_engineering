import json
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

db_host = os.getenv("POSTGRES_HOST", "localhost")
db_name = os.getenv("POSTGRES_DB")
db_user = os.getenv("POSTGRES_USER")
db_password = os.getenv("POSTGRES_PASSWORD")
db_port = os.getenv("POSTGRES_PORT", "5432")

# 1. Read the JSON file
with open("data/users.json", "r", encoding="utf-8") as file:
    users = json.load(file)

# 2. Flatten each user object
flattened_users = []
for user in users:
    flattened_users.append(
        {
            "customer_id": user.get("id"),
            "customer_name": user.get("name"),
            "email": user.get("email"),
            "phone": user.get("phone"),
            "city": user.get("address", {}).get("city"),
            "zipcode": user.get("address", {}).get("zipcode"),
            "company_name": user.get("company", {}).get("name"),
        }
    )

def create_tables():
    connection = psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password,
        port=db_port
    )
    cursor = connection.cursor()
    
    # Fixed SQL syntax with closing parenthesis and more columns
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT PRIMARY KEY,
            name TEXT,
            email TEXT,
            phone TEXT,
            city TEXT,
            zipcode TEXT,
            company_name TEXT
        );
    """)

    connection.commit()
    cursor.close()
    connection.close()
    print("Table created successfully!")


def insert_users_to_postgres():
    connection = psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password,
        port=db_port
    )

    cursor = connection.cursor()

    try:
        inserted_count = 0
        for user in flattened_users:
            cursor.execute(
                """
                INSERT INTO users (id, name, email, phone, city, zipcode, company_name) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING;
                """,
                (
                    user["customer_id"],
                    user["customer_name"],
                    user["email"],
                    user["phone"],
                    user["city"],
                    user["zipcode"],
                    user["company_name"]
                )
            )
            inserted_count += 1
            
        connection.commit()
        print(f"Successfully loaded {inserted_count} records into PostgreSQL!")
        
    except Exception as error:
        connection.rollback()
        print(f"Failed to insert records into database: {error}")
        
    finally:
        cursor.close()
        connection.close()  # Always close the connection!


if __name__ == "__main__":
    create_tables()
    insert_users_to_postgres()