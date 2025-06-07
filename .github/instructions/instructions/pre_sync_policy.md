## 🔒 Mandatory Pre-Sync Instructions

Before **any data synchronization, migration, extraction, or update** process from Zoho to Odoo, the following rules must be strictly followed:

1. **Perform a full analysis and comparison** between the data in Zoho (source) and Odoo (target).
   - This includes record counts, field structure, ID mapping, and key data attributes.

2. The system must always treat **Zoho as the source of truth**.
   - Odoo is the target system that must be updated, modified, enhanced, or cleaned to match Zoho.

3. **No data should be pushed to Odoo** without:
   - A complete diff between both systems.
   - Clear statistics on what will be added, updated, or deleted.
   - Logs or reports generated before actual synchronization.

4. Every sync operation must include:
   - Analysis Phase
   - Difference Detection Phase
   - Review or Dry Run Phase (optional)
   - Execution Phase

5. These instructions apply to all operations involving:
   - Full or partial sync
   - One-time migrations
   - Live or background syncing
   - Automated data pulls

🎯 Objective: Ensure data integrity, avoid duplication or accidental overwrites, and maintain a consistent and trusted source.
