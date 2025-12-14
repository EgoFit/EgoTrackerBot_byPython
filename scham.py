import mysql.connector
from dotenv import load_dotenv
import os


# بارگذاری متغیرهای محیطی از فایل .env
load_dotenv()
# db_url = os.getenv('database_url')
DB_HOST=os.getenv('DB_HOST')
DB_USER=os.getenv('DB_USER')
DB_PASSWORD=os.getenv('DB_PASSWORD')
DB_NAME=os.getenv('DB_NAME')
DB_PORT=os.getenv('DB_PORT')



def connection():
# ایجاد اتصال
    try:
        conn = mysql.connector.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        # print("✅ اتصال موفق بود!")

        # نمونه استفاده: اجرای یک کوئری ساده
        cursor = conn.cursor()
        return conn , cursor
    

    except mysql.connector.Error as err:
        print("❌ خطا در اتصال:", err)

    finally:
        if 'connection' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("🔒 اتصال بسته شد.")

