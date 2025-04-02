import sqlite3
import random

conn = sqlite3.connect('home_energy.db')
cursor = conn.cursor()

# Sample data pools
first_names = ["Brian", "Faith", "Kevin", "Mercy", "Collins", "Janet", "Dennis", "Lucy", "George", "Irene",
               "Victor", "Sharon", "Samuel", "Diana", "James", "Elizabeth", "John", "Grace", "David", "Cynthia",
               "Stephen", "Joy", "Daniel", "Beatrice", "Eric", "Martha", "Nicholas", "Hilda", "Mark", "Ruth"]

last_names = ["Mwangi", "Kipchoge", "Omondi", "Wambui", "Otieno", "Muthoni", "Njoroge", "Achieng", "Kariuki", "Mugambi",
              "Kimani", "Wangari", "Kamau", "Mutua", "Ngugi", "Maina", "Odhiambo", "Nyaga", "Macharia", "Koech",
              "Okello", "Cheruiyot", "Kagwe", "Owuor", "Wekesa", "Wamalwa", "Gichuhi", "Makau", "Njenga", "Ndungu"]

locations = ["Nairobi", "Mombasa", "Kisumu", "Eldoret", "Nakuru", "Thika", "Nyeri", "Machakos", "Meru", "Kakamega"]
home_types = ["Apartment", "Bungalow", "Mansion", "Townhouse", "Bedsitter"]
appliances = ["Refrigerator", "TV", "Microwave", "Electric Cooker", "Washing Machine", "Iron Box", "Water Heater",
              "Laptop", "Gaming Console", "Air Conditioner", "Ceiling Fan", "Blender", "Toaster", "Desktop PC",
              "Router", "Kettle"]

# Peak usage patterns
peak_hours = ["6AM - 9AM", "12PM - 3PM", "6PM - 10PM"]
daily_usage = [3, 5, 7, 10, 12]

# Insert exactly 30 users
for i in range(30):
    full_name = f"{random.choice(first_names)} {random.choice(last_names)}"
    email = full_name.replace(" ", "").lower() + "@gmail.com"
    password = "password123"

    # Insert user
    cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
    user_id = cursor.lastrowid

    # Assign a home
    home_size = random.randint(50, 500)  # Square meters
    occupants = random.randint(1, 8)
    location = random.choice(locations)
    home_type = random.choice(home_types)

    cursor.execute("INSERT INTO home (user_id, size, occupants, location, home_type) VALUES (?, ?, ?, ?, ?)", 
                   (user_id, home_size, occupants, location, home_type))
    home_id = cursor.lastrowid

    # Assign 3-7 appliances to each home
    user_appliances = random.sample(appliances, random.randint(3, 7))
    for appliance in user_appliances:
        power_usage = random.randint(50, 300)  # Wattage range
        cursor.execute("INSERT INTO appliances (home_id, appliance_name, power_usage) VALUES (?, ?, ?)", 
                       (home_id, appliance, power_usage))

    # Assign behavior
    peak_usage = random.choice(peak_hours)
    daily_hours = random.choice(daily_usage)

    cursor.execute("INSERT INTO behavior (home_id, peak_usage_hours, daily_usage_hours) VALUES (?, ?, ?)", 
                   (home_id, peak_usage, daily_hours))

conn.commit()
conn.close()

print("✅ 30 Users with Home Data, Appliances, and Behavior inserted successfully!")
