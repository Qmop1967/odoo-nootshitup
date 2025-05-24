#!/usr/bin/env python3

import os
import sys
import signal
import time
from continuous_sync_server import ContinuousSyncServer

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("🛑 Received shutdown signal - stopping sync server...")
    global sync_server
    if sync_server:
        sync_server.stop_sync_server()
    sys.exit(0)

def main():
    """Start sync server automatically"""
    print("🚀 STARTING ZOHO-ODOO CONTINUOUS SYNC SERVER")
    print("=" * 60)
    
    # Default settings
    sync_interval = int(os.environ.get('SYNC_INTERVAL', 300))  # 5 minutes default
    
    print(f"⚙️  Configuration:")
    print(f"   Sync Interval: {sync_interval} seconds ({sync_interval//60} minutes)")
    print(f"   Log File: /opt/odoo/migration/logs/sync_server.log")
    print(f"   Data Dir: /opt/odoo/migration/data/sync_server/")
    print("=" * 60)
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Create sync server
        global sync_server
        sync_server = ContinuousSyncServer()
        
        # Start the server
        sync_server.start_sync_server(sync_interval)
        
        print(f"✅ Sync server started successfully!")
        print(f"🔄 Monitoring Zoho → Odoo sync every {sync_interval} seconds")
        print(f"📊 Monitor status with: python3 sync_monitor.py")
        print(f"🛑 Stop server with: Ctrl+C or kill signal")
        print("=" * 60)
        
        # Keep the main thread alive
        while sync_server.running:
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n🛑 Keyboard interrupt received")
        signal_handler(signal.SIGINT, None)
        
    except Exception as e:
        print(f"❌ Error starting sync server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    sync_server = None
    main() 