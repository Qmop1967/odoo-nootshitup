applyTo: '**'

## Zoho Sync Guidelines

When syncing or importing data from Zoho (e.g., products, customers, vendors):

1. Always assign a **unique identifier** to each master record.
2. Extract the ID from Zoho if available (e.g., `item_code`, `customer_id`).
3. If not available, generate a stable ID using a consistent format.
4. Map the ID to a field in Odoo:
   - Products → `default_code` or `x_zoho_item_code`
   - Customers → `ref` or `x_zoho_customer_id`
   - Vendors → `ref` or `x_zoho_vendor_id`
5. If a record with the same ID exists in Odoo, **update it**, do not create a new one.
6. Ensure data in Odoo mirrors Zoho — uniquely and consistently.

🎯 Purpose: Prevent duplication and keep the sync clean and traceable.

## Coding Standards and Domain Knowledge

Coding standards, domain knowledge, and preferences that AI should follow.

