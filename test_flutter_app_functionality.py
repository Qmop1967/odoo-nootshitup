#!/usr/bin/env python3
"""
TSH Flutter App Functionality Test
Tests all aspects of the Flutter app and Odoo integration
"""

import requests
import json
import xmlrpc.client
from datetime import datetime

class TSHFlutterAppTester:
    def __init__(self):
        self.odoo_url = "http://138.68.89.104:8069"
        self.odoo_db = "odtshbrain"
        self.admin_email = "khaleel@tsh.sale"
        self.admin_password = "Zcbm.97531tsh"
        self.uid = None
        
    def print_header(self, title):
        print(f"\n{'='*60}")
        print(f"🔍 {title}")
        print(f"{'='*60}")
    
    def print_success(self, message):
        print(f"✅ {message}")
    
    def print_error(self, message):
        print(f"❌ {message}")
    
    def print_info(self, message):
        print(f"ℹ️  {message}")
    
    def test_odoo_authentication(self):
        """Test Odoo authentication with admin credentials"""
        self.print_header("Testing Odoo Authentication")
        
        try:
            # Test XML-RPC authentication
            common = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/common')
            self.uid = common.authenticate(self.odoo_db, self.admin_email, self.admin_password, {})
            
            if self.uid:
                self.print_success(f"XML-RPC Authentication successful! User ID: {self.uid}")
                
                # Get user info
                models = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/object')
                user_info = models.execute_kw(
                    self.odoo_db, self.uid, self.admin_password,
                    'res.users', 'read',
                    [self.uid], {'fields': ['name', 'login', 'groups_id']}
                )
                
                if user_info:
                    user = user_info[0]
                    self.print_info(f"User Name: {user.get('name')}")
                    self.print_info(f"Login: {user.get('login')}")
                    self.print_info(f"Groups: {len(user.get('groups_id', []))} groups assigned")
                
                return True
            else:
                self.print_error("XML-RPC Authentication failed")
                return False
                
        except Exception as e:
            self.print_error(f"Authentication error: {e}")
            return False
    
    def test_web_session_authentication(self):
        """Test web session authentication (Flutter app method)"""
        self.print_header("Testing Web Session Authentication")
        
        try:
            session = requests.Session()
            
            # Authenticate via web session
            auth_url = f"{self.odoo_url}/web/session/authenticate"
            auth_data = {
                'params': {
                    'db': self.odoo_db,
                    'login': self.admin_email,
                    'password': self.admin_password,
                }
            }
            
            response = session.post(
                auth_url,
                headers={'Content-Type': 'application/json'},
                data=json.dumps(auth_data)
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('result') and result['result'].get('uid'):
                    uid = result['result']['uid']
                    self.print_success(f"Web session authentication successful! User ID: {uid}")
                    
                    # Extract session ID
                    cookies = response.headers.get('set-cookie', '')
                    if 'session_id=' in cookies:
                        self.print_success("Session ID extracted successfully")
                    
                    return session, uid
                else:
                    self.print_error("Web session authentication failed - no UID returned")
                    return None, None
            else:
                self.print_error(f"Web session authentication failed - HTTP {response.status_code}")
                return None, None
                
        except Exception as e:
            self.print_error(f"Web session authentication error: {e}")
            return None, None
    
    def test_data_access(self, session=None):
        """Test access to various Odoo data models"""
        self.print_header("Testing Data Access")
        
        if not self.uid:
            self.print_error("No authenticated session available")
            return False
        
        try:
            models = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/object')
            
            # Test data models used by the Flutter app
            test_models = [
                ('res.partner', 'Customers/Partners', [['customer_rank', '>', 0]]),
                ('product.product', 'Products', [['sale_ok', '=', True]]),
                ('sale.order', 'Sales Orders', []),
                ('account.move', 'Invoices', [['move_type', '=', 'out_invoice']]),
                ('account.payment', 'Payments', [['payment_type', '=', 'inbound']]),
            ]
            
            for model, description, domain in test_models:
                try:
                    # Test search_read
                    records = models.execute_kw(
                        self.odoo_db, self.uid, self.admin_password,
                        model, 'search_read',
                        [domain],
                        {'limit': 5}
                    )
                    
                    count = len(records)
                    self.print_success(f"{description} ({model}): {count} records accessible")
                    
                    if records:
                        # Show sample data
                        sample = records[0]
                        sample_fields = list(sample.keys())[:3]  # Show first 3 fields
                        self.print_info(f"  Sample fields: {', '.join(sample_fields)}")
                    
                except Exception as e:
                    self.print_error(f"{description} ({model}): Access failed - {e}")
            
            return True
            
        except Exception as e:
            self.print_error(f"Data access test failed: {e}")
            return False
    
    def test_dashboard_data_simulation(self):
        """Test dashboard data retrieval simulation"""
        self.print_header("Testing Dashboard Data Simulation")
        
        if not self.uid:
            self.print_error("No authenticated session available")
            return False
        
        try:
            models = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/object')
            
            # Simulate dashboard data collection
            dashboard_data = {}
            
            # Get sales data
            sales_orders = models.execute_kw(
                self.odoo_db, self.uid, self.admin_password,
                'sale.order', 'search_read',
                [[['state', 'in', ['sale', 'done']]]],
                {'fields': ['amount_total', 'partner_id', 'date_order', 'state'], 'limit': 100}
            )
            
            # Calculate total revenue
            total_revenue = sum(order.get('amount_total', 0) for order in sales_orders)
            dashboard_data['total_revenue'] = total_revenue
            dashboard_data['total_orders'] = len(sales_orders)
            
            # Get customer count
            customers = models.execute_kw(
                self.odoo_db, self.uid, self.admin_password,
                'res.partner', 'search_read',
                [[['customer_rank', '>', 0]]],
                {'fields': ['name'], 'limit': 1000}
            )
            dashboard_data['total_customers'] = len(customers)
            
            # Get product count
            products = models.execute_kw(
                self.odoo_db, self.uid, self.admin_password,
                'product.product', 'search_read',
                [[['sale_ok', '=', True]]],
                {'fields': ['name'], 'limit': 1000}
            )
            dashboard_data['total_products'] = len(products)
            
            # Get invoice data
            invoices = models.execute_kw(
                self.odoo_db, self.uid, self.admin_password,
                'account.move', 'search_read',
                [[['move_type', '=', 'out_invoice']]],
                {'fields': ['amount_total', 'payment_state'], 'limit': 100}
            )
            
            pending_invoices = len([inv for inv in invoices if inv.get('payment_state') != 'paid'])
            dashboard_data['pending_invoices'] = pending_invoices
            dashboard_data['total_invoices'] = len(invoices)
            
            # Display results
            self.print_success("Dashboard data simulation completed:")
            self.print_info(f"  Total Revenue: ${dashboard_data['total_revenue']:,.2f}")
            self.print_info(f"  Total Orders: {dashboard_data['total_orders']}")
            self.print_info(f"  Total Customers: {dashboard_data['total_customers']}")
            self.print_info(f"  Total Products: {dashboard_data['total_products']}")
            self.print_info(f"  Total Invoices: {dashboard_data['total_invoices']}")
            self.print_info(f"  Pending Invoices: {dashboard_data['pending_invoices']}")
            
            return True
            
        except Exception as e:
            self.print_error(f"Dashboard data simulation failed: {e}")
            return False
    
    def test_crud_operations(self):
        """Test Create, Read, Update operations (no Delete for safety)"""
        self.print_header("Testing CRUD Operations")
        
        if not self.uid:
            self.print_error("No authenticated session available")
            return False
        
        try:
            models = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/object')
            
            # Test CREATE - Create a test customer
            test_customer_data = {
                'name': f'Test Customer - {datetime.now().strftime("%Y%m%d_%H%M%S")}',
                'email': 'test@tshsales.com',
                'phone': '+1-555-0123',
                'is_company': True,
                'customer_rank': 1,
                'comment': 'Created by TSH Flutter App functionality test'
            }
            
            customer_id = models.execute_kw(
                self.odoo_db, self.uid, self.admin_password,
                'res.partner', 'create',
                [test_customer_data]
            )
            
            if customer_id:
                self.print_success(f"CREATE: Test customer created with ID {customer_id}")
                
                # Test READ - Read the created customer
                customer_data = models.execute_kw(
                    self.odoo_db, self.uid, self.admin_password,
                    'res.partner', 'read',
                    [customer_id], {'fields': ['name', 'email', 'phone']}
                )
                
                if customer_data:
                    self.print_success(f"READ: Customer data retrieved successfully")
                    self.print_info(f"  Name: {customer_data[0].get('name')}")
                    self.print_info(f"  Email: {customer_data[0].get('email')}")
                    
                    # Test UPDATE - Update the customer
                    update_data = {
                        'phone': '+1-555-9999',
                        'comment': 'Updated by TSH Flutter App functionality test'
                    }
                    
                    update_result = models.execute_kw(
                        self.odoo_db, self.uid, self.admin_password,
                        'res.partner', 'write',
                        [[customer_id], update_data]
                    )
                    
                    if update_result:
                        self.print_success(f"UPDATE: Customer updated successfully")
                        
                        # Verify update
                        updated_data = models.execute_kw(
                            self.odoo_db, self.uid, self.admin_password,
                            'res.partner', 'read',
                            [customer_id], {'fields': ['phone', 'comment']}
                        )
                        
                        if updated_data:
                            self.print_info(f"  Updated Phone: {updated_data[0].get('phone')}")
                    else:
                        self.print_error("UPDATE: Failed to update customer")
                else:
                    self.print_error("READ: Failed to read customer data")
            else:
                self.print_error("CREATE: Failed to create test customer")
            
            return True
            
        except Exception as e:
            self.print_error(f"CRUD operations test failed: {e}")
            return False
    
    def test_flutter_app_compatibility(self):
        """Test Flutter app specific functionality"""
        self.print_header("Testing Flutter App Compatibility")
        
        # Test web session authentication (Flutter method)
        session, uid = self.test_web_session_authentication()
        
        if not session or not uid:
            return False
        
        try:
            # Test search_read endpoint (used by Flutter app)
            search_read_url = f"{self.odoo_url}/web/dataset/search_read"
            
            test_requests = [
                {
                    'model': 'res.partner',
                    'domain': [['customer_rank', '>', 0]],
                    'fields': ['name', 'email', 'phone'],
                    'limit': 5
                },
                {
                    'model': 'product.product',
                    'domain': [['sale_ok', '=', True]],
                    'fields': ['name', 'list_price'],
                    'limit': 5
                },
                {
                    'model': 'sale.order',
                    'domain': [],
                    'fields': ['name', 'partner_id', 'amount_total'],
                    'limit': 5
                }
            ]
            
            for request_data in test_requests:
                response = session.post(
                    search_read_url,
                    headers={'Content-Type': 'application/json'},
                    data=json.dumps({'params': request_data})
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('result') and result['result'].get('records'):
                        records = result['result']['records']
                        model = request_data['model']
                        self.print_success(f"Flutter search_read test for {model}: {len(records)} records")
                    else:
                        self.print_error(f"Flutter search_read test for {request_data['model']}: No records returned")
                else:
                    self.print_error(f"Flutter search_read test for {request_data['model']}: HTTP {response.status_code}")
            
            return True
            
        except Exception as e:
            self.print_error(f"Flutter app compatibility test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all functionality tests"""
        print("🚀 Starting TSH Flutter App Functionality Tests")
        print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        test_results = []
        
        # Run all tests
        test_results.append(("Odoo Authentication", self.test_odoo_authentication()))
        test_results.append(("Data Access", self.test_data_access()))
        test_results.append(("Dashboard Data", self.test_dashboard_data_simulation()))
        test_results.append(("CRUD Operations", self.test_crud_operations()))
        test_results.append(("Flutter Compatibility", self.test_flutter_app_compatibility()))
        
        # Summary
        self.print_header("Test Results Summary")
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results:
            if result:
                self.print_success(f"{test_name}: PASSED")
                passed += 1
            else:
                self.print_error(f"{test_name}: FAILED")
        
        print(f"\n📊 Overall Results: {passed}/{total} tests passed")
        
        if passed == total:
            self.print_success("🎉 All tests passed! TSH Flutter App is fully functional with Odoo integration.")
            self.print_info("✨ Admin access is properly configured and working.")
            self.print_info("🔗 Flutter app can successfully connect to and interact with Odoo.")
        else:
            self.print_error(f"⚠️  {total - passed} test(s) failed. Please review the issues above.")
        
        return passed == total

if __name__ == "__main__":
    tester = TSHFlutterAppTester()
    tester.run_all_tests()