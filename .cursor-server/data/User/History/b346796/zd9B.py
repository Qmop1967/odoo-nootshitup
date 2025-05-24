#!/usr/bin/env python3

from continuous_sync_server_enhanced import EnhancedContinuousSyncServer
import logging

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create sync server instance
sync_server = EnhancedContinuousSyncServer()

# Run one-time complete sync
print('🚀 Running one-time sync to get your new Zoho product...')
success = sync_server.sync_complete_exact_copy()

if success:
    print('✅ Sync completed successfully! Your new product should now be in Odoo.')
else:
    print('❌ Sync failed. Please check the logs.') 