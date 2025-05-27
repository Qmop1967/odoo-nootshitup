#!/bin/bash

# 🔍 TSH Salesperson App - Error Detection & Issue Reporter
# This script detects common issues and provides actionable solutions

set -e

echo "🔍 TSH Salesperson App - Error Detection & Issue Reporter"
echo "=========================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
ERRORS=0
WARNINGS=0
SUGGESTIONS=0

# Functions
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

log_suggestion() {
    echo -e "${YELLOW}💡 SUGGESTION: $1${NC}"
    ((SUGGESTIONS++))
}

# Check if running in CI
if [ "$CI" = "true" ] || [ "$CODEMAGIC" = "true" ]; then
    echo "🤖 Running in CI/CD environment"
    CI_MODE=true
else
    echo "💻 Running in local development environment"
    CI_MODE=false
fi

echo ""
echo "🔍 Starting comprehensive error detection..."
echo ""

# 1. Environment Checks
echo "📋 1. Environment Validation"
echo "----------------------------"

# Check Flutter installation
if command -v flutter &> /dev/null; then
    FLUTTER_VERSION=$(flutter --version | head -n1 | cut -d' ' -f2)
    log_success "Flutter installed: $FLUTTER_VERSION"
    
    # Check if Flutter version is compatible
    if [[ "$FLUTTER_VERSION" < "3.0.0" ]]; then
        log_warning "Flutter version $FLUTTER_VERSION might be outdated. Consider upgrading to 3.24.5+"
    fi
else
    log_error "Flutter not found in PATH"
fi

# Check Dart installation
if command -v dart &> /dev/null; then
    DART_VERSION=$(dart --version | cut -d' ' -f4)
    log_success "Dart installed: $DART_VERSION"
else
    log_error "Dart not found in PATH"
fi

# Check Android SDK
if [ -n "$ANDROID_HOME" ] || [ -n "$ANDROID_SDK_ROOT" ]; then
    log_success "Android SDK configured"
else
    log_warning "Android SDK environment variables not set"
fi

# Check iOS development tools (macOS only)
if [[ "$OSTYPE" == "darwin"* ]]; then
    if command -v xcodebuild &> /dev/null; then
        XCODE_VERSION=$(xcodebuild -version | head -n1 | cut -d' ' -f2)
        log_success "Xcode installed: $XCODE_VERSION"
    else
        log_warning "Xcode not found (required for iOS development)"
    fi
fi

echo ""

# 2. Project Structure Validation
echo "📁 2. Project Structure Validation"
echo "-----------------------------------"

# Check essential files
REQUIRED_FILES=(
    "pubspec.yaml"
    "lib/main.dart"
    "android/app/build.gradle"
    "android/gradle.properties"
    "ios/Runner.xcodeproj/project.pbxproj"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        log_success "Found: $file"
    else
        log_error "Missing: $file"
    fi
done

# Check Android signing
if [ -f "android/key.properties" ]; then
    log_success "Android signing configuration found"
else
    log_warning "Android signing configuration missing (android/key.properties)"
    log_suggestion "Create android/key.properties for release builds"
fi

if [ -f "android/app/tsh-salesperson-key.jks" ] || [ -f "tsh-salesperson-key.jks" ]; then
    log_success "Android keystore found"
else
    log_warning "Android keystore not found"
fi

echo ""

# 3. Dependencies Analysis
echo "📦 3. Dependencies Analysis"
echo "---------------------------"

if [ -f "pubspec.yaml" ]; then
    # Check for outdated dependencies
    log_info "Checking for outdated dependencies..."
    flutter pub outdated --json > outdated_deps.json 2>/dev/null || true
    
    if [ -f "outdated_deps.json" ]; then
        OUTDATED_COUNT=$(cat outdated_deps.json | grep -o '"current"' | wc -l)
        if [ "$OUTDATED_COUNT" -gt 0 ]; then
            log_warning "$OUTDATED_COUNT dependencies have newer versions available"
            log_suggestion "Run 'flutter pub outdated' to see details"
        else
            log_success "All dependencies are up to date"
        fi
        rm -f outdated_deps.json
    fi
    
    # Check for security vulnerabilities
    log_info "Checking for security vulnerabilities..."
    flutter pub deps --json > deps.json 2>/dev/null || true
    
    if [ -f "deps.json" ]; then
        # Look for known vulnerable packages (basic check)
        if grep -q "http.*0\." deps.json; then
            log_warning "Old HTTP package version detected - potential security risk"
        fi
        rm -f deps.json
    fi
else
    log_error "pubspec.yaml not found"
fi

echo ""

# 4. Code Quality Analysis
echo "🔍 4. Code Quality Analysis"
echo "---------------------------"

# Run Flutter analyze
log_info "Running Flutter analysis..."
if flutter analyze --fatal-infos --fatal-warnings > analysis_output.txt 2>&1; then
    log_success "Code analysis passed"
else
    log_error "Code analysis failed"
    if [ -f "analysis_output.txt" ]; then
        echo "Analysis errors:"
        cat analysis_output.txt
    fi
fi

# Check code formatting
log_info "Checking code formatting..."
if dart format --set-exit-if-changed . > /dev/null 2>&1; then
    log_success "Code formatting is consistent"
else
    log_warning "Code formatting issues detected"
    log_suggestion "Run 'dart format .' to fix formatting"
fi

# Clean up
rm -f analysis_output.txt

echo ""

# 5. Build Configuration Validation
echo "🔧 5. Build Configuration Validation"
echo "-------------------------------------"

# Check Android configuration
if [ -f "android/app/build.gradle" ]; then
    log_info "Validating Android build configuration..."
    
    # Check compile SDK version
    COMPILE_SDK=$(grep "compileSdk" android/app/build.gradle | grep -o '[0-9]\+' | head -1)
    if [ -n "$COMPILE_SDK" ] && [ "$COMPILE_SDK" -ge 34 ]; then
        log_success "Android compile SDK version: $COMPILE_SDK"
    else
        log_warning "Android compile SDK version might be outdated: $COMPILE_SDK"
    fi
    
    # Check target SDK version
    TARGET_SDK=$(grep "targetSdk" android/app/build.gradle | grep -o '[0-9]\+' | head -1)
    if [ -n "$TARGET_SDK" ] && [ "$TARGET_SDK" -ge 34 ]; then
        log_success "Android target SDK version: $TARGET_SDK"
    else
        log_warning "Android target SDK version might be outdated: $TARGET_SDK"
    fi
    
    # Check minimum SDK version
    MIN_SDK=$(grep "minSdk" android/app/build.gradle | grep -o '[0-9]\+' | head -1)
    if [ -n "$MIN_SDK" ] && [ "$MIN_SDK" -ge 21 ]; then
        log_success "Android minimum SDK version: $MIN_SDK"
    else
        log_warning "Android minimum SDK version might be too low: $MIN_SDK"
    fi
fi

# Check Gradle wrapper version
if [ -f "android/gradle/wrapper/gradle-wrapper.properties" ]; then
    GRADLE_VERSION=$(grep "distributionUrl" android/gradle/wrapper/gradle-wrapper.properties | grep -o '[0-9]\+\.[0-9]\+' | head -1)
    if [ -n "$GRADLE_VERSION" ]; then
        log_success "Gradle version: $GRADLE_VERSION"
        
        # Check if Gradle version is compatible with AGP
        if [[ "$GRADLE_VERSION" < "8.4" ]]; then
            log_warning "Gradle version $GRADLE_VERSION might be incompatible with Android Gradle Plugin 8.3+"
        fi
    fi
fi

echo ""

# 6. Security Checks
echo "🔒 6. Security Validation"
echo "-------------------------"

# Check for hardcoded secrets
log_info "Scanning for potential security issues..."

# Check for API keys in code
if grep -r "api_key\|apikey\|secret\|password" lib/ --include="*.dart" | grep -v "// TODO\|// FIXME" > /dev/null 2>&1; then
    log_warning "Potential hardcoded secrets found in code"
    log_suggestion "Use environment variables or secure storage for sensitive data"
fi

# Check network security config
if [ -f "android/app/src/main/res/xml/network_security_config.xml" ]; then
    log_success "Network security configuration found"
else
    log_warning "Network security configuration missing"
    log_suggestion "Add network_security_config.xml for enhanced security"
fi

# Check for cleartext traffic
if grep -q "usesCleartextTraffic.*true" android/app/src/main/AndroidManifest.xml 2>/dev/null; then
    log_warning "Cleartext traffic is enabled - security risk"
else
    log_success "Cleartext traffic is disabled"
fi

echo ""

# 7. Performance Checks
echo "⚡ 7. Performance Validation"
echo "----------------------------"

# Check app size (if built)
if [ -f "build/app/outputs/flutter-apk/app-release.apk" ]; then
    APK_SIZE=$(du -h "build/app/outputs/flutter-apk/app-release.apk" | cut -f1)
    log_info "Release APK size: $APK_SIZE"
    
    # Convert to MB for comparison
    SIZE_MB=$(du -m "build/app/outputs/flutter-apk/app-release.apk" | cut -f1)
    if [ "$SIZE_MB" -gt 50 ]; then
        log_warning "APK size is large ($APK_SIZE). Consider optimizing."
        log_suggestion "Use 'flutter build apk --split-per-abi' to reduce size"
    else
        log_success "APK size is reasonable: $APK_SIZE"
    fi
fi

# Check for large assets
if [ -d "assets" ]; then
    LARGE_ASSETS=$(find assets -type f -size +1M 2>/dev/null | wc -l)
    if [ "$LARGE_ASSETS" -gt 0 ]; then
        log_warning "$LARGE_ASSETS large assets (>1MB) found"
        log_suggestion "Consider compressing large assets"
    else
        log_success "No large assets detected"
    fi
fi

echo ""

# 8. Test Coverage
echo "🧪 8. Test Coverage Analysis"
echo "----------------------------"

if [ -d "test" ]; then
    TEST_COUNT=$(find test -name "*.dart" | wc -l)
    if [ "$TEST_COUNT" -gt 0 ]; then
        log_success "$TEST_COUNT test files found"
        
        # Run tests if not in CI or if explicitly requested
        if [ "$CI_MODE" = false ] || [ "$RUN_TESTS" = "true" ]; then
            log_info "Running tests..."
            if flutter test --coverage > test_output.txt 2>&1; then
                log_success "All tests passed"
                
                # Check coverage if available
                if [ -f "coverage/lcov.info" ]; then
                    # Basic coverage check (requires lcov)
                    if command -v lcov &> /dev/null; then
                        COVERAGE=$(lcov --summary coverage/lcov.info 2>/dev/null | grep "lines" | grep -o '[0-9]\+\.[0-9]\+%' | head -1)
                        if [ -n "$COVERAGE" ]; then
                            log_info "Test coverage: $COVERAGE"
                        fi
                    fi
                fi
            else
                log_error "Some tests failed"
                if [ -f "test_output.txt" ]; then
                    echo "Test errors:"
                    cat test_output.txt
                fi
            fi
            rm -f test_output.txt
        fi
    else
        log_warning "No test files found"
        log_suggestion "Add unit tests to improve code quality"
    fi
else
    log_warning "Test directory not found"
    log_suggestion "Create test directory and add unit tests"
fi

echo ""

# 9. CI/CD Configuration
echo "🚀 9. CI/CD Configuration"
echo "-------------------------"

if [ -f "codemagic.yaml" ]; then
    log_success "Codemagic configuration found"
    
    # Basic validation of codemagic.yaml
    if grep -q "workflows:" codemagic.yaml; then
        log_success "Workflows defined in codemagic.yaml"
    else
        log_warning "No workflows found in codemagic.yaml"
    fi
    
    if grep -q "publishing:" codemagic.yaml; then
        log_success "Publishing configuration found"
    else
        log_warning "No publishing configuration found"
    fi
else
    log_warning "Codemagic configuration not found"
    log_suggestion "Create codemagic.yaml for automated CI/CD"
fi

# Check for GitHub Actions
if [ -f ".github/workflows/main.yml" ] || [ -d ".github/workflows" ]; then
    log_info "GitHub Actions configuration detected"
fi

echo ""

# 10. Summary Report
echo "📊 10. Summary Report"
echo "====================="

echo ""
echo "🔍 Error Detection Summary:"
echo "  ❌ Errors: $ERRORS"
echo "  ⚠️  Warnings: $WARNINGS"
echo "  💡 Suggestions: $SUGGESTIONS"
echo ""

if [ "$ERRORS" -eq 0 ] && [ "$WARNINGS" -eq 0 ]; then
    echo -e "${GREEN}🎉 Excellent! No critical issues detected.${NC}"
    echo -e "${GREEN}Your app is ready for deployment!${NC}"
    exit 0
elif [ "$ERRORS" -eq 0 ]; then
    echo -e "${YELLOW}✅ Good! No critical errors, but some warnings to address.${NC}"
    echo -e "${YELLOW}Consider fixing warnings before deployment.${NC}"
    exit 0
else
    echo -e "${RED}🚨 Critical issues detected that need immediate attention!${NC}"
    echo -e "${RED}Please fix all errors before proceeding.${NC}"
    exit 1
fi 