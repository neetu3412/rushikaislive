import sqlite3
from werkzeug.security import generate_password_hash

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Create Users Table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    address TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL)''')

    # Create Dashboard Content Table
    c.execute('''CREATE TABLE IF NOT EXISTS dashboard_content (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    youtube_embed_link TEXT)''')
                    
    # Insert Default Admin (Password: admin123)
    admin_pass = generate_password_hash('admin123')
    c.execute("SELECT * FROM users WHERE role='admin'")
    if not c.fetchone():
        c.execute('''INSERT INTO users (name, address, phone, username, password_hash, role) 
                     VALUES (?, ?, ?, ?, ?, ?)''', 
                  ('Master Admin', 'HQ Server', '0000000000', 'admin', admin_pass, 'admin'))
        
    # Insert Default YT Link
    c.execute("SELECT * FROM dashboard_content")
    if not c.fetchone():
        c.execute("INSERT INTO dashboard_content (youtube_embed_link) VALUES (?)",
                  ("https://youtube.com/@rushikaislive?si=WdhhWS2lvj1UIoXP",))

    conn.commit()
    conn.close()
    print("Database ready hai! Admin username: 'admin', password: 'admin123'")

if __name__ == '__main__':
    init_db()