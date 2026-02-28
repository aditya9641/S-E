import sqlite3

# 1. Connect to the database (this will create a file called pharmacy_inventory.db)
conn = sqlite3.connect('pharmacy_inventory.db')
cursor = conn.cursor()

# 2. Build the Table (The Ledger)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY,
        medicine_name TEXT,
        generic_name TEXT,
        category TEXT,
        stock_box_count INTEGER,
        wholesale_price_per_box REAL,
        expiry_date TEXT
    )
''')

# 3. Clear old data (in case you run this twice)
cursor.execute('DELETE FROM inventory')

# 4. Insert Real-World Wholesale Data 
pharmacy_data = [
    (1, 'Paracetamol 500mg', 'Acetaminophen', 'Analgesic', 500, 12.50, '2027-05-01'),
    (2, 'Amoxicillin 250mg', 'Amoxicillin', 'Antibiotic', 200, 45.00, '2026-11-15'),
    (3, 'Omeprazole 20mg', 'Omeprazole', 'Antacid', 350, 22.00, '2028-01-10'),
    (4, 'Cetirizine 10mg', 'Cetirizine', 'Antihistamine', 400, 15.00, '2027-08-20'),
    (5, 'Azithromycin 500mg', 'Azithromycin', 'Antibiotic', 150, 65.50, '2026-09-30')
]

cursor.executemany('''
    INSERT INTO inventory (id, medicine_name, generic_name, category, stock_box_count, wholesale_price_per_box, expiry_date)
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', pharmacy_data)

# 5. Save and Close
conn.commit()
conn.close()

print("✅ SUCCESS: Wholesale database 'pharmacy_inventory.db' is locked and loaded.")