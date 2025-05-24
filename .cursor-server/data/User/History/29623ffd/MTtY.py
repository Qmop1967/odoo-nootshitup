#!/usr/bin/env python3
"""
Fix Admin Permissions
====================
Grant admin user all necessary permissions for migration.
"""

import odoorpc

def fix_admin_permissions():
    """Grant admin user all necessary groups for migration"""
    
    try:
        # Connect to Odoo
        odoo = odoorpc.ODOO('localhost', port=8069)
        odoo.login('odtshbrain', 'admin', 'admin')
        
        print("🔐 Connected to Odoo as admin")
        
        # Get admin user
        admin_user = odoo.env.user
        print(f"👤 Current user: {admin_user.name} (ID: {admin_user.id})")
        
        # Get all available groups
        groups_to_add = [
            'account.group_account_manager',  # Invoicing/Administrator
            'account.group_account_invoice',  # Invoicing/Invoicing  
            'purchase.group_purchase_user',   # Purchase/User
            'sales_team.group_sale_salesman', # Sales/User
            'base.group_user',                # Internal User
            'base.group_system',              # Administration/Settings
        ]
        
        print("🔧 Adding necessary groups to admin user...")
        
        for group_xml_id in groups_to_add:
            try:
                # Find the group
                group = odoo.env['res.groups'].search([('full_name', 'like', group_xml_id.split('.')[-1])])
                if not group:
                    # Try by searching for the XML ID
                    group_data = odoo.env['ir.model.data'].search([('name', '=', group_xml_id.split('.')[-1])])
                    if group_data:
                        group = [group_data[0].res_id]
                
                if group:
                    # Add user to group
                    group_obj = odoo.env['res.groups'].browse(group[0])
                    current_users = [u.id for u in group_obj.users]
                    if admin_user.id not in current_users:
                        current_users.append(admin_user.id)
                        group_obj.write({'users': [(6, 0, current_users)]})
                        print(f"✅ Added to group: {group_obj.name}")
                    else:
                        print(f"✅ Already in group: {group_obj.name}")
                        
            except Exception as e:
                print(f"⚠️ Could not add group {group_xml_id}: {e}")
        
        # Alternative approach: Grant all available groups
        print("\n🔓 Granting all system groups...")
        all_groups = odoo.env['res.groups'].search([])
        
        admin_user.write({
            'groups_id': [(6, 0, [g.id for g in all_groups])]
        })
        
        print("✅ Admin user granted all system permissions")
        
        # Verify permissions
        print("\n🔍 Verifying permissions...")
        updated_admin = odoo.env['res.users'].browse(admin_user.id)
        group_names = [g.name for g in updated_admin.groups_id]
        print(f"📋 Admin user now has {len(group_names)} groups")
        
        # Test access to key models
        test_models = ['account.move', 'res.partner', 'product.product', 'sale.order', 'purchase.order']
        
        for model in test_models:
            try:
                odoo.env[model].search([], limit=1)
                print(f"✅ Can access {model}")
            except Exception as e:
                print(f"❌ Cannot access {model}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing permissions: {e}")
        return False

if __name__ == "__main__":
    if fix_admin_permissions():
        print("\n🎉 ADMIN PERMISSIONS FIXED!")
        print("✅ Ready to run migration")
    else:
        print("\n❌ Failed to fix permissions") 