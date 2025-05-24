#!/usr/bin/env python3
import json

config = {
    "zoho_books": {
        "client_id": "1000.GD7654YNI3QGSGCR26VJWN0TXSKGWJ",
        "client_secret": "a1cd4bacae541d5266b3e16fb7437442f293159a22",
        "refresh_token": "1000.fe9b5044a847da4fff37eba67ee41bd9.7495446741c4f7554e5cdcb97243c961",
        "organization_id": "748369814",
        "base_url": "https://www.zohoapis.com/books/v3",
        "rate_limit": 100,
        "endpoints": {
            "contacts": "/contacts",
            "items": "/items",
            "invoices": "/invoices",
            "bills": "/bills",
            "chartofaccounts": "/chartofaccounts",
            "taxes": "/settings/taxes",
            "payments": "/customerpayments"
        }
    },
    "zoho_inventory": {
        "client_id": "1000.GD7654YNI3QGSGCR26VJWN0TXSKGWJ",
        "client_secret": "a1cd4bacae541d5266b3e16fb7437442f293159a22",
        "refresh_token": "1000.107530bebdb9fb42c28257e272142939.e6b2c9c198cb512da78a218c628ac549",
        "organization_id": "748369814",
        "base_url": "https://www.zohoapis.com/inventory/v1",
        "rate_limit": 200,
        "endpoints": {
            "items": "/items",
            "warehouses": "/settings/warehouses",
            "salesorders": "/salesorders",
            "purchaseorders": "/purchaseorders",
            "inventoryadjustments": "/inventoryadjustments"
        }
    },
    "odoo": {
        "test_db": {
            "host": "localhost",
            "port": 8070,
            "database": "odtshbrain_test",
            "username": "admin",
            "password": "admin_password_here"
        },
        "production_db": {
            "host": "localhost",
            "port": 8069,
            "database": "odtshbrain",
            "username": "admin",
            "password": "admin_password_here"
        }
    },
    "migration_settings": {
        "batch_size": 100,
        "delay_between_requests": 0.6,
        "max_retries": 3,
        "backup_before_import": True,
        "validate_data": True,
        "log_level": "INFO"
    }
}

with open('config/zoho_config.json', 'w') as f:
    json.dump(config, f, indent=2)

print("✅ Configuration updated with correct refresh tokens and API URLs!")
print(f"📚 Books URL: {config['zoho_books']['base_url']}")
print(f"📦 Inventory URL: {config['zoho_inventory']['base_url']}")
print(f"📚 Books token: {config['zoho_books']['refresh_token'][:30]}...")
print(f"📦 Inventory token: {config['zoho_inventory']['refresh_token'][:30]}...") 