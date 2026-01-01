import sqlite3
import os

def migrate_db():
    db_path = 'G:/sidda/instance/society.db'
    if not os.path.exists(db_path):
        db_path = 'G:/sidda/society.db' # जर instance फोल्डरमध्ये नसेल तर

    print(f"🔍 डेटाबेस येथे शोधत आहे: {db_path}")
    
    if not os.path.exists(db_path):
        print("❌ डेटाबेस फाईल सापडली नाही!")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # जोडायचे असलेले नवीन कॉलम्स
        new_columns = [
            ('ai_category', 'VARCHAR(100)'),
            ('ai_priority', 'VARCHAR(50)'),
            ('ai_sentiment', 'VARCHAR(50)'),
            ('ai_suggested_reply', 'TEXT')
        ]
        
        for col_name, col_type in new_columns:
            try:
                cursor.execute(f"ALTER TABLE complaints ADD COLUMN {col_name} {col_type}")
                print(f"✅ कॉलम जोडला: {col_name}")
            except sqlite3.OperationalError:
                print(f"ℹ️ कॉलम आधीच अस्तित्वात आहे: {col_name}")
        
        conn.commit()
        conn.close()
        print("🎉 डेटाबेस मायग्रेशन पूर्ण झाले!")
        
    except Exception as e:
        print(f"❌ त्रुटी: {e}")

if __name__ == "__main__":
 society_db_path = 'G:/sidda/society.db'
 migrate_db()
