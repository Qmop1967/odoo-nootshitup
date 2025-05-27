#!/bin/bash

# 🔐 TSH Salesperson App - Keystore Validation Script
# This script validates your keystore configuration for both local and Codemagic builds

echo "🔐 TSH Salesperson App - Keystore Validation"
echo "============================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

log_error() {
    echo -e "${RED}❌ ERROR: $1${NC}"
    ((ERRORS++))
}

log_warning() {
    echo -e "${YELLOW}⚠️  WARNING: $1${NC}"
    ((WARNINGS++))
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

echo ""
echo "🔍 Validating keystore configuration..."
echo ""

# 1. Check if keystore file exists
echo "📁 1. Keystore File Validation"
echo "------------------------------"

if [ -f "tsh-salesperson-key.jks" ]; then
    log_success "Keystore file found: tsh-salesperson-key.jks"
    KEYSTORE_PATH="tsh-salesperson-key.jks"
elif [ -f "android/app/tsh-salesperson-key.jks" ]; then
    log_success "Keystore file found: android/app/tsh-salesperson-key.jks"
    KEYSTORE_PATH="android/app/tsh-salesperson-key.jks"
else
    log_error "Keystore file not found. Expected: tsh-salesperson-key.jks"
    KEYSTORE_PATH=""
fi

echo ""

# 2. Check key.properties file
echo "📋 2. Key Properties Validation"
echo "-------------------------------"

if [ -f "android/key.properties" ]; then
    log_success "key.properties file found"
    
    # Read properties
    STORE_PASSWORD=$(grep "storePassword=" android/key.properties | cut -d'=' -f2)
    KEY_PASSWORD=$(grep "keyPassword=" android/key.properties | cut -d'=' -f2)
    KEY_ALIAS=$(grep "keyAlias=" android/key.properties | cut -d'=' -f2)
    STORE_FILE=$(grep "storeFile=" android/key.properties | cut -d'=' -f2)
    
    echo "   Store Password: $STORE_PASSWORD"
    echo "   Key Password: $KEY_PASSWORD"
    echo "   Key Alias: $KEY_ALIAS"
    echo "   Store File: $STORE_FILE"
    
    # Validate against expected values
    if [ "$STORE_PASSWORD" = "Zcbm.97531tsh" ]; then
        log_success "Store password matches Codemagic configuration"
    else
        log_warning "Store password doesn't match expected value: Zcbm.97531tsh"
    fi
    
    if [ "$KEY_ALIAS" = "my-key-alias" ]; then
        log_success "Key alias matches Codemagic configuration"
    else
        log_warning "Key alias doesn't match expected value: my-key-alias"
    fi
    
else
    log_error "key.properties file not found"
fi

echo ""

# 3. Validate keystore contents (if keystore exists and keytool is available)
echo "🔑 3. Keystore Contents Validation"
echo "----------------------------------"

if [ -n "$KEYSTORE_PATH" ] && command -v keytool &> /dev/null; then
    log_info "Checking keystore contents..."
    
    # List keystore contents
    if keytool -list -keystore "$KEYSTORE_PATH" -storepass "Zcbm.97531tsh" > keystore_info.txt 2>&1; then
        log_success "Keystore can be accessed with configured password"
        
        # Check if the expected alias exists
        if grep -q "my-key-alias" keystore_info.txt; then
            log_success "Key alias 'my-key-alias' found in keystore"
        else
            log_warning "Key alias 'my-key-alias' not found in keystore"
            echo "Available aliases:"
            grep "Alias name:" keystore_info.txt || echo "No aliases found"
        fi
        
        # Show keystore info
        echo ""
        log_info "Keystore information:"
        cat keystore_info.txt
        
    else
        log_error "Cannot access keystore with configured password"
        echo "Error details:"
        cat keystore_info.txt
    fi
    
    rm -f keystore_info.txt
    
elif [ -z "$KEYSTORE_PATH" ]; then
    log_warning "Skipping keystore validation - keystore file not found"
elif ! command -v keytool &> /dev/null; then
    log_warning "Skipping keystore validation - keytool not available"
fi

echo ""

# 4. Check Android build configuration
echo "🔧 4. Android Build Configuration"
echo "---------------------------------"

if [ -f "android/app/build.gradle" ]; then
    log_success "Android build.gradle found"
    
    # Check if Codemagic environment variable support is configured
    if grep -q "CM_KEYSTORE" android/app/build.gradle; then
        log_success "Codemagic environment variable support configured"
    else
        log_warning "Codemagic environment variable support not found in build.gradle"
    fi
    
    # Check if local key.properties support is configured
    if grep -q "keystoreProperties" android/app/build.gradle; then
        log_success "Local key.properties support configured"
    else
        log_warning "Local key.properties support not found in build.gradle"
    fi
    
else
    log_error "Android build.gradle not found"
fi

echo ""

# 5. Codemagic configuration check
echo "🚀 5. Codemagic Configuration"
echo "-----------------------------"

if [ -f "codemagic.yaml" ]; then
    log_success "codemagic.yaml found"
    
    # Check if tsh_keystore is referenced
    if grep -q "tsh_keystore" codemagic.yaml; then
        log_success "tsh_keystore reference found in codemagic.yaml"
    else
        log_warning "tsh_keystore reference not found in codemagic.yaml"
    fi
    
else
    log_warning "codemagic.yaml not found"
fi

echo ""

# 6. Environment simulation
echo "🧪 6. Environment Simulation"
echo "----------------------------"

log_info "Simulating Codemagic environment variables..."

# Simulate Codemagic environment
export CM_KEYSTORE="$KEYSTORE_PATH"
export CM_KEY_ALIAS="my-key-alias"
export CM_KEYSTORE_PASSWORD="Zcbm.97531tsh"
export CM_KEY_PASSWORD="Zcbm.97531tsh"

if [ -n "$CM_KEYSTORE" ]; then
    log_success "CM_KEYSTORE would be set to: $CM_KEYSTORE"
else
    log_warning "CM_KEYSTORE would be empty (keystore file not found)"
fi

log_info "CM_KEY_ALIAS would be set to: $CM_KEY_ALIAS"
log_info "CM_KEYSTORE_PASSWORD would be set to: [HIDDEN]"
log_info "CM_KEY_PASSWORD would be set to: [HIDDEN]"

echo ""

# 7. Summary
echo "📊 7. Validation Summary"
echo "========================"

echo ""
echo "🔍 Validation Results:"
echo "  ❌ Errors: $ERRORS"
echo "  ⚠️  Warnings: $WARNINGS"
echo ""

if [ "$ERRORS" -eq 0 ] && [ "$WARNINGS" -eq 0 ]; then
    echo -e "${GREEN}🎉 Perfect! Your keystore configuration is ready for Codemagic!${NC}"
    echo -e "${GREEN}✅ All validations passed${NC}"
    echo ""
    echo "🚀 Next steps:"
    echo "1. Upload your keystore to Codemagic with reference name 'tsh_keystore'"
    echo "2. Configure the keystore password: Zcbm.97531tsh"
    echo "3. Set the key alias: my-key-alias"
    echo "4. Test with a development build"
elif [ "$ERRORS" -eq 0 ]; then
    echo -e "${YELLOW}✅ Good! No critical errors, but some warnings to address.${NC}"
    echo -e "${YELLOW}Your configuration should work, but consider fixing warnings.${NC}"
else
    echo -e "${RED}🚨 Critical issues detected!${NC}"
    echo -e "${RED}Please fix all errors before proceeding with Codemagic setup.${NC}"
fi

echo ""
echo "📖 For detailed setup instructions, see: CODEMAGIC_ENV_SETUP.md"
echo ""

exit $ERRORS 