# TSH Salesperson App - Odoo Integration Guide

## Overview

The TSH Salesperson App is a comprehensive Flutter mobile application that provides a complete mirror of your Odoo ERP system. It allows salespersons and administrators to access customers, products, sale orders, invoices, and payment data directly from their mobile devices, with full synchronization with your Odoo server.

## Features

### 🔐 Authentication & User Management
- **Odoo SSO Integration**: Login with same email/password as Odoo
- **Role-based Access**: Automatic detection of admin vs salesperson privileges
- **Session Management**: Secure session handling with automatic logout

### 📊 Dashboard
- **Real-time Analytics**: Revenue tracking, regional breakdown
- **Quick Stats**: Active orders, pending invoices, customer count
- **User Profile**: Display current user info and role

### 👥 Customer Management
- **Complete Customer List**: Mirror of Odoo res.partner records
- **Search & Filter**: Find customers quickly
- **Customer Details**: View contact information, addresses
- **Add New Customers**: Admin users can create new customers (syncs to Odoo)

### 📦 Product Catalog
- **Product Inventory**: Complete product list from Odoo
- **Category Filtering**: Filter by product categories
- **Product Details**: View prices, codes, categories
- **Search Functionality**: Find products by name or code

### 🛒 Sale Orders
- **Order Management**: View all sale orders with status tracking
- **Status Filtering**: Filter by order status (Draft, Sent, Sale, Done, Cancelled)
- **Order Details**: Customer info, amounts, dates
- **Real-time Sync**: Always up-to-date with Odoo

### 🧾 Invoices
- **Invoice Tracking**: Complete invoice list with payment status
- **Payment Status**: Track paid, unpaid, partial, overdue invoices
- **Overdue Alerts**: Visual indicators for overdue invoices
- **Invoice Details**: Full invoice information

### 💰 Payment Management
- **Payment Records**: View all received payments
- **Record New Payments**: Admin users can record payments directly
- **Payment Methods**: Support for cash, check, bank transfer, credit card
- **Real-time Updates**: Payments sync immediately to Odoo

## Technical Architecture

### Backend Integration
- **Odoo JSON-RPC API**: Direct integration with Odoo's web API
- **Authentication**: Session-based authentication using Odoo's session system
- **Data Models**: Complete mapping of Odoo models to Flutter models
- **Real-time Sync**: All data operations sync immediately with Odoo

### Security Features
- **Secure Sessions**: Encrypted session storage
- **Role Verification**: Server-side role checking
- **Data Validation**: Input validation and sanitization
- **Error Handling**: Comprehensive error handling and user feedback

## Installation & Setup

### Prerequisites
- Odoo server (version 14+ recommended)
- Flutter development environment
- Android/iOS device or emulator

### Configuration

1. **Update Odoo Server Settings** in `lib/config/app_config.dart`:
```dart
static const String odooServerUrl = 'http://your-odoo-server:8069';
static const String odooDatabaseName = 'your-database-name';
```

2. **Build and Install**:
```bash
flutter pub get
flutter build apk --release  # For Android
flutter build ios --release  # For iOS
```

### Odoo Server Requirements

Ensure your Odoo server has:
- Web API enabled
- CORS configured for mobile access
- User accounts with appropriate permissions

## User Roles & Permissions

### Administrator Access
Administrators (users with Administration/Settings access in Odoo) can:
- ✅ View all data (customers, products, orders, invoices, payments)
- ✅ Create new customers
- ✅ Record payments
- ✅ Access admin features in the side menu
- ✅ Edit records (coming soon)

### Salesperson Access
Regular users can:
- ✅ View all data (read-only)
- ✅ Access customer and product information
- ✅ View orders and invoices
- ❌ Cannot create or modify records
- ❌ No admin features access

## Data Synchronization

### Real-time Sync
- All data is fetched directly from Odoo in real-time
- No local database - always current data
- Changes made in Odoo appear immediately in the app
- Changes made in the app sync immediately to Odoo

### Supported Operations
- **Read**: All data types (customers, products, orders, invoices, payments)
- **Create**: Customers, payments (admin only)
- **Update**: Coming soon
- **Delete**: Not supported (use Odoo web interface)

## API Endpoints Used

The app integrates with these Odoo models:
- `res.partner` - Customers
- `product.product` - Products
- `sale.order` - Sale Orders
- `account.move` - Invoices
- `account.payment` - Payments
- `res.users` - User authentication and roles
- `res.groups` - User permissions

## Troubleshooting

### Common Issues

1. **Login Failed**
   - Verify Odoo server URL and database name
   - Check user credentials in Odoo
   - Ensure Odoo server is accessible from mobile device

2. **Data Not Loading**
   - Check internet connection
   - Verify Odoo server is running
   - Check user permissions in Odoo

3. **Admin Features Not Visible**
   - Verify user has Administration/Settings access in Odoo
   - Logout and login again to refresh permissions

### Error Messages
- **"Not authenticated"**: Session expired, please login again
- **"Network connection error"**: Check internet and server connectivity
- **"Server error"**: Contact system administrator

## Development

### Project Structure
```
lib/
├── config/          # App configuration
├── models/          # Data models
├── pages/           # UI screens
├── services/        # Odoo API service
└── widgets/         # Reusable UI components
```

### Key Files
- `lib/services/odoo_service.dart` - Main Odoo integration
- `lib/config/app_config.dart` - Server configuration
- `lib/models/` - Data model definitions

## Support

For technical support or feature requests:
1. Check the troubleshooting section above
2. Verify Odoo server configuration
3. Contact your system administrator

## Version History

### v1.0.0 (Current)
- ✅ Complete Odoo integration
- ✅ User authentication with role detection
- ✅ Customer, product, order, invoice, payment management
- ✅ Admin features for creating customers and recording payments
- ✅ Modern, responsive UI
- ✅ Real-time data synchronization

### Planned Features
- 🔄 Edit existing records
- 🔄 Create sale orders from mobile
- 🔄 Offline mode with sync
- 🔄 Push notifications
- 🔄 Advanced reporting
- 🔄 Barcode scanning

## License

This application is proprietary software developed for TSH. All rights reserved.