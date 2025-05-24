class ZohoOdooSyncFinal:
    """
    Final robust one-way synchronization service from Zoho Books to Odoo
    Handles all edge cases including special characters, images, and unique IDs
    """
    
    def __init__(self, config_path='/opt/odoo/migration/config/zoho_config.json'):
        self.config_path = config_path
        self.running = False
        self.sync_interval = 300  # 5 minutes
        self.last_sync_time = None
        
        # Setup logging
        self.setup_logging()
        
        # Load configuration
        self.load_config()
        self.setup_directories()
        
        # Connect to systems
        self.connect_to_odoo()
        self.test_zoho_connection()
        
        # Load tracking data
        self.load_sync_tracking()
        
        # Sync statistics
        self.sync_stats = {
            'total_syncs': 0,
            'successful_syncs': 0,
            'failed_syncs': 0,
            'products_added': 0,
            'products_updated': 0,
            'products_deleted': 0,
            'images_synced': 0,
            'images_failed': 0,
            'conflicts_resolved': 0,
            'last_sync_duration': 0,
            'errors': [],
            'service_start_time': datetime.now().isoformat()
        }
        
        self.logger.info("🚀 Final Zoho-Odoo Sync Service initialized successfully")
        
        self.uom_mapping = {}
        self.default_uom_id = 1
    
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
        """Resolve unit of measure string to Odoo UoM ID dynamically"""
        try:
            normalized = uom_string.lower().strip()
            return self.uom_mapping.get(normalized, self.default_uom_id)
        except Exception as e:
            self.logger.warning(f"⚠️ Error resolving UoM '{uom_string}', using default: {e}")
            return self.default_uom_id

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
            
            # Fetch UoM mapping
            try:
                uoms = self.odoo_models.execute_kw(
                    self.odoo_config['database'],
                    self.odoo_uid,
                    self.odoo_config['password'],
                    'uom.uom',
                    'search_read',
                    [[]],
                    {'fields': ['id', 'name', 'category_id']}
                )
                self.uom_mapping = {u['name'].lower(): u['id'] for u in uoms}
                self.default_uom_id = uoms[0]['id'] if uoms else 1
                self.logger.info(f"✅ Loaded {len(self.uom_mapping)} UoMs from Odoo (default ID: {self.default_uom_id})")
            except Exception as e:
                self.logger.warning(f"⚠️ Could not load UoMs from Odoo, using fallback: {e}")
                self.uom_mapping = {'unit': 1, 'pcs': 1, 'piece': 1}
                self.default_uom_id = 1
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to connect to Odoo: {e}")
            raise 

    def sync_active_pricelists(self):
        """Sync all active price lists from Zoho to Odoo, overwriting Odoo to match Zoho"""
        try:
            # Step 1: Fetch all price lists from Zoho
            access_token = self.get_zoho_access_token()
            if not access_token:
                self.logger.error("❌ Could not get Zoho access token for price list sync")
                return False
            headers = {'Authorization': f'Zoho-oauthtoken {access_token}'}
            org_id = self.zoho_config['organization_id']
            base_url = self.zoho_config['base_url']
            pricelists_url = f"{base_url}/pricelists?organization_id={org_id}"
            resp = requests.get(pricelists_url, headers=headers, timeout=30)
            resp.raise_for_status()
            all_pricelists = resp.json().get('price_lists', [])
            active_pricelists = [p for p in all_pricelists if p.get('status', '').lower() == 'active']
            self.logger.info(f"🔄 Found {len(active_pricelists)} active price lists in Zoho")

            # Step 2: For each active price list, fetch its items and sync to Odoo
            for zoho_pricelist in active_pricelists:
                pl_name = zoho_pricelist['name']
                pl_currency = zoho_pricelist.get('currency_id', 'IQD')
                pl_id = zoho_pricelist['price_list_id']
                # Fetch items for this price list
                items_url = f"{base_url}/pricelists/{pl_id}/items?organization_id={org_id}"
                items_resp = requests.get(items_url, headers=headers, timeout=30)
                items_resp.raise_for_status()
                items = items_resp.json().get('price_list_items', [])
                self.logger.info(f"   📋 {pl_name}: {len(items)} items")

                # Step 3: In Odoo, create/update the pricelist
                # Find or create pricelist by name/currency
                pricelist_domain = [[('name', '=', pl_name), ('currency_id', '=', pl_currency)]]
                odoo_pricelists = self.odoo_models.execute_kw(
                    self.odoo_config['database'],
                    self.odoo_uid,
                    self.odoo_config['password'],
                    'product.pricelist',
                    'search_read',
                    pricelist_domain,
                    {'fields': ['id'], 'limit': 1}
                )
                if odoo_pricelists:
                    odoo_pl_id = odoo_pricelists[0]['id']
                    # Remove all old items
                    old_items = self.odoo_models.execute_kw(
                        self.odoo_config['database'],
                        self.odoo_uid,
                        self.odoo_config['password'],
                        'product.pricelist.item',
                        'search',
                        [[('pricelist_id', '=', odoo_pl_id)]]
                    )
                    if old_items:
                        self.odoo_models.execute_kw(
                            self.odoo_config['database'],
                            self.odoo_uid,
                            self.odoo_config['password'],
                            'product.pricelist.item',
                            'unlink',
                            [old_items]
                        )
                else:
                    # Create new pricelist
                    odoo_pl_id = self.odoo_models.execute_kw(
                        self.odoo_config['database'],
                        self.odoo_uid,
                        self.odoo_config['password'],
                        'product.pricelist',
                        'create',
                        [{'name': pl_name, 'currency_id': pl_currency}]
                    )
                # Step 4: Add new items
                for item in items:
                    zoho_item_id = str(item.get('item_id'))
                    price = float(item.get('rate', 0))
                    # Find Odoo product by Zoho ID
                    odoo_products = self.odoo_models.execute_kw(
                        self.odoo_config['database'],
                        self.odoo_uid,
                        self.odoo_config['password'],
                        'product.template',
                        'search_read',
                        [[('x_zoho_item_id', '=', zoho_item_id)]],
                        {'fields': ['id'], 'limit': 1}
                    )
                    if not odoo_products:
                        continue
                    odoo_product_id = odoo_products[0]['id']
                    # Create pricelist item
                    self.odoo_models.execute_kw(
                        self.odoo_config['database'],
                        self.odoo_uid,
                        self.odoo_config['password'],
                        'product.pricelist.item',
                        'create',
                        [{
                            'pricelist_id': odoo_pl_id,
                            'applied_on': '1_product',
                            'product_tmpl_id': odoo_product_id,
                            'fixed_price': price
                        }]
                    )
                self.logger.info(f"   ✅ Synced {pl_name} to Odoo (ID: {odoo_pl_id})")
            return True
        except Exception as e:
            self.logger.error(f"❌ Error syncing price lists: {e}")
            return False 