#!/usr/bin/env python3
import json

# Load current configuration
with open('config/zoho_config.json', 'r') as f:
    config = json.load(f)

# Update passwords
config['odoo']['test_db']['password'] = 'admin'
config['odoo']['production_db']['password'] = 'admin'

# Save updated configuration
with open('config/zoho_config.json', 'w') as f:
    json.dump(config, f, indent=2)

print("✅ Configuration updated with admin passwords")
print(f"Test DB: {config['odoo']['test_db']['username']}@{config['odoo']['test_db']['host']}:{config['odoo']['test_db']['port']}")
print(f"Prod DB: {config['odoo']['production_db']['username']}@{config['odoo']['production_db']['host']}:{config['odoo']['production_db']['port']}") 