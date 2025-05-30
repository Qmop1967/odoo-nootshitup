#!/usr/bin/env python3
"""
CodeMagic Build Log Fetcher and Analyzer
Automatically fetches build logs and provides feedback analysis
"""

import requests
import json
import os
import sys
from datetime import datetime
import re

class CodeMagicLogAnalyzer:
    def __init__(self, api_token):
        self.api_token = api_token
        self.base_url = "https://api.codemagic.io/builds"
        self.headers = {
            "X-Auth-Token": api_token,
            "Content-Type": "application/json"
        }
    
    def get_latest_builds(self, app_id, limit=5):
        """Fetch latest builds for the app"""
        url = f"{self.base_url}?appId={app_id}&limit={limit}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching builds: {response.status_code}")
            return None
    
    def get_build_logs(self, build_id):
        """Fetch detailed logs for a specific build"""
        url = f"{self.base_url}/{build_id}/logs"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.text
        else:
            print(f"Error fetching logs for build {build_id}: {response.status_code}")
            return None
    
    def analyze_ios_errors(self, logs):
        """Analyze iOS-specific errors in build logs"""
        ios_errors = []
        
        # Common iOS error patterns
        error_patterns = [
            r"No matching profiles found for bundle identifier",
            r"Code signing error",
            r"Provisioning profile.*not found",
            r"Certificate.*not found",
            r"Team ID.*not found",
            r"iOS build failed",
            r"xcodebuild.*failed",
            r"CocoaPods.*error",
            r"Flutter iOS build failed"
        ]
        
        for pattern in error_patterns:
            matches = re.findall(pattern, logs, re.IGNORECASE)
            if matches:
                ios_errors.extend(matches)
        
        return ios_errors
    
    def analyze_android_errors(self, logs):
        """Analyze Android-specific errors in build logs"""
        android_errors = []
        
        # Common Android error patterns
        error_patterns = [
            r"Android build failed",
            r"Gradle.*failed",
            r"Keystore.*not found",
            r"Signing.*failed",
            r"Flutter Android build failed",
            r"AAPT.*error",
            r"Dex.*error"
        ]
        
        for pattern in error_patterns:
            matches = re.findall(pattern, logs, re.IGNORECASE)
            if matches:
                android_errors.extend(matches)
        
        return android_errors
    
    def generate_feedback_report(self, build_data, logs):
        """Generate a comprehensive feedback report"""
        report = {
            "build_info": {
                "id": build_data.get("_id"),
                "number": build_data.get("buildNumber"),
                "status": build_data.get("status"),
                "workflow": build_data.get("workflowName"),
                "branch": build_data.get("branch"),
                "commit": build_data.get("commit"),
                "started_at": build_data.get("startedAt"),
                "finished_at": build_data.get("finishedAt"),
                "duration": build_data.get("duration")
            },
            "analysis": {
                "ios_errors": self.analyze_ios_errors(logs) if logs else [],
                "android_errors": self.analyze_android_errors(logs) if logs else [],
                "success": build_data.get("status") == "finished"
            },
            "recommendations": []
        }
        
        # Add recommendations based on errors
        if report["analysis"]["ios_errors"]:
            report["recommendations"].append("Check iOS code signing configuration")
            report["recommendations"].append("Verify Apple Developer account settings")
            report["recommendations"].append("Review provisioning profiles")
        
        if report["analysis"]["android_errors"]:
            report["recommendations"].append("Check Android keystore configuration")
            report["recommendations"].append("Verify Gradle build settings")
        
        if not report["analysis"]["ios_errors"] and not report["analysis"]["android_errors"] and not report["analysis"]["success"]:
            report["recommendations"].append("Check general build configuration")
            report["recommendations"].append("Review Flutter dependencies")
        
        return report
    
    def save_report(self, report, filename=None):
        """Save the feedback report to a file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"build_feedback_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Report saved to: {filename}")
        return filename
    
    def print_summary(self, report):
        """Print a human-readable summary"""
        build_info = report["build_info"]
        analysis = report["analysis"]
        
        print("\n" + "="*60)
        print("🔍 BUILD ANALYSIS SUMMARY")
        print("="*60)
        print(f"📱 Build #{build_info['number']} - {build_info['status'].upper()}")
        print(f"🔧 Workflow: {build_info['workflow']}")
        print(f"🌿 Branch: {build_info['branch']}")
        print(f"⏱️  Duration: {build_info['duration']}s")
        
        if analysis["success"]:
            print("✅ BUILD SUCCESSFUL!")
        else:
            print("❌ BUILD FAILED")
            
            if analysis["ios_errors"]:
                print(f"\n🍎 iOS Errors ({len(analysis['ios_errors'])}):")
                for error in analysis["ios_errors"][:3]:  # Show first 3
                    print(f"   • {error}")
            
            if analysis["android_errors"]:
                print(f"\n🤖 Android Errors ({len(analysis['android_errors'])}):")
                for error in analysis["android_errors"][:3]:  # Show first 3
                    print(f"   • {error}")
        
        if report["recommendations"]:
            print(f"\n💡 Recommendations:")
            for rec in report["recommendations"]:
                print(f"   • {rec}")
        
        print("="*60)

def main():
    # Configuration
    API_TOKEN = os.getenv("CODEMAGIC_API_TOKEN")
    APP_ID = os.getenv("CODEMAGIC_APP_ID", "6835ef689ead500d866e20f7")  # Your app ID
    
    if not API_TOKEN:
        print("❌ Error: CODEMAGIC_API_TOKEN environment variable not set")
        print("Get your API token from: https://codemagic.io/teams/personal-account/integrations")
        sys.exit(1)
    
    analyzer = CodeMagicLogAnalyzer(API_TOKEN)
    
    # Fetch latest builds
    print("🔍 Fetching latest builds...")
    builds = analyzer.get_latest_builds(APP_ID)
    
    if not builds or not builds.get("builds"):
        print("❌ No builds found")
        sys.exit(1)
    
    # Analyze the latest build
    latest_build = builds["builds"][0]
    build_id = latest_build["_id"]
    
    print(f"📋 Analyzing build #{latest_build['buildNumber']} ({build_id})")
    
    # Fetch logs
    logs = analyzer.get_build_logs(build_id)
    
    # Generate report
    report = analyzer.generate_feedback_report(latest_build, logs)
    
    # Print summary
    analyzer.print_summary(report)
    
    # Save detailed report
    filename = analyzer.save_report(report)
    
    print(f"\n📄 Detailed report saved to: {filename}")
    print(f"🔗 Build URL: https://codemagic.io/app/{APP_ID}/build/{build_id}")

if __name__ == "__main__":
    main()