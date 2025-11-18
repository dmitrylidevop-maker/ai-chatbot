#!/usr/bin/env python3
"""
Database initialization script
Creates all tables in the database
"""

from app.database import init_db, engine
from app.models.user import User, UserDetails, PersonalFact, ChatHistory
from sqlalchemy import inspect

def show_tables():
    """Show all created tables"""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("\nCreated tables:")
    for table in tables:
        print(f"  - {table}")

if __name__ == "__main__":
    print("Initializing database...")
    print(f"Database URL: {engine.url}")
    
    try:
        init_db()
        print("✓ Database tables created successfully!")
        show_tables()
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        raise
