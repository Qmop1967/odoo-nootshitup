#!/usr/bin/env python3
"""
TSH Salesperson Flutter App MCP Server
Provides comprehensive access to Flutter app codebase, Odoo data, and development tools
"""

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# MCP SDK imports
try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Resource,
        Tool,
        TextContent,
        ImageContent,
        EmbeddedResource,
        LoggingLevel
    )
except ImportError:
    print("MCP SDK not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "mcp"])
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Resource,
        Tool,
        TextContent,
        ImageContent,
        EmbeddedResource,
        LoggingLevel
    )

# Additional imports for Odoo integration
try:
    import requests
    import xmlrpc.client
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests
    import xmlrpc.client

class TSHFlutterMCPServer:
    def __init__(self):
        self.app_root = Path("/root")
        self.lib_path = self.app_root / "lib"
        self.server = Server("tsh-flutter-mcp")
        
        # Odoo configuration
        self.odoo_url = "http://138.68.89.104:8069"
        self.odoo_db = "odtshbrain"
        self.odoo_username = "khaleel@tsh.sale"
        self.odoo_password = "Zcbm.97531tsh"
        self.odoo_uid = None
        
        self.setup_handlers()
    
    def setup_handlers(self):
        """Set up all MCP handlers"""
        
        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            """List all available Flutter app resources"""
            resources = []
            
            # Flutter app structure
            resources.extend([
                Resource(
                    uri="flutter://app/structure",
                    name="Flutter App Structure",
                    description="Complete Flutter app directory structure and file organization",
                    mimeType="application/json"
                ),
                Resource(
                    uri="flutter://app/dependencies",
                    name="App Dependencies",
                    description="Flutter app dependencies from pubspec.yaml",
                    mimeType="application/yaml"
                ),
                Resource(
                    uri="flutter://app/config",
                    name="App Configuration",
                    description="App configuration and settings",
                    mimeType="text/plain"
                )
            ])
            
            # Flutter source files
            if self.lib_path.exists():
                for dart_file in self.lib_path.rglob("*.dart"):
                    rel_path = dart_file.relative_to(self.app_root)
                    resources.append(Resource(
                        uri=f"flutter://source/{rel_path}",
                        name=f"Flutter Source: {rel_path.name}",
                        description=f"Flutter Dart source file: {rel_path}",
                        mimeType="text/x-dart"
                    ))
            
            # Odoo integration resources
            resources.extend([
                Resource(
                    uri="odoo://connection/status",
                    name="Odoo Connection Status",
                    description="Current Odoo connection status and configuration",
                    mimeType="application/json"
                ),
                Resource(
                    uri="odoo://data/customers",
                    name="Odoo Customers",
                    description="Customer data from Odoo CRM",
                    mimeType="application/json"
                ),
                Resource(
                    uri="odoo://data/products",
                    name="Odoo Products",
                    description="Product catalog from Odoo",
                    mimeType="application/json"
                ),
                Resource(
                    uri="odoo://data/sales",
                    name="Odoo Sales Orders",
                    description="Sales orders and opportunities",
                    mimeType="application/json"
                )
            ])
            
            return resources
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read specific resource content"""
            
            if uri.startswith("flutter://app/structure"):
                return await self._get_app_structure()
            elif uri.startswith("flutter://app/dependencies"):
                return await self._get_dependencies()
            elif uri.startswith("flutter://app/config"):
                return await self._get_app_config()
            elif uri.startswith("flutter://source/"):
                file_path = uri.replace("flutter://source/", "")
                return await self._read_source_file(file_path)
            elif uri.startswith("odoo://connection/status"):
                return await self._get_odoo_status()
            elif uri.startswith("odoo://data/customers"):
                return await self._get_odoo_customers()
            elif uri.startswith("odoo://data/products"):
                return await self._get_odoo_products()
            elif uri.startswith("odoo://data/sales"):
                return await self._get_odoo_sales()
            else:
                raise ValueError(f"Unknown resource URI: {uri}")
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List all available tools"""
            return [
                Tool(
                    name="flutter_analyze",
                    description="Run Flutter analyze on the codebase to check for issues",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Specific path to analyze (optional, defaults to entire app)"
                            }
                        }
                    }
                ),
                Tool(
                    name="flutter_test",
                    description="Run Flutter tests",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "test_file": {
                                "type": "string",
                                "description": "Specific test file to run (optional)"
                            }
                        }
                    }
                ),
                Tool(
                    name="flutter_build",
                    description="Build Flutter app for specified platform",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "platform": {
                                "type": "string",
                                "enum": ["android", "ios", "web"],
                                "description": "Target platform to build for"
                            },
                            "mode": {
                                "type": "string",
                                "enum": ["debug", "release", "profile"],
                                "default": "debug",
                                "description": "Build mode"
                            }
                        },
                        "required": ["platform"]
                    }
                ),
                Tool(
                    name="odoo_query",
                    description="Execute queries against Odoo database",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "model": {
                                "type": "string",
                                "description": "Odoo model to query (e.g., 'res.partner', 'product.product')"
                            },
                            "domain": {
                                "type": "array",
                                "description": "Search domain filters",
                                "default": []
                            },
                            "fields": {
                                "type": "array",
                                "description": "Fields to retrieve",
                                "default": []
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of records to return",
                                "default": 100
                            }
                        },
                        "required": ["model"]
                    }
                ),
                Tool(
                    name="odoo_create",
                    description="Create new records in Odoo",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "model": {
                                "type": "string",
                                "description": "Odoo model to create record in"
                            },
                            "values": {
                                "type": "object",
                                "description": "Field values for the new record"
                            }
                        },
                        "required": ["model", "values"]
                    }
                ),
                Tool(
                    name="odoo_update",
                    description="Update existing records in Odoo",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "model": {
                                "type": "string",
                                "description": "Odoo model"
                            },
                            "record_ids": {
                                "type": "array",
                                "description": "IDs of records to update"
                            },
                            "values": {
                                "type": "object",
                                "description": "Field values to update"
                            }
                        },
                        "required": ["model", "record_ids", "values"]
                    }
                ),
                Tool(
                    name="generate_flutter_code",
                    description="Generate Flutter code based on specifications",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["widget", "page", "model", "service"],
                                "description": "Type of code to generate"
                            },
                            "name": {
                                "type": "string",
                                "description": "Name of the component to generate"
                            },
                            "specifications": {
                                "type": "string",
                                "description": "Detailed specifications for the code"
                            }
                        },
                        "required": ["type", "name", "specifications"]
                    }
                ),
                Tool(
                    name="app_diagnostics",
                    description="Run comprehensive diagnostics on the Flutter app",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "include_odoo": {
                                "type": "boolean",
                                "default": True,
                                "description": "Include Odoo connectivity tests"
                            }
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Execute tool calls"""
            
            if name == "flutter_analyze":
                return await self._flutter_analyze(arguments.get("path"))
            elif name == "flutter_test":
                return await self._flutter_test(arguments.get("test_file"))
            elif name == "flutter_build":
                return await self._flutter_build(
                    arguments["platform"], 
                    arguments.get("mode", "debug")
                )
            elif name == "odoo_query":
                return await self._odoo_query(
                    arguments["model"],
                    arguments.get("domain", []),
                    arguments.get("fields", []),
                    arguments.get("limit", 100)
                )
            elif name == "odoo_create":
                return await self._odoo_create(
                    arguments["model"],
                    arguments["values"]
                )
            elif name == "odoo_update":
                return await self._odoo_update(
                    arguments["model"],
                    arguments["record_ids"],
                    arguments["values"]
                )
            elif name == "generate_flutter_code":
                return await self._generate_flutter_code(
                    arguments["type"],
                    arguments["name"],
                    arguments["specifications"]
                )
            elif name == "app_diagnostics":
                return await self._app_diagnostics(
                    arguments.get("include_odoo", True)
                )
            else:
                raise ValueError(f"Unknown tool: {name}")
    
    # Resource reading methods
    async def _get_app_structure(self) -> str:
        """Get Flutter app structure"""
        structure = {}
        
        def scan_directory(path: Path, max_depth: int = 3, current_depth: int = 0):
            if current_depth >= max_depth:
                return {}
            
            result = {}
            try:
                for item in path.iterdir():
                    if item.name.startswith('.'):
                        continue
                    
                    if item.is_file():
                        result[item.name] = {
                            "type": "file",
                            "size": item.stat().st_size,
                            "extension": item.suffix
                        }
                    elif item.is_dir():
                        result[item.name] = {
                            "type": "directory",
                            "children": scan_directory(item, max_depth, current_depth + 1)
                        }
            except PermissionError:
                pass
            
            return result
        
        structure = scan_directory(self.app_root)
        return json.dumps(structure, indent=2)
    
    async def _get_dependencies(self) -> str:
        """Get pubspec.yaml content"""
        pubspec_path = self.app_root / "pubspec.yaml"
        if pubspec_path.exists():
            return pubspec_path.read_text()
        return "pubspec.yaml not found"
    
    async def _get_app_config(self) -> str:
        """Get app configuration"""
        config_path = self.lib_path / "config" / "app_config.dart"
        if config_path.exists():
            return config_path.read_text()
        return "App configuration not found"
    
    async def _read_source_file(self, file_path: str) -> str:
        """Read Flutter source file"""
        full_path = self.app_root / file_path
        if full_path.exists() and full_path.suffix == ".dart":
            return full_path.read_text()
        return f"File not found: {file_path}"
    
    # Odoo integration methods
    async def _authenticate_odoo(self) -> bool:
        """Authenticate with Odoo"""
        try:
            common = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/common')
            self.odoo_uid = common.authenticate(
                self.odoo_db, self.odoo_username, self.odoo_password, {}
            )
            return self.odoo_uid is not None
        except Exception as e:
            print(f"Odoo authentication failed: {e}")
            return False
    
    async def _get_odoo_status(self) -> str:
        """Get Odoo connection status"""
        status = {
            "url": self.odoo_url,
            "database": self.odoo_db,
            "username": self.odoo_username,
            "connected": False,
            "uid": None
        }
        
        if await self._authenticate_odoo():
            status["connected"] = True
            status["uid"] = self.odoo_uid
        
        return json.dumps(status, indent=2)
    
    async def _get_odoo_customers(self) -> str:
        """Get customer data from Odoo"""
        if not await self._authenticate_odoo():
            return json.dumps({"error": "Failed to authenticate with Odoo"})
        
        try:
            models = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/object')
            customers = models.execute_kw(
                self.odoo_db, self.odoo_uid, self.odoo_password,
                'res.partner', 'search_read',
                [[['is_company', '=', True]]],
                {'fields': ['name', 'email', 'phone', 'city', 'country_id'], 'limit': 50}
            )
            return json.dumps(customers, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    async def _get_odoo_products(self) -> str:
        """Get product data from Odoo"""
        if not await self._authenticate_odoo():
            return json.dumps({"error": "Failed to authenticate with Odoo"})
        
        try:
            models = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/object')
            products = models.execute_kw(
                self.odoo_db, self.odoo_uid, self.odoo_password,
                'product.product', 'search_read',
                [[]],
                {'fields': ['name', 'list_price', 'standard_price', 'categ_id'], 'limit': 50}
            )
            return json.dumps(products, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    async def _get_odoo_sales(self) -> str:
        """Get sales order data from Odoo"""
        if not await self._authenticate_odoo():
            return json.dumps({"error": "Failed to authenticate with Odoo"})
        
        try:
            models = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/object')
            sales = models.execute_kw(
                self.odoo_db, self.odoo_uid, self.odoo_password,
                'sale.order', 'search_read',
                [[]],
                {'fields': ['name', 'partner_id', 'amount_total', 'state', 'date_order'], 'limit': 50}
            )
            return json.dumps(sales, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    # Tool implementation methods
    async def _flutter_analyze(self, path: Optional[str]) -> List[TextContent]:
        """Run Flutter analyze"""
        try:
            cmd = ["flutter", "analyze"]
            if path:
                cmd.append(path)
            
            result = subprocess.run(
                cmd, 
                cwd=self.app_root, 
                capture_output=True, 
                text=True
            )
            
            output = f"Flutter Analyze Results:\n\n"
            output += f"Exit Code: {result.returncode}\n\n"
            output += f"STDOUT:\n{result.stdout}\n\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"
            
            return [TextContent(type="text", text=output)]
        except Exception as e:
            return [TextContent(type="text", text=f"Error running flutter analyze: {e}")]
    
    async def _flutter_test(self, test_file: Optional[str]) -> List[TextContent]:
        """Run Flutter tests"""
        try:
            cmd = ["flutter", "test"]
            if test_file:
                cmd.append(test_file)
            
            result = subprocess.run(
                cmd, 
                cwd=self.app_root, 
                capture_output=True, 
                text=True
            )
            
            output = f"Flutter Test Results:\n\n"
            output += f"Exit Code: {result.returncode}\n\n"
            output += f"STDOUT:\n{result.stdout}\n\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"
            
            return [TextContent(type="text", text=output)]
        except Exception as e:
            return [TextContent(type="text", text=f"Error running flutter test: {e}")]
    
    async def _flutter_build(self, platform: str, mode: str) -> List[TextContent]:
        """Build Flutter app"""
        try:
            cmd = ["flutter", "build", platform]
            if mode != "debug":
                cmd.extend([f"--{mode}"])
            
            result = subprocess.run(
                cmd, 
                cwd=self.app_root, 
                capture_output=True, 
                text=True
            )
            
            output = f"Flutter Build Results ({platform} - {mode}):\n\n"
            output += f"Exit Code: {result.returncode}\n\n"
            output += f"STDOUT:\n{result.stdout}\n\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"
            
            return [TextContent(type="text", text=output)]
        except Exception as e:
            return [TextContent(type="text", text=f"Error building Flutter app: {e}")]
    
    async def _odoo_query(self, model: str, domain: List, fields: List, limit: int) -> List[TextContent]:
        """Execute Odoo query"""
        if not await self._authenticate_odoo():
            return [TextContent(type="text", text="Failed to authenticate with Odoo")]
        
        try:
            models = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/object')
            records = models.execute_kw(
                self.odoo_db, self.odoo_uid, self.odoo_password,
                model, 'search_read',
                [domain],
                {'fields': fields, 'limit': limit} if fields else {'limit': limit}
            )
            
            result = {
                "model": model,
                "domain": domain,
                "fields": fields,
                "limit": limit,
                "count": len(records),
                "records": records
            }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error querying Odoo: {e}")]
    
    async def _odoo_create(self, model: str, values: Dict) -> List[TextContent]:
        """Create record in Odoo"""
        if not await self._authenticate_odoo():
            return [TextContent(type="text", text="Failed to authenticate with Odoo")]
        
        try:
            models = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/object')
            record_id = models.execute_kw(
                self.odoo_db, self.odoo_uid, self.odoo_password,
                model, 'create',
                [values]
            )
            
            result = {
                "model": model,
                "created_id": record_id,
                "values": values
            }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error creating Odoo record: {e}")]
    
    async def _odoo_update(self, model: str, record_ids: List[int], values: Dict) -> List[TextContent]:
        """Update records in Odoo"""
        if not await self._authenticate_odoo():
            return [TextContent(type="text", text="Failed to authenticate with Odoo")]
        
        try:
            models = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/object')
            success = models.execute_kw(
                self.odoo_db, self.odoo_uid, self.odoo_password,
                model, 'write',
                [record_ids, values]
            )
            
            result = {
                "model": model,
                "updated_ids": record_ids,
                "values": values,
                "success": success
            }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error updating Odoo records: {e}")]
    
    async def _generate_flutter_code(self, code_type: str, name: str, specifications: str) -> List[TextContent]:
        """Generate Flutter code based on specifications"""
        # This is a simplified code generator - you can enhance it with AI-powered generation
        templates = {
            "widget": self._generate_widget_template,
            "page": self._generate_page_template,
            "model": self._generate_model_template,
            "service": self._generate_service_template
        }
        
        if code_type not in templates:
            return [TextContent(type="text", text=f"Unknown code type: {code_type}")]
        
        try:
            code = templates[code_type](name, specifications)
            return [TextContent(type="text", text=code)]
        except Exception as e:
            return [TextContent(type="text", text=f"Error generating code: {e}")]
    
    def _generate_widget_template(self, name: str, specifications: str) -> str:
        """Generate Flutter widget template"""
        class_name = ''.join(word.capitalize() for word in name.split('_'))
        return f"""import 'package:flutter/material.dart';

class {class_name} extends StatelessWidget {{
  const {class_name}({{Key? key}}) : super(key: key);

  @override
  Widget build(BuildContext context) {{
    // TODO: Implement widget based on specifications:
    // {specifications}
    
    return Container(
      child: Text('{class_name}'),
    );
  }}
}}"""
    
    def _generate_page_template(self, name: str, specifications: str) -> str:
        """Generate Flutter page template"""
        class_name = ''.join(word.capitalize() for word in name.split('_'))
        return f"""import 'package:flutter/material.dart';

class {class_name}Page extends StatefulWidget {{
  const {class_name}Page({{Key? key}}) : super(key: key);

  @override
  State<{class_name}Page> createState() => _{class_name}PageState();
}}

class _{class_name}PageState extends State<{class_name}Page> {{
  @override
  Widget build(BuildContext context) {{
    // TODO: Implement page based on specifications:
    // {specifications}
    
    return Scaffold(
      appBar: AppBar(
        title: Text('{class_name}'),
      ),
      body: Center(
        child: Text('{class_name} Page'),
      ),
    );
  }}
}}"""
    
    def _generate_model_template(self, name: str, specifications: str) -> str:
        """Generate Flutter model template"""
        class_name = ''.join(word.capitalize() for word in name.split('_'))
        return f"""class {class_name} {{
  // TODO: Add properties based on specifications:
  // {specifications}
  
  {class_name}();
  
  factory {class_name}.fromJson(Map<String, dynamic> json) {{
    return {class_name}();
  }}
  
  Map<String, dynamic> toJson() {{
    return {{}};
  }}
}}"""
    
    def _generate_service_template(self, name: str, specifications: str) -> str:
        """Generate Flutter service template"""
        class_name = ''.join(word.capitalize() for word in name.split('_'))
        return f"""import 'dart:convert';
import 'package:http/http.dart' as http;

class {class_name}Service {{
  // TODO: Implement service based on specifications:
  // {specifications}
  
  static const String baseUrl = 'your-api-url';
  
  Future<List<dynamic>> fetchData() async {{
    try {{
      final response = await http.get(Uri.parse('$baseUrl/endpoint'));
      if (response.statusCode == 200) {{
        return json.decode(response.body);
      }} else {{
        throw Exception('Failed to load data');
      }}
    }} catch (e) {{
      throw Exception('Error: $e');
    }}
  }}
}}"""
    
    async def _app_diagnostics(self, include_odoo: bool) -> List[TextContent]:
        """Run comprehensive app diagnostics"""
        diagnostics = []
        
        # Flutter environment check
        try:
            result = subprocess.run(
                ["flutter", "doctor"], 
                cwd=self.app_root, 
                capture_output=True, 
                text=True
            )
            diagnostics.append(f"Flutter Doctor:\n{result.stdout}")
        except Exception as e:
            diagnostics.append(f"Flutter Doctor Error: {e}")
        
        # Dependencies check
        try:
            result = subprocess.run(
                ["flutter", "pub", "deps"], 
                cwd=self.app_root, 
                capture_output=True, 
                text=True
            )
            diagnostics.append(f"Dependencies Status:\n{result.stdout}")
        except Exception as e:
            diagnostics.append(f"Dependencies Check Error: {e}")
        
        # Odoo connectivity check
        if include_odoo:
            if await self._authenticate_odoo():
                diagnostics.append("Odoo Connection: ✅ Connected successfully")
            else:
                diagnostics.append("Odoo Connection: ❌ Failed to connect")
        
        # File structure validation
        required_files = [
            "pubspec.yaml",
            "lib/main.dart",
            "lib/services/odoo_service.dart"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (self.app_root / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            diagnostics.append(f"Missing Files: {', '.join(missing_files)}")
        else:
            diagnostics.append("File Structure: ✅ All required files present")
        
        return [TextContent(type="text", text="\n\n".join(diagnostics))]

async def main():
    """Main entry point"""
    server_instance = TSHFlutterMCPServer()
    
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="tsh-flutter-mcp",
                server_version="1.0.0",
                capabilities=server_instance.server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())