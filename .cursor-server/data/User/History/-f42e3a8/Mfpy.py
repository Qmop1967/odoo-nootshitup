def transform_zoho_to_odoo(self, zoho_product: dict) -> dict:
        """Transform Zoho product to Odoo format with robust error handling"""
        try:
            product_mapping = self.field_mapping['products']['zoho_books']
            default_values = self.field_mapping['products']['default_values']
            
            odoo_product = {}
            
            # First apply default values
            odoo_product.update(default_values)
            
            # Map fields with sanitization
            for zoho_field, odoo_field in product_mapping.items():
                if zoho_field in zoho_product and zoho_product[zoho_field] is not None:
                    value = zoho_product[zoho_field]
                    
                    # Special handling for different field types
                    if zoho_field in ['rate', 'purchase_rate']:
                        try:
                            price_value = float(value) if value else 0.0
                            converted_price = self.convert_usd_to_iqd(price_value)
                            odoo_product[odoo_field] = converted_price
                        except (ValueError, TypeError):
                            odoo_product[odoo_field] = 0.0
                    elif zoho_field == 'unit':
                        # Handle unit of measure - map to Odoo's UoM ID
                        uom_id = self.resolve_uom_id(str(value))
                        if uom_id:
                            odoo_product['uom_id'] = uom_id
                            odoo_product['uom_po_id'] = uom_id
                    elif zoho_field == 'status':
                        # Handle product status (active/inactive)
                        odoo_product['active'] = value.lower() != 'inactive'
                    elif zoho_field in ['name', 'description']:
                        # Sanitize text fields
                        odoo_product[odoo_field] = self.sanitize_text(value)
                    else:
                        # For other fields, convert to string and sanitize if needed
                        if isinstance(value, str):
                            odoo_product[odoo_field] = self.sanitize_text(value)
                        else:
                            odoo_product[odoo_field] = value
            
            # Ensure required fields
            if 'name' not in odoo_product or not odoo_product['name']:
                odoo_product['name'] = f"Product {zoho_product.get('item_id', 'Unknown')}"
            
            # Ensure name is not too long (Odoo has limits)
            if len(odoo_product['name']) > 100:
                odoo_product['name'] = odoo_product['name'][:97] + "..."
            
            # Ensure x_zoho_item_id is set
            if 'x_zoho_item_id' not in odoo_product:
                odoo_product['x_zoho_item_id'] = str(zoho_product.get('item_id', ''))
            
            # Remove problematic fields
            problematic_fields = ['item_type', 'product_type', 'category_id', 'category_name', 'group_id', 'group_name']
            for field in problematic_fields:
                odoo_product.pop(field, None)
            
            # Log the transformation for debugging
            self.logger.debug(f"Transformed product data: {odoo_product}")
            
            return odoo_product
            
        except Exception as e:
            self.logger.error(f"❌ Error transforming product {zoho_product.get('item_id')}: {e}")
            # Return minimal valid product data
            return {
                'name': self.sanitize_text(zoho_product.get('name', f"Product {zoho_product.get('item_id', 'Unknown')}")),
                'type': 'product',
                'detailed_type': 'product',
                'sale_ok': True,
                'purchase_ok': True,
                'tracking': 'none',
                'active': True,
                'company_id': 1,
                'list_price': 0.0,
                'standard_price': 0.0,
                'uom_id': 1,
                'uom_po_id': 1,
                'categ_id': 1,
                'invoice_policy': 'order',
                'purchase_method': 'receive',
                'x_zoho_item_id': str(zoho_product.get('item_id', ''))
            }

def resolve_uom_id(self, uom_string: str) -> int:
        """Resolve unit of measure string to Odoo UoM ID"""
        try:
            # Common UoM mappings
            uom_mapping = {
                'pcs': 1,      # Units
                'units': 1,    # Units
                'unit': 1,     # Units
                'piece': 1,    # Units
                'pieces': 1,   # Units
                'kg': 3,       # kg
                'kgs': 3,      # kg
                'gram': 2,     # g
                'grams': 2,    # g
                'g': 2,        # g
                'dozen': 4,    # Dozens
                'dozens': 4,   # Dozens
                'box': 5,      # Box
                'boxes': 5,    # Box
                'pack': 6,     # Pack
                'packs': 6,    # Pack
                'set': 7,      # Set
                'sets': 7,     # Set
            }
            
            # Normalize input string
            normalized = uom_string.lower().strip()
            
            # Try to find in mapping
            return uom_mapping.get(normalized, 1)  # Default to 'Units' (ID: 1) if not found
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error resolving UoM '{uom_string}', using default: {e}")
            return 1  # Default to 'Units'

def get_default_field_mapping(self):
        """Default field mapping for Zoho to Odoo"""
        return {
            'products': {
                'zoho_books': {
                    'name': 'name',
                    'rate': 'list_price',
                    'purchase_rate': 'standard_price',
                    'description': 'description',
                    'sku': 'default_code',
                    'item_id': 'x_zoho_item_id',
                    'unit': 'uom_id',  # Will be transformed by resolve_uom_id
                    'status': 'active'  # Will be transformed to active/archived
                },
                'default_values': {
                    'type': 'product',
                    'sale_ok': True,
                    'purchase_ok': True,
                    'tracking': 'none',
                    'active': True,
                    'company_id': 1,  # Main company
                    'detailed_type': 'product',
                    'invoice_policy': 'order',
                    'purchase_method': 'receive',
                    'categ_id': 1,  # All Products / Saleable
                    'uom_id': 1,  # Units
                    'uom_po_id': 1  # Units
                }
            }
        }

def connect_to_odoo(self):
        """Establish connection to Odoo with proper error handling"""
        try:
            # Build URL
            url = f"http://{self.odoo_config['host']}:{self.odoo_config['port']}"
            
            # Setup common endpoint
            self.odoo_common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
            
            # Authenticate
            self.odoo_uid = self.odoo_common.authenticate(
                self.odoo_config['database'],
                self.odoo_config['username'],
                self.odoo_config['password'],
                {}
            )
            
            if not self.odoo_uid:
                raise Exception("Failed to authenticate with Odoo")
            
            # Setup object endpoint
            self.odoo_models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
            
            # Test connection by checking version
            version_info = self.odoo_common.version()
            self.logger.info(f"✅ Connected to Odoo {version_info.get('server_version', 'Unknown')}")
            
            # Get required fields for product template
            fields_data = self.odoo_models.execute_kw(
                self.odoo_config['database'],
                self.odoo_uid,
                self.odoo_config['password'],
                'product.template',
                'fields_get',
                [],
                {'attributes': ['required', 'type', 'string']}
            )
            
            # Store required fields for validation
            self.required_fields = {
                field: attrs for field, attrs in fields_data.items()
                if attrs.get('required', False)
            }
            
            self.logger.info(f"✅ Found {len(self.required_fields)} required fields for products")
            
            # Verify Zoho ID field exists
            if 'x_zoho_item_id' not in fields_data:
                self.logger.warning("⚠️ Zoho ID field not found - attempting to create it")
                self.create_zoho_field()
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to connect to Odoo: {e}")
            raise
    
    def create_zoho_field(self):
        """Create the Zoho ID field in Odoo if it doesn't exist"""
        try:
            # Get product.template model ID
            model_id = self.odoo_models.execute_kw(
                self.odoo_config['database'],
                self.odoo_uid,
                self.odoo_config['password'],
                'ir.model',
                'search',
                [[('model', '=', 'product.template')]],
                {'limit': 1}
            )[0]
            
            # Check if field already exists
            field_exists = self.odoo_models.execute_kw(
                self.odoo_config['database'],
                self.odoo_uid,
                self.odoo_config['password'],
                'ir.model.fields',
                'search_count',
                [[('model', '=', 'product.template'), ('name', '=', 'x_zoho_item_id')]]
            )
            
            if not field_exists:
                # Create the field
                field_data = {
                    'model_id': model_id,
                    'name': 'x_zoho_item_id',
                    'field_description': 'Zoho Item ID',
                    'ttype': 'char',
                    'state': 'manual',
                    'readonly': True,
                    'store': True,
                    'index': True,
                    'copied': False
                }
                
                self.odoo_models.execute_kw(
                    self.odoo_config['database'],
                    self.odoo_uid,
                    self.odoo_config['password'],
                    'ir.model.fields',
                    'create',
                    [field_data]
                )
                
                self.logger.info("✅ Created Zoho Item ID field in Odoo")
            else:
                self.logger.info("✅ Zoho Item ID field already exists in Odoo")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to create Zoho Item ID field: {e}")
            raise 