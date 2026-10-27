import os
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from dotenv import load_dotenv
import psycopg2

# Load environment variables
load_dotenv()

db_host = os.getenv("POSTGRES_HOST", "localhost")
db_name = os.getenv("POSTGRES_DB")
db_user = os.getenv("POSTGRES_USER")
db_password = os.getenv("POSTGRES_PASSWORD")
db_port = os.getenv("POSTGRES_PORT", "5432")


def connect_to_database():
    """Establishes a connection to the PostgreSQL database."""
    connection = psycopg2.connect(
        host=db_host, database=db_name, user=db_user, password=db_password, port=db_port
    )
    return connection


def create_tables(conn):
    """Creates the required metadata and target data tables if they don't exist."""
    with conn.cursor() as curr:
        # 1. State Table for Watermarking
        curr.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_state (
                source_name VARCHAR(100) PRIMARY KEY,
                watermark_value TIMESTAMP NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # 2. Target Table for Coin Data
        curr.execute("""
            CREATE TABLE IF NOT EXISTS coingecko_coins (
                coin_id VARCHAR(100) PRIMARY KEY,
                symbol VARCHAR(50),
                current_price FLOAT,
                last_updated TIMESTAMP,
                loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()


def fetch_last_date(conn, source_name):
    """Fetches the last watermark timestamp, or sets a default bootstrap date if missing."""
    with conn.cursor() as curr:
        curr.execute(
            "SELECT watermark_value FROM pipeline_state WHERE source_name = %s;",
            (source_name,),
        )
        row = curr.fetchone()

        if row:
            return row[0]
        else:
            default_date = "2024-01-01 00:00:00"
            curr.execute(
                "INSERT INTO pipeline_state (source_name, watermark_value) VALUES (%s, %s);",
                (source_name, default_date),
            )
            conn.commit()
            return default_date


def fetch_data_from_api(api_url, watermark):
    """Fetches new records from the CoinGecko API."""
    print(f"Fetching data from API newer than watermark: {watermark}")

    req = Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data
    except (HTTPError, URLError) as e:
        print(f"Error fetching data from API: {e}")
        return []


def load_data_and_update_state(conn, source_name, records):
    """
    Upserts coin records into the target table, tracks the maximum timestamp 
    of the batch, and updates the pipeline_state watermark at the very end.
    """
    if not records:
        print("No new records to load.")
        return

    with conn.cursor() as curr:
        max_timestamp = None

        for record in records:
            coin_id = record.get("id")
            symbol = record.get("symbol")
            price = record.get("current_price")
            event_time = record.get("last_updated") # ISO timestamp from CoinGecko

            if not event_time or not coin_id:
                continue

            # Track the maximum timestamp seen in this batch
            if max_timestamp is None or event_time > max_timestamp:
                max_timestamp = event_time

            # Idempotent Upsert for each coin record
            curr.execute("""
                INSERT INTO coingecko_coins (coin_id, symbol, current_price, last_updated)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (coin_id) 
                DO UPDATE SET symbol = EXCLUDED.symbol,
                              current_price = EXCLUDED.current_price,
                              last_updated = EXCLUDED.last_updated,
                              loaded_at = CURRENT_TIMESTAMP;
            """, (coin_id, symbol, price, event_time))

        # Update the watermark in pipeline_state ONLY after successful data load
        if max_timestamp:
            curr.execute("""
                UPDATE pipeline_state 
                SET watermark_value = %s, updated_at = CURRENT_TIMESTAMP
                WHERE source_name = %s;
            """, (max_timestamp, source_name))

        conn.commit()
        print(f"Successfully loaded batch and updated watermark to: {max_timestamp}")


if __name__ == "__main__":
    conn = connect_to_database()
    source = "coingecko_market"
    
    try:
        # 1. Initialize tables
        create_tables(conn)
        
        # 2. Get current watermark
        last_watermark = fetch_last_date(conn, source)
        
        # 3. Fetch data from API
        api_url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1&sparkline=false"
        api_data = fetch_data_from_api(api_url, last_watermark)
        
        # 4. Load data and advance watermark
        load_data_and_update_state(conn, source, api_data)
        
    finally:
        conn.close()
        print("Database connection closed.")