# Platform McKinsey, Workspaces & Tagging

## Workspaces
- Project Workspace: many Platform McKinsey services without a Product ID. Good for temporary/internal project work.
- Product Workspace: required for Azure Subscription; tied to a Product ID.
- Azure Sandbox: green data only. Azure Analytics Environment: preferred for yellow or higher.
- Platform McKinsey questions → #platform-mckinsey-help

## Migrate Project → Product Workspace
(Requires a registered Product ID.)
1. Log into the project workspace
2. Settings → Advanced features
3. Product workspace migration status → Start migration
4. Fill in the Migration readiness checklist → Migrate
5. Review Product ID, FinalDocs and members
6. Complete
Guide: KO105426.

## Tagging
Mandatory tags on cloud resources: `product_id`, `used_for` (sbx / non_prod / prod), `product_version`.
CMDB sync of correctly tagged resources: ~24 hours.

## Asset Inventory
MPP → product → Asset Inventory shows resources linked to the Product ID (synced from CMDB).
Missing resources: tagged with a different product_id, missing/incorrect tags, or not yet synced.

## Product IDs
System-generated; no range, prefix or pattern encodes PoC/Sandbox/prod. Identify sandbox via `used_for`, Lifecycle Status, naming, pathway, Platform McK Projects — never by Product ID (e.g., Dynatrace filters).

## Environments
- Pre-Prod: synced weekly
- QA: synced occasionally only. Need a Product ID in QA → raise a request to the PCIS team.
