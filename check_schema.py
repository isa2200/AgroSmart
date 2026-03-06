import sqlite3
import os

db_path = 'db.sqlite3'
if not os.path.exists(db_path):
    print("DB not found")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA table_info(aves_loteaves)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"Columns: {columns}")
        if 'tipo' in columns:
            print("Column 'tipo' EXISTS")
        else:
            print("Column 'tipo' MISSING")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
