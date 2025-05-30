#!/usr/bin/env python3
"""
CodeMagic Webhook Receiver
Receives build notifications and automatically analyzes results
"""

from flask import Flask, request, jsonify
import json
import os
import logging
from datetime import datetime
import requests

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BuildAnalyzer:
    def __init__(self):
        self.webhook_token = os.getenv("WEBHOOK_TOKEN", "your-secret-token")
    
    def verify_webhook(self, request):
        """Verify webhook authenticity"""
        auth_header = request.headers.get("Authorization", "")
        expected_token = f"Bearer {self.webhook_token}"
        return auth_header == expected_token
    
    def analyze_build_result(self, payload):
        """Analyze the build result and provide feedback"""
        analysis = {
            "build_id": payload.get("build_id"),
            "status": payload.get("status"),
            "workflow": payload.get("workflow"),
            "duration": payload.get("duration"),
            "issues": [],
            "recommendations": [],
            "success": payload.get("status") == "finished"
        }
        
        # Analyze based on status
        if payload.get("status") == "failed":
            analysis["issues"].append("Build failed")
            
            # Check for common issues based on workflow
            if "ios" in payload.get("workflow", "").lower():
                analysis["recommendations"].extend([
                    "Check iOS code signing configuration",
                    "Verify Apple Developer account credentials",
                    "Review provisioning profiles"
                ])
            
            if "android" in payload.get("workflow", "").lower():
                analysis["recommendations"].extend([
                    "Check Android keystore configuration",
                    "Verify Google Play credentials"
                ])
        
        return analysis
    
    def send_notification(self, analysis, payload):
        """Send notification to relevant channels"""
        # You can integrate with Slack, Discord, Teams, etc.
        message = self.format_notification_message(analysis, payload)
        logger.info(f"Build notification: {message}")
        
        # Example: Send to Slack (uncomment and configure)
        # self.send_to_slack(message)
        
        return message
    
    def format_notification_message(self, analysis, payload):
        """Format a human-readable notification message"""
        status_emoji = "✅" if analysis["success"] else "❌"
        
        message = f"""
{status_emoji} **Build #{payload.get('build_number')} - {analysis['status'].upper()}**

📱 **App**: {payload.get('app_name')}
🔧 **Workflow**: {analysis['workflow']}
🌿 **Branch**: {payload.get('branch')}
⏱️ **Duration**: {analysis['duration']}s
🔗 **Build URL**: {payload.get('build_url')}

"""
        
        if analysis["issues"]:
            message += "❌ **Issues Found**:\n"
            for issue in analysis["issues"]:
                message += f"   • {issue}\n"
        
        if analysis["recommendations"]:
            message += "\n💡 **Recommendations**:\n"
            for rec in analysis["recommendations"]:
                message += f"   • {rec}\n"
        
        if analysis["success"]:
            message += "🎉 **Artifacts Available**:\n"
            message += f"   • Download: {payload.get('artifacts_url')}\n"
        
        return message
    
    def send_to_slack(self, message):
        """Send notification to Slack (example)"""
        slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        if not slack_webhook_url:
            return
        
        payload = {
            "text": message,
            "username": "CodeMagic Bot",
            "icon_emoji": ":robot_face:"
        }
        
        try:
            response = requests.post(slack_webhook_url, json=payload)
            response.raise_for_status()
            logger.info("Slack notification sent successfully")
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")

analyzer = BuildAnalyzer()

@app.route('/webhook/codemagic', methods=['POST'])
def handle_codemagic_webhook():
    """Handle incoming CodeMagic webhook"""
    try:
        # Verify webhook authenticity
        if not analyzer.verify_webhook(request):
            logger.warning("Unauthorized webhook request")
            return jsonify({"error": "Unauthorized"}), 401
        
        # Parse payload
        payload = request.get_json()
        if not payload:
            return jsonify({"error": "Invalid payload"}), 400
        
        logger.info(f"Received webhook for build {payload.get('build_id')}")
        
        # Analyze build result
        analysis = analyzer.analyze_build_result(payload)
        
        # Send notifications
        message = analyzer.send_notification(analysis, payload)
        
        # Save to file for record keeping
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"webhook_logs/build_{payload.get('build_number')}_{timestamp}.json"
        
        os.makedirs("webhook_logs", exist_ok=True)
        with open(filename, 'w') as f:
            json.dump({
                "payload": payload,
                "analysis": analysis,
                "timestamp": timestamp
            }, f, indent=2)
        
        return jsonify({
            "status": "success",
            "message": "Webhook processed successfully",
            "analysis": analysis
        })
    
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/recent-builds', methods=['GET'])
def get_recent_builds():
    """Get recent build analyses"""
    try:
        log_files = []
        if os.path.exists("webhook_logs"):
            for filename in sorted(os.listdir("webhook_logs"), reverse=True)[:10]:
                if filename.endswith('.json'):
                    with open(f"webhook_logs/{filename}", 'r') as f:
                        data = json.load(f)
                        log_files.append({
                            "filename": filename,
                            "build_number": data.get("payload", {}).get("build_number"),
                            "status": data.get("analysis", {}).get("status"),
                            "timestamp": data.get("timestamp")
                        })
        
        return jsonify({"recent_builds": log_files})
    
    except Exception as e:
        logger.error(f"Error fetching recent builds: {e}")
        return jsonify({"error": "Failed to fetch recent builds"}), 500

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)