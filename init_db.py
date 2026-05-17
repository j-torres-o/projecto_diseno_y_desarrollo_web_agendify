import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

try:
    print("Conectando a MySQL para inicializar la base de datos...")
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', '')
    )
    cursor = conn.cursor()
    
    with open('schema.sql', 'r', encoding='utf-8') as f:
        sql_commands = f.read().split(';')
        
    for command in sql_commands:
        if command.strip():
            cursor.execute(command)
            
    conn.commit()
    print("✅ Base de datos inicializada correctamente.")

except Exception as e:
    print(f"❌ Error al inicializar: {e}")
finally:
    if 'cursor' in locals() and cursor:
        cursor.close()
    if 'conn' in locals() and conn.is_connected():
        conn.close()
