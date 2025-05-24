from odoo import api, SUPERUSER_ID
import odoo
from odoo.modules.registry import Registry

# Initialize Odoo
odoo.tools.config.parse_config(['-c', '/opt/odoo/odoo.conf', '-d', 'odtshbrain'])
registry = Registry.new('odtshbrain')
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    # Reset admin password
    admin_user = env['res.users'].search([('login', '=', 'admin')])
    if admin_user:
        admin_user.password = 'admin'
        print('✅ Admin password reset to: admin')
    else:
        print('❌ Admin user not found') 