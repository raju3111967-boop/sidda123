import sqlite3
import os

db_path = os.path.join('instance', 'society.db')

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if is_active column exists in notices
    cursor.execute("PRAGMA table_info(notices)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'is_active' not in columns:
        print("Adding 'is_active' column to 'notices' table...")
        cursor.execute("ALTER TABLE notices ADD COLUMN is_active BOOLEAN DEFAULT 1")
        print("Column added successfully.")
    else:
        print("'is_active' column already exists in 'notices' table.")
    
    conn.commit()
except Exception as e:
    print(f"Error during migration: {e}")
finally:
    conn.close()
