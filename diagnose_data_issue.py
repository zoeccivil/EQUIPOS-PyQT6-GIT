#!/usr/bin/env python3
"""
Diagnostic script to identify why transactions and gastos aren't showing in the UI.
"""

import sqlite3
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from logic import DatabaseManager
from app.app_settings import get_settings
from app.repo.repository_factory import RepositoryFactory

def check_sqlite_data(db_path):
    """Check what data exists in SQLite database."""
    print(f"\n=== Checking SQLite Database: {db_path} ===\n")
    
    try:
        db = DatabaseManager(db_path)
        
        # Check transactions
        transacciones = db.fetchall("SELECT COUNT(*) as count, tipo FROM transacciones GROUP BY tipo")
        print("Transactions in DB:")
        for t in transacciones:
            print(f"  - {t['tipo']}: {t['count']} records")
        
        # Check gastos specifically
        gastos = db.fetchall("""
            SELECT COUNT(*) as count, proyecto_id 
            FROM transacciones 
            WHERE tipo = 'Gasto' 
            GROUP BY proyecto_id
        """)
        print("\nGastos by project:")
        for g in gastos:
            print(f"  - Project {g['proyecto_id']}: {g['count']} gastos")
        
        # Check sample gastos for project 8
        sample_gastos = db.fetchall("""
            SELECT t.id, t.fecha, t.descripcion, t.monto, t.proyecto_id
            FROM transacciones t
            WHERE t.proyecto_id = 8 AND t.tipo = 'Gasto'
            LIMIT 5
        """)
        print("\nSample gastos for project 8:")
        for g in sample_gastos:
            print(f"  - {g['fecha']}: {g['descripcion']} - RD$ {g['monto']}")
            
        # Check ingresos (transactions)  
        ingresos = db.fetchall("""
            SELECT COUNT(*) as count, proyecto_id 
            FROM transacciones 
            WHERE tipo = 'Ingreso' 
            GROUP BY proyecto_id
        """)
        print("\nIngresos by project:")
        for i in ingresos:
            print(f"  - Project {i['proyecto_id']}: {i['count']} ingresos")
            
        # Check sample ingresos for project 8
        sample_ingresos = db.fetchall("""
            SELECT t.id, t.fecha, t.descripcion, t.monto, t.proyecto_id
            FROM transacciones t
            WHERE t.proyecto_id = 8 AND t.tipo = 'Ingreso'
            LIMIT 5
        """)
        print("\nSample ingresos for project 8:")
        for i in sample_ingresos:
            print(f"  - {i['fecha']}: {i['descripcion']} - RD$ {i['monto']}")
            
    except Exception as e:
        print(f"ERROR checking SQLite: {e}")
        import traceback
        traceback.print_exc()

def check_firestore_data():
    """Check what data exists in Firestore."""
    print("\n=== Checking Firestore Data ===\n")
    
    try:
        settings = get_settings()
        
        if settings.data_source != "firestore":
            print(f"Data source is set to: {settings.data_source}")
            print("Switch to Firestore to test Firestore data.")
            return
        
        print(f"Firestore Project: {settings.firestore.get('project_id')}")
        print(f"Firestore Email: {settings.firestore.get('email')}")
        
        # Create Firestore repository
        repo = RepositoryFactory.create_from_settings(settings)
        
        # Check transacciones collection
        transacciones = repo.obtener_tabla_completa("transacciones")
        print(f"\nTotal transactions in Firestore: {len(transacciones)}")
        
        # Count by type
        tipos = {}
        proyectos = {}
        for t in transacciones:
            tipo = t.get('tipo', 'unknown')
            tipos[tipo] = tipos.get(tipo, 0) + 1
            
            proyecto_id = t.get('proyecto_id')
            if proyecto_id:
                key = f"{tipo}_p{proyecto_id}"
                proyectos[key] = proyectos.get(key, 0) + 1
        
        print("\nBy type:")
        for tipo, count in tipos.items():
            print(f"  - {tipo}: {count}")
            
        print("\nBy type and project:")
        for key, count in sorted(proyectos.items()):
            print(f"  - {key}: {count}")
        
        # Sample gastos for project 8
        gastos_p8 = [t for t in transacciones if t.get('tipo') == 'Gasto' and t.get('proyecto_id') == 8]
        print(f"\nSample Gastos for Project 8 in Firestore (showing 5/{len(gastos_p8)}):")
        for g in gastos_p8[:5]:
            print(f"  - {g.get('fecha')}: {g.get('descripcion')} - RD$ {g.get('monto')}")
            
        # Sample ingresos for project 8
        ingresos_p8 = [t for t in transacciones if t.get('tipo') == 'Ingreso' and t.get('proyecto_id') == 8]
        print(f"\nSample Ingresos for Project 8 in Firestore (showing 5/{len(ingresos_p8)}):")
        for i in ingresos_p8[:5]:
            print(f"  - {i.get('fecha')}: {i.get('descripcion')} - RD$ {i.get('monto')}")
        
    except Exception as e:
        print(f"ERROR checking Firestore: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 70)
    print("DIAGNOSTIC TOOL: Transaction & Gastos Data Check")
    print("=" * 70)
    
    # Check the main SQLite database
    check_sqlite_data("progain_database.db")
    
    # Check Firestore
    check_firestore_data()
    
    print("\n" + "=" * 70)
    print("Diagnosis complete!")
    print("=" * 70)
