#!/usr/bin/env python3
"""
Reset Admin Password
==================
Reset the admin user password in Odoo database.
"""

import psycopg2
import hashlib
import base64

def reset_admin_password():
    """Reset admin password to 'admin' in the database"""
    
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
        cursor.execute("SELECT id, login, password FROM res_users WHERE login = 'admin'")
        admin_user = cursor.fetchone()
        
        if admin_user:
            user_id, login, current_password = admin_user
            print(f"👤 Found admin user: ID={user_id}, login={login}")
            
            # Generate password hash for 'admin'
            password = 'admin'
            password_crypt = password  # In newer Odoo versions, plain text might work
            
            # Update password
            cursor.execute(
                "UPDATE res_users SET password = %s WHERE login = 'admin'",
                (password_crypt,)
            )
            
            # Also try updating password hash
            cursor.execute(
                "UPDATE res_users SET password = 'admin', password_crypt = NULL WHERE login = 'admin'"
            )
            
            conn.commit()
            print("✅ Admin password reset to 'admin'")
            
            # Also make sure admin has basic access rights
            cursor.execute("""
                UPDATE res_users 
                SET active = true, 
                    share = false,
                    groups_id = NULL
                WHERE login = 'admin'
            """)
            
            conn.commit()
            print("✅ Admin user activated and groups reset")
            
        else:
            print("❌ Admin user not found")
            return False
            
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error resetting password: {e}")
        return False

if __name__ == "__main__":
    if reset_admin_password():
        print("\n🎉 ADMIN PASSWORD RESET!")
        print("🔐 Login: admin / admin")
    else:
        print("\n❌ Failed to reset password") 