#!/bin/bash

echo "Setting up TSH Flutter MCP Server..."

# Make the MCP server executable
chmod +x /root/mcp_servers/tsh_flutter_mcp.py

# Install required Python packages
echo "Installing Python dependencies..."
pip install mcp requests

# Update the MCP configuration
echo "Updating MCP configuration..."

# Backup existing config
cp /root/.cursor/mcp.json /root/.cursor/mcp.json.backup

# Create updated MCP config with TSH Flutter server
cat > /root/.cursor/mcp.json << 'EOF'
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/root"
      ],
      "env": {}
    },
    "memory": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-memory"
      ],
      "env": {}
    },
    "brave-search": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-brave-search"
      ],
      "env": {
        "BRAVE_API_KEY": ""
      }
    },
    "git": {
      "command": "/root/.local/bin/uvx",
      "args": [
        "mcp-server-git",
        "--repository",
        "/root"
      ],
      "env": {}
    },
    "sqlite": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-sqlite"
      ],
      "env": {}
    },
    "postgres": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres"
      ],
      "env": {
        "POSTGRES_CONNECTION_STRING": ""
      }
    },
    "fetch": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-fetch"
      ],
      "env": {}
    },
    "odoo": {
      "command": "/root/.local/bin/uvx",
      "args": [
        "odoo-mcp"
      ],
      "env": {
        "ODOO_URL": "http://138.68.89.104:8069",
        "ODOO_DB": "odtshbrain",
        "ODOO_USERNAME": "khaleel@tsh.sale",
        "ODOO_PASSWORD": "Zcbm.97531tsh"
      }
    },
    "tsh-flutter": {
      "command": "python3",
      "args": [
        "/root/mcp_servers/tsh_flutter_mcp.py"
      ],
      "env": {
        "PYTHONPATH": "/root"
      }
    }
  }
}
EOF

echo "✅ TSH Flutter MCP Server setup complete!"
echo ""
echo "🔧 What's been configured:"
echo "  - Custom TSH Flutter MCP server with full app access"
echo "  - Odoo integration with your credentials"
echo "  - Flutter development tools"
echo "  - Code generation capabilities"
echo "  - Comprehensive diagnostics"
echo ""
echo "📋 Available MCP Resources:"
echo "  - flutter://app/structure - Complete app structure"
echo "  - flutter://app/dependencies - App dependencies"
echo "  - flutter://source/* - All Flutter source files"
echo "  - odoo://connection/status - Odoo connection status"
echo "  - odoo://data/customers - Customer data"
echo "  - odoo://data/products - Product catalog"
echo "  - odoo://data/sales - Sales orders"
echo ""
echo "🛠️ Available Tools:"
echo "  - flutter_analyze - Code analysis"
echo "  - flutter_test - Run tests"
echo "  - flutter_build - Build app"
echo "  - odoo_query - Query Odoo data"
echo "  - odoo_create - Create Odoo records"
echo "  - odoo_update - Update Odoo records"
echo "  - generate_flutter_code - Generate code templates"
echo "  - app_diagnostics - Comprehensive diagnostics"
echo ""
echo "🔄 Next Steps:"
echo "  1. Restart Cursor completely to load the new MCP configuration"
echo "  2. Go to Cursor Settings > MCP to verify servers are loaded"
echo "  3. Start using the enhanced capabilities!"
echo ""
echo "💡 Example Usage:"
echo "  - 'Show me the Flutter app structure'"
echo "  - 'Run diagnostics on the app'"
echo "  - 'Query Odoo customers'"
echo "  - 'Generate a new Flutter widget'"
echo "  - 'Build the app for Android'"