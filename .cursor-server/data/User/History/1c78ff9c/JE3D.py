#!/usr/bin/env python3
import odoorpc

passwords = ['admin', 'admin123', 'password', '123456', 'odoo', '']

for pwd in passwords:
    try:
        odoo = odoorpc.ODOO('localhost', port=8069)
        odoo.login('odtshbrain', 'admin', pwd)
        print(f'✅ SUCCESS: admin password is: "{pwd}"')
        break
    except Exception as e:
        print(f'❌ Failed with password: "{pwd}" - {str(e)[:50]}') 