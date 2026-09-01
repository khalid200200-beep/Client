import pymysql
import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host='84.247.141.162',
    user='root',
    password='e250eb38de998d02',
    database='shipping_db',
    charset='utf8mb4'
)
cursor = conn.cursor()
cursor.execute("SELECT setting_key, setting_value FROM system_settings WHERE setting_key LIKE 'whatsapp_%'")
rows = dict(cursor.fetchall())
print("WhatsApp DB Settings:", rows)
conn.close()
