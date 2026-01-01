import sqlite3
import os

def migrate_v3():
    db_path = 'instance/society.db'
    if not os.path.exists(db_path):
        print("❌ डेटाबेस फाईल सापडली नाही!")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # १. director_board टेबल तयार करा
        cursor.execute("DROP TABLE IF EXISTS director_board")
        cursor.execute("""
        CREATE TABLE director_board (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            position TEXT NOT NULL,
            mobile TEXT NOT NULL,
            photo TEXT DEFAULT 'default_user.png',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # २. pmc_committee टेबल तयार करा
        cursor.execute("DROP TABLE IF EXISTS pmc_committee")
        cursor.execute("""
        CREATE TABLE pmc_committee (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            building_no TEXT NOT NULL,
            mobile TEXT NOT NULL,
            photo TEXT DEFAULT 'default_user.png',
            role TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # ३. प्री-इन्सर्टेड संचालक डेटा
        directors = [
            ("श्री. शामराव बाबुराव मोरे", "चेअरमन", "9423557744"),
            ("श्री दिपक भगवानदास मोरे", "सचिव", "9922030401"),
            ("श्री. श्रीकांत विठठल शेरे", "खजिनदार", "8237626246"),
            ("श्री. जिवन बाबुराव वाघ", "सदस्य", "9763439323"),
            ("श्री. त्रंबक सोनु सांगळे", "सदस्य", "8237626246"),
            ("श्री. अमोल मधुकर म्हेमाने", "सदस्य", "9890322301"),
            ("श्री. रुपेश शरद पहाडी", "सदस्य", "9921310205"),
            ("श्री. देविदास तुळशीराम सुर्यवंशी", "सदस्य", "9225117519"),
            ("श्री. सुभाष सोपन भवर", "सदस्य", "9011059740"),
            ("सौ. कविता अनिल अंभगे", "सदस्य", "9823776948"),
            ("श्रीमती माधुरी अशोक गांगुर्डे", "सदस्य", "9270619888")
        ]

        for name, pos, mob in directors:
            cursor.execute("INSERT INTO director_board (name, position, mobile) VALUES (?, ?, ?)", (name, pos, mob))

        conn.commit()
        print("✅ मायग्रेशन यशस्वी! नवीन टेबल्स आणि संचालकांचा डेटा भरला गेला.")
    except Exception as e:
        print(f"❌ त्रुटी: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_v3()
