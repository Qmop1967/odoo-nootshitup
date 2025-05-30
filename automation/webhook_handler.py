#!/usr/bin/env python3
"""
TSH Salesperson App - CodeMagic Webhook Handler
This script receives webhooks from CodeMagic and triggers automated fixes.
"""

from flask import Flask, request, jsonify
import json
import threading
import os
import sys
from error_handler import CodeMagicErrorHandler

app = Flask(__name__)

@app.route('/webhook/codemagic', methods=['POST'])
def handle_codemagic_webhook():
    """Handle incoming CodeMagic webhooks"""
    try:
        # Verify webhook signature (optional but recommended)
        signature = request.headers.get('X-Codemagic-Signature')
        
        # Parse webhook payload
        payload = request.get_json()
        
        if not payload:
            return jsonify({"error": "No payload received"}), 400
        
        # Extract build information
        build_id = payload.get('buildId')
        status = payload.get('status')
        app_id = payload.get('appId')
        
        print(f"📨 Webhook received: Build {build_id} - Status: {status}")
        
        # Only process failed builds
        if status == 'failed':
            print(f"🚨 Build failed, triggering automated fix...")
            
            # Start error handler in background thread
            thread = threading.Thread(
                target=trigger_automated_fix,
                args=(app_id, build_id)
            )
            thread.daemon = True
            thread.start()
            
            return jsonify({
                "message": "Automated fix triggered",
                "buildId": build_id,
                "status": "processing"
            }), 200
        else:
            print(f"✅ Build status: {status} - No action needed")
            return jsonify({
                "message": "Build status noted",
                "buildId": build_id,
                "status": status
            }), 200
            
    except Exception as e:
        print(f"❌ Error processing webhook: {e}")
        return jsonify({"error": str(e)}), 500

def trigger_automated_fix(app_id: str, build_id: str):
    """Trigger the automated fix process"""
    try:
        # Get credentials from environment
        api_token = os.getenv("CODEMAGIC_API_TOKEN")
        github_token = os.getenv("GITHUB_TOKEN")
        
        if not all([api_token, github_token]):
            print("❌ Missing required environment variables")
            return
        
        # Create error handler and start monitoring
        handler = CodeMagicErrorHandler(api_token, app_id, github_token)
        success = handler.monitor_and_fix(max_attempts=3)
        
        if success:
            print("🎉 Automated fix completed successfully!")
        else:
            print("💥 Automated fix failed - manual intervention required")
            # Here you could send notifications, create issues, etc.
            
    except Exception as e:
        print(f"❌ Error in automated fix: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "TSH CI/CD Automation"}), 200

@app.route('/trigger-fix', methods=['POST'])
def manual_trigger():
    """Manual trigger endpoint for testing"""
    try:
        data = request.get_json()
        app_id = data.get('appId') or os.getenv("CODEMAGIC_APP_ID")
        
        if not app_id:
            return jsonify({"error": "appId required"}), 400
        
        # Start error handler in background thread
        thread = threading.Thread(
            target=trigger_automated_fix,
            args=(app_id, "manual-trigger")
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "message": "Manual fix triggered",
            "appId": app_id
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'false').lower() == 'true'
    
    print(f"🚀 Starting TSH CI/CD Automation Webhook Handler on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug) 