# Lifecycle, Sunset & Archive

## Lifecycle statuses mentioned in governance
Ideate → … → Operate/Support → Exit/Sunset → Archived/Offline. (Some compliance indicators only appear once in Operate/Support.)

## Sunset / decommission process
1. Before you start
   - Charge Code active and valid ≥ 2 more months (covers remaining tech cost)
   - PM or TL active
   - Users informed and moved off
2. Set to Exit/Sunset: MPP → product → pencil icon → Product Lifecycle Status = Exit/Sunset → Save/Submit
3. Decommission technical components (non-prod first, then prod):
   - Application/hosting (VMs, cloud resources, containers)
   - Database (back up first, then delete)
   - DNS records, firewall/WAF rules
   - Okta apps and service accounts
   - Monitoring (Splunk, Dynatrace, alerts)
   - GitHub repos (archive rather than delete)
   - Revoke access no longer needed
   Keep vulnerabilities remediated until fully withdrawn from production.
4. Data retention: retiring the tool ≠ deleting data. Back up DBs to storage approved for its classification. SharePoint folders stay in place. Retention rules (Standard on Data Management, FinalDocs) apply, especially for client data — confirm with data management/Legal.
5. Close out: update MPP and CMDB records; move to Archived/Offline once complete.

## Who decommissions assets
MPP Team does not decommission assets. Product team raises a request per asset assigned to its support group (e.g., Windows VM → MCS Wintel).
- Okta app: ServiceNow Change Request → fCAB Security
- On-prem VM/server: ServiceNow Change Request → fCAB Wintel; check with Internal Platform Team (IPT) that no other product shares the VM first
- Cloud accounts: retire via AVM (https://avm.mckinsey.com/)
Change Request help: Change Management team (turnaround can be ~48h with complete inputs).

## Archive blockers
- "Cloud Account Decommissioning" control (PLC-LCK00002): all active cloud accounts must be decommissioned before archiving. Check Asset Inventory; retire via AVM.
- Archive option appears only after CMDB shows assets as decommissioned (sync ~24h). If not reflected after 24h → team responsible for asset decommissioning.
- After remediation, use "Tell us about wrong data!" to get compliance flags refreshed.
- Product history shows who archived it. Restoring an archived product → MPP Team. Reviving later as new scope = new registration.

## Support
#unified_product_catalog (sunset process) · #td-sre-cloudconnect (cloud decommissioning) · #my-product-portal (record updates)
Service account deprovisioning sequence isn't explicitly documented → #security-ama / tech_risk@mckinsey.com.
