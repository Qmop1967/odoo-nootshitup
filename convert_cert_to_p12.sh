#!/bin/bash

# iOS Certificate to P12 Conversion Script
# This script converts an iOS distribution certificate to P12 format for CodeMagic

echo "=== iOS Certificate to P12 Conversion ==="
echo ""

# Check if certificate file is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <certificate_file.cer>"
    echo ""
    echo "Example: $0 ios_distribution.cer"
    echo ""
    echo "Please provide the path to your downloaded .cer certificate file"
    exit 1
fi

CERT_FILE="$1"
PRIVATE_KEY="ios_distribution_private_key.pem"
OUTPUT_P12="ios_distribution.p12"

# Check if files exist
if [ ! -f "$CERT_FILE" ]; then
    echo "Error: Certificate file '$CERT_FILE' not found!"
    echo "Please make sure you've downloaded the certificate from Apple Developer Portal"
    exit 1
fi

if [ ! -f "$PRIVATE_KEY" ]; then
    echo "Error: Private key file '$PRIVATE_KEY' not found!"
    echo "Please make sure the private key file exists in the current directory"
    exit 1
fi

echo "Converting certificate to P12 format..."
echo "Certificate file: $CERT_FILE"
echo "Private key file: $PRIVATE_KEY"
echo "Output P12 file: $OUTPUT_P12"
echo ""

# Convert certificate to PEM format first
echo "Step 1: Converting certificate to PEM format..."
openssl x509 -inform DER -in "$CERT_FILE" -out ios_distribution_cert.pem

if [ $? -ne 0 ]; then
    echo "Error: Failed to convert certificate to PEM format"
    exit 1
fi

# Create P12 file
echo "Step 2: Creating P12 file..."
echo "You will be prompted to enter a password for the P12 file."
echo "Remember this password - you'll need it in CodeMagic!"
echo ""

openssl pkcs12 -export -out "$OUTPUT_P12" -inkey "$PRIVATE_KEY" -in ios_distribution_cert.pem

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SUCCESS! P12 file created: $OUTPUT_P12"
    echo ""
    echo "Next steps:"
    echo "1. Upload $OUTPUT_P12 to CodeMagic"
    echo "2. Use the password you just set when configuring CodeMagic"
    echo "3. Clean up temporary files if needed:"
    echo "   rm ios_distribution_cert.pem"
    echo ""
else
    echo "❌ Error: Failed to create P12 file"
    exit 1
fi