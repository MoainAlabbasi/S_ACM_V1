import os
import psycopg2
from dotenv import load_dotenv

# تحميل المتغيرات
load_dotenv()

# الاتصال بقاعدة البيانات
try:
    print("Connecting to database...")
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    conn.autocommit = True
    cur = conn.cursor()

    # مسح جميع الجداول (Format)
    print("Wiping all tables (DROP SCHEMA)...")
    cur.execute("DROP SCHEMA public CASCADE;")
    cur.execute("CREATE SCHEMA public;")
    
    print("✅ Database cleaned successfully!")
    print("Now you can run 'migrate'.")

    cur.close()
    conn.close()

except Exception as e:
    print(f"❌ Error: {e}")