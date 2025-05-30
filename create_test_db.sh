#!/bin/bash

# Odoo Test Database Creation Script
# Creates a test copy of your production Odoo database

set -e  # Exit on any error

echo "🚀 Odoo Test Database Creator"
echo "================================"
echo "This script will create a test copy of your Odoo database"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get Odoo configuration
read -p "Enter Odoo URL (e.g., https://your-odoo.com): " ODOO_URL
read -p "Enter Odoo database name: " SOURCE_DB
read -s -p "Enter master password: " MASTER_PASSWORD
echo ""
read -p "Enter test database suffix (default: _test): " TEST_SUFFIX

# Set defaults
ODOO_URL=${ODOO_URL%/}  # Remove trailing slash
TEST_SUFFIX=${TEST_SUFFIX:-_test}
TEST_DB="${SOURCE_DB}${TEST_SUFFIX}"

print_status "Source Database: $SOURCE_DB"
print_status "Test Database: $TEST_DB"
print_status "Odoo URL: $ODOO_URL"

# Create backup directory
BACKUP_DIR="./odoo_backups"
mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/${SOURCE_DB}_backup_${TIMESTAMP}.zip"

print_status "Creating backup directory: $BACKUP_DIR"

# Method 1: Using curl to backup database
backup_with_curl() {
    print_status "Creating backup using HTTP API..."
    
    # Create backup
    curl -X POST "${ODOO_URL}/web/database/backup" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "master_pwd=${MASTER_PASSWORD}&name=${SOURCE_DB}&backup_format=zip" \
        -o "$BACKUP_FILE" \
        --fail --silent --show-error
    
    if [ $? -eq 0 ] && [ -f "$BACKUP_FILE" ] && [ -s "$BACKUP_FILE" ]; then
        print_success "Backup created: $BACKUP_FILE"
        return 0
    else
        print_error "Backup failed"
        return 1
    fi
}

# Method 2: Using Odoo command line (if available)
backup_with_odoo_cli() {
    print_status "Attempting backup with Odoo CLI..."
    
    # Check if odoo command is available
    if command -v odoo &> /dev/null; then
        odoo -d "$SOURCE_DB" --db_host=localhost --stop-after-init --backup-db="$BACKUP_FILE"
        if [ $? -eq 0 ]; then
            print_success "Backup created with Odoo CLI: $BACKUP_FILE"
            return 0
        fi
    fi
    
    print_warning "Odoo CLI not available or backup failed"
    return 1
}

# Method 3: Direct PostgreSQL backup (if accessible)
backup_with_pg_dump() {
    print_status "Attempting PostgreSQL backup..."
    
    if command -v pg_dump &> /dev/null; then
        # Try to backup using pg_dump
        pg_dump "$SOURCE_DB" > "${BACKUP_FILE%.zip}.sql" 2>/dev/null
        if [ $? -eq 0 ]; then
            # Compress the SQL file
            zip "$BACKUP_FILE" "${BACKUP_FILE%.zip}.sql"
            rm "${BACKUP_FILE%.zip}.sql"
            print_success "PostgreSQL backup created: $BACKUP_FILE"
            return 0
        fi
    fi
    
    print_warning "PostgreSQL backup not available"
    return 1
}

# Try backup methods in order
print_status "Starting backup process..."

if backup_with_curl; then
    BACKUP_SUCCESS=true
elif backup_with_odoo_cli; then
    BACKUP_SUCCESS=true
elif backup_with_pg_dump; then
    BACKUP_SUCCESS=true
else
    print_error "All backup methods failed!"
    echo ""
    echo "Manual backup instructions:"
    echo "1. Go to $ODOO_URL/web/database/manager"
    echo "2. Click 'Backup' next to your database"
    echo "3. Download the backup file"
    echo "4. Save it as: $BACKUP_FILE"
    echo "5. Run this script again with the backup file"
    exit 1
fi

# Restore database
restore_database() {
    print_status "Restoring database as $TEST_DB..."
    
    # Method 1: Using curl to restore
    curl -X POST "${ODOO_URL}/web/database/restore" \
        -F "master_pwd=${MASTER_PASSWORD}" \
        -F "name=${TEST_DB}" \
        -F "backup_file=@${BACKUP_FILE}" \
        -F "copy=true" \
        --fail --silent --show-error
    
    if [ $? -eq 0 ]; then
        print_success "Database restored as $TEST_DB"
        return 0
    else
        print_error "Database restore failed"
        return 1
    fi
}

# Check if test database already exists
check_existing_db() {
    print_status "Checking if test database already exists..."
    
    # Try to get database list
    DB_LIST=$(curl -s -X POST "${ODOO_URL}/web/database/list" \
        -H "Content-Type: application/json" \
        -d '{"jsonrpc":"2.0","method":"call","params":{},"id":1}' | \
        grep -o "\"${TEST_DB}\"" || true)
    
    if [ ! -z "$DB_LIST" ]; then
        print_warning "Test database $TEST_DB already exists!"
        read -p "Do you want to drop it and recreate? (y/N): " DROP_EXISTING
        
        if [ "$DROP_EXISTING" = "y" ] || [ "$DROP_EXISTING" = "Y" ]; then
            print_status "Dropping existing test database..."
            curl -X POST "${ODOO_URL}/web/database/drop" \
                -H "Content-Type: application/x-www-form-urlencoded" \
                -d "master_pwd=${MASTER_PASSWORD}&name=${TEST_DB}" \
                --fail --silent --show-error
            
            if [ $? -eq 0 ]; then
                print_success "Existing database dropped"
            else
                print_error "Failed to drop existing database"
                exit 1
            fi
        else
            print_error "Cannot proceed with existing database"
            exit 1
        fi
    fi
}

# Main execution
if [ "$BACKUP_SUCCESS" = true ]; then
    check_existing_db
    
    if restore_database; then
        print_success "Test database created successfully!"
        echo ""
        echo "📋 Summary:"
        echo "   Source Database: $SOURCE_DB"
        echo "   Test Database: $TEST_DB"
        echo "   Backup File: $BACKUP_FILE"
        echo "   Access URL: $ODOO_URL"
        echo ""
        echo "💡 Tips:"
        echo "   - Use the same login credentials as your original database"
        echo "   - The test database is a complete copy of your production data"
        echo "   - Consider anonymizing sensitive data in the test database"
        echo "   - Remember to clean up test databases when no longer needed"
        echo ""
        
        # Ask about cleanup
        read -p "Keep backup file for future use? (Y/n): " KEEP_BACKUP
        if [ "$KEEP_BACKUP" = "n" ] || [ "$KEEP_BACKUP" = "N" ]; then
            rm "$BACKUP_FILE"
            print_status "Backup file deleted"
        else
            print_status "Backup file saved: $BACKUP_FILE"
        fi
        
        # Ask about data anonymization
        echo ""
        read -p "Do you want to run data anonymization on the test database? (y/N): " ANONYMIZE
        if [ "$ANONYMIZE" = "y" ] || [ "$ANONYMIZE" = "Y" ]; then
            print_status "You can use the Python script to anonymize data:"
            echo "python3 create_odoo_test_database.py"
        fi
        
    else
        print_error "Failed to create test database"
        exit 1
    fi
fi

print_success "Script completed!"