import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('home_energy.db')
cursor = conn.cursor()

# Create Users Table (For authentication, only allows POST)
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);
''')

#Home Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS home (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    size INTEGER NOT NULL,
    occupants INTEGER NOT NULL,
    location TEXT NOT NULL,
    home_type TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
''')

# Appliances Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS appliances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    home_id INTEGER NOT NULL,
    appliance_name TEXT NOT NULL,
    power_usage INTEGER NOT NULL,
    FOREIGN KEY (home_id) REFERENCES home(id) ON DELETE CASCADE
);
''')

#Behavior Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS behavior (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    home_id INTEGER NOT NULL,
    peak_usage_hours TEXT NOT NULL,
    daily_usage_hours INTEGER NOT NULL,
    FOREIGN KEY (home_id) REFERENCES home(id) ON DELETE CASCADE
);
''')

# Commit
conn.commit()
conn.close()

print("Database and tables created successfully!")
