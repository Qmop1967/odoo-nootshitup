# Odoo Integration Guide

## Creating Customer "Moon Light" with Number "74838489"

You have several options to create this customer in your Odoo system:

## Option 1: Direct Python Script (Recommended)

I've created a Python script `create_odoo_customer.py` that can directly connect to your Odoo instance.

### To use the script:

```bash
python3 create_odoo_customer.py
```

The script will prompt you for:
- Odoo URL (e.g., https://your-company.odoo.com)
- Database name
- Username
- Password/API Key

### What the script does:
- ✅ Connects to your Odoo instance via XML-RPC
- ✅ Authenticates with your credentials
- ✅ Checks if customer already exists
- ✅ Creates customer "Moon Light" with reference number "74838489"
- ✅ Verifies the creation was successful

## Option 2: MCP Server Integration (Future Use)

I've added an Odoo MCP server to your `.cursor/mcp.json` configuration. To use this:

### 1. Configure Environment Variables

Update the Odoo section in `.cursor/mcp.json`:

```json
"odoo": {
  "command": "/root/.local/bin/uvx",
  "args": ["odoo-mcp"],
  "env": {
    "ODOO_URL": "https://your-company.odoo.com",
    "ODOO_DB": "your-database-name",
    "ODOO_USERNAME": "your-username",
    "ODOO_PASSWORD": "your-password-or-api-key"
  }
}
```

### 2. Restart Cursor

After updating the configuration, restart Cursor completely.

### 3. Use Natural Language

Once configured, you can ask Cursor:
- "Create a new customer named Moon Light with number 74838489"
- "Search for customer Moon Light"
- "List all customers"

## Option 3: Manual Odoo Web Interface

If you prefer to use the Odoo web interface:

1. **Log into Odoo**
   - Go to your Odoo URL
   - Log in with your credentials

2. **Navigate to Contacts**
   - Go to Contacts app
   - Click "Create" button

3. **Fill Customer Details**
   - Name: `Moon Light`
   - Reference: `74838489`
   - Mark as "Customer"
   - Save the record

## Option 4: Odoo API via curl

You can also use curl to create the customer:

```bash
# First, authenticate and get session
curl -X POST https://your-odoo.com/web/session/authenticate \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "db": "your-database",
      "login": "your-username",
      "password": "your-password"
    }
  }'

# Then create the customer (you'll need the session cookie from above)
curl -X POST https://your-odoo.com/web/dataset/call_kw \
  -H "Content-Type: application/json" \
  -H "Cookie: session_id=YOUR_SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "model": "res.partner",
      "method": "create",
      "args": [{
        "name": "Moon Light",
        "ref": "74838489",
        "customer_rank": 1,
        "is_company": false
      }],
      "kwargs": {}
    }
  }'
```

## Troubleshooting

### Common Issues:

1. **Authentication Failed**
   - Check your username and password
   - Ensure you have the correct database name
   - Verify the Odoo URL is correct

2. **Permission Denied**
   - Make sure your user has permission to create contacts
   - Check if you need admin privileges

3. **Customer Already Exists**
   - The script will check for existing customers with the same reference number
   - You can search for existing customers first

### Testing Connection:

```python
# Quick test script
import xmlrpc.client

url = "https://your-odoo.com"
db = "your-database"
username = "your-username"
password = "your-password"

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

if uid:
    print(f"✅ Connected successfully! User ID: {uid}")
else:
    print("❌ Connection failed")
```

## Next Steps

1. **Try the Python script first** - it's the most straightforward approach
2. **Configure the MCP server** for future use with Cursor
3. **Test the integration** by creating the customer
4. **Verify in Odoo** that the customer was created correctly

## Customer Details to Create

- **Name**: Moon Light
- **Reference Number**: 74838489
- **Type**: Individual Customer
- **Status**: Active

The customer will be created as an individual (not a company) and marked as a customer in your Odoo system. 