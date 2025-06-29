import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

print(os.getenv("DB_HOST"))

try:
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS")
    )
    cur = conn.cursor()
    cur.execute("SELECT 1;")
    print("✅ Database connected successfully.")
    cur.close()
    conn.close()
except Exception as e:
    print("❌ Database connection failed:", e)
