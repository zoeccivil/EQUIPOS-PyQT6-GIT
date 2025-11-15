#!/usr/bin/env python3
"""
Diagnostic script to check why transactions aren't showing up after sync.
"""
import sqlite3

# Check original database
print("=" * 60)
print("ORIGINAL DATABASE (progain_database.db)")
print("=" * 60)

conn_orig = sqlite3.connect('progain_database.db')
cursor = conn_orig.cursor()

# Count all transactions for proyecto_id = 8
cursor.execute("SELECT COUNT(*) FROM transacciones WHERE proyecto_id = 8")
total = cursor.fetchone()[0]
print(f"Total transactions for proyecto_id=8: {total}")

# Count by type
cursor.execute("SELECT tipo, COUNT(*) FROM transacciones WHERE proyecto_id = 8 GROUP BY tipo")
for tipo, count in cursor.fetchall():
    print(f"  {tipo}: {count}")

# Sample some IDs
cursor.execute("SELECT id, tipo, monto, fecha FROM transacciones WHERE proyecto_id = 8 LIMIT 10")
print("\nSample transaction IDs:")
for row in cursor.fetchall():
    print(f"  ID: {row[0]}, Tipo: {row[1]}, Monto: {row[2]}, Fecha: {row[3]}")

# Check data types of proyecto_id column
cursor.execute("SELECT DISTINCT typeof(proyecto_id), COUNT(*) FROM transacciones GROUP BY typeof(proyecto_id)")
print("\nData types of proyecto_id column in original DB:")
for dtype, count in cursor.fetchall():
    print(f"  {dtype}: {count} records")

# Check if there are any NULL proyecto_id
cursor.execute("SELECT COUNT(*) FROM transacciones WHERE proyecto_id IS NULL")
null_count = cursor.fetchone()[0]
print(f"  NULL proyecto_id: {null_count} records")

conn_orig.close()

print("\n" + "=" * 60)
print("Recommendations:")
print("=" * 60)
print("1. All 519 transactions should be migrated to Firestore")
print("2. All 519 transactions should be synced back to SQLite")  
print("3. The sync process should preserve proyecto_id as INTEGER")
print("4. Check if Firestore migration completed successfully")
