import sqlite3
import os

def migrate_v2():
    db_path = 'instance/society.db'
    
    if not os.path.exists(db_path):
        print("❌ डेटाबेस फाईल सापडली नाही!")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. member_questions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS member_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            question_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(50) DEFAULT 'प्रलंबित',
            FOREIGN KEY (member_id) REFERENCES members (id)
        )
        """)
        print("✅ table created: member_questions")
        
        # 2. admin_replies table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_replies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER NOT NULL,
            reply_text TEXT NOT NULL,
            reply_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            admin_id INTEGER DEFAULT 0,
            FOREIGN KEY (question_id) REFERENCES member_questions (id)
        )
        """)
        print("✅ table created: admin_replies")
        
        conn.commit()
        conn.close()
        print("🎉 मायग्रेशन (V2) यशस्वी झाले!")
        
    except Exception as e:
        print(f"❌ त्रुटी: {e}")

if __name__ == "__main__":
    migrate_v2()
