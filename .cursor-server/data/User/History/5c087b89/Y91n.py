#!/usr/bin/env python3
"""
Create Admin User
================
Create a new admin user with known credentials for migration.
"""

import psycopg2
import hashlib

def create_admin_user():
    """Create or update admin user with known password"""
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host="localhost",
            database="odtshbrain",
            user="root",
            password=""
        )
        cursor = conn.cursor()
        
        print("🔗 Connected to PostgreSQL database")
        
        # Check if admin user exists
        cursor.execute("SELECT id, login FROM res_users WHERE login = 'admin'")
        admin_user = cursor.fetchone()
        
        if admin_user:
            user_id, login = admin_user
            print(f"👤 Found existing admin user: ID={user_id}")
            
            # Update password to 'admin'
            cursor.execute("""
                UPDATE res_users 
                SET password = 'admin',
                    active = true,
                    share = false
                WHERE login = 'admin'
            """)
            
            print("✅ Updated admin user password")
            
        else:
            print("👤 Creating new admin user...")
            
            # Create admin user
            cursor.execute("""
                INSERT INTO res_users (login, password, name, email, active, share, company_id)
                VALUES ('admin', 'admin', 'Administrator', 'admin@example.com', true, false, 1)
            """)
            
            print("✅ Created new admin user")
        
        # Make sure admin has superuser privileges
        cursor.execute("""
            UPDATE res_users 
            SET groups_id = NULL
            WHERE login = 'admin'
        """)
        
        conn.commit()
        print("✅ Admin user configured successfully")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return False

if __name__ == "__main__":
    if create_admin_user():
        print("\n🎉 ADMIN USER READY!")
        print("🔐 Login: admin / admin")
    else:
        print("\n❌ Failed to create admin user") 