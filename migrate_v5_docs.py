from app import db, app
from sqlalchemy import text

def migrate():
    with app.app_context():
        try:
            # Check if column exists
            result = db.session.execute(text("PRAGMA table_info(documents)"))
            columns = [row[1] for row in result]
            if 'description' not in columns:
                db.session.execute(text('ALTER TABLE documents ADD COLUMN description TEXT'))
                db.session.commit()
                print("✅ Column 'description' added to 'documents' table")
            else:
                print("ℹ️ Column 'description' already exists")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    migrate()
